const $ = s => document.querySelector(s);

let cases = [];

async function init() {
    const response = await fetch("/api/cases");
    const data = await response.json();

    cases = data.cases;

    const select = $("#scenario");

    cases.forEach((c, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.textContent = c.label;
        select.appendChild(option);
    });

    select.addEventListener("change", () => {
        loadCase(cases[select.value]);
    });

    loadCase(cases[0]);
}


function loadCase(c) {
    $("#customer").textContent = c.customer_id;
    $("#order").textContent = c.order_id;
    $("#issue").value = c.issue;
}


function setLoop(stage) {
    const items = document.querySelectorAll(".loop-item");

    items.forEach((item, index) => {
        item.classList.toggle("active", index === stage);
    });
}


function stateView(s) {
    const dash = "—";

    const inventory = s.inventory_checked
        ? (s.inventory_available ? "Available" : "Out of stock")
        : dash;

    const policy = s.policy
        ? (s.policy.replacement ? "Replacement + Refund" : "Restricted")
        : dash;

    const resolution =
        s.replacement
            ? "Replacement initiated"
            : s.refund
                ? "Refund processed"
                : dash;

    $("#state").innerHTML = `
        <div>
            <small>ORDER STATUS</small>
            <strong>${s.order?.status || dash}</strong>
        </div>

        <div>
            <small>INVENTORY</small>
            <strong>${inventory}</strong>
        </div>

        <div>
            <small>POLICY</small>
            <strong>${policy}</strong>
        </div>

        <div>
            <small>RESOLUTION</small>
            <strong>${resolution}</strong>
        </div>
    `;
}


function eventType(e) {

    if (e.type) {
        return e.type.toUpperCase();
    }

    if (e.action === "verify_resolution") {
        return "VERIFY";
    }

    if (
        e.action === "process_refund" ||
        e.action === "create_replacement"
    ) {
        return "ACT";
    }

    return "OBSERVE";
}


function eventClass(type, status) {

    if (status === "blocked") {
        return "blocked";
    }

    if (type === "ADAPT") {
        return "adapt";
    }

    if (type === "DECIDE") {
        return "decide";
    }

    if (type === "ACT") {
        return "action";
    }

    if (type === "VERIFY") {
        return "verify";
    }

    return "";
}


function addEvent(e) {

    const timeline = $("#timeline");

    if (timeline.querySelector(".empty")) {
        timeline.innerHTML = "";
    }

    const type = eventType(e);

    const action = (e.action || e.type || "agent_event")
        .replaceAll("_", " ")
        .toUpperCase();

    const adaptation = e.adaptation
        ? `<p class="adaptation">↳ ${e.adaptation}</p>`
        : "";

    const resultLabel =
        e.status === "blocked"
            ? "BLOCKED"
            : type === "VERIFY"
                ? "VERIFIED"
                : type;

    const element = document.createElement("div");

    element.className =
        `event ${eventClass(type, e.status)}`;

    element.innerHTML = `
        <div class="event-num">
            ${String(e.step || 0).padStart(2, "0")}
        </div>

        <div class="event-main">

            <div class="event-meta">
                ${type}
            </div>

            <b>${action}</b>

            <p>
                ${e.rationale || "Agent evaluated the current environment state."}
            </p>

            ${adaptation}

        </div>

        <div class="event-result">
            ${resultLabel}
        </div>
    `;

    timeline.appendChild(element);

    timeline.scrollTop = timeline.scrollHeight;
}


function updateLoopFromEvent(e) {

    const type = eventType(e);

    switch (type) {

        case "GOAL":
            setLoop(0);
            break;

        case "OBSERVE":
            setLoop(1);
            break;

        case "DECIDE":
            setLoop(2);
            break;

        case "ACT":
            setLoop(3);
            break;

        case "RESULT":
            setLoop(4);
            break;

        case "ADAPT":
            setLoop(5);
            break;

        case "VERIFY":
            setLoop(6);
            break;

        default:
            break;
    }
}


async function run() {

    const scenario = cases[$("#scenario").value];

    $("#run").disabled = true;

    $("#run").textContent =
        "Agent executing...";

    $("#live").textContent =
        "RUNNING";

    $("#live").className =
        "live-pill running";

    $("#headline").textContent =
        "Pursuing resolution";

    $("#timeline").innerHTML = `
        <div class="empty">
            Agent is investigating the case...
        </div>
    `;

    $("#result")
        .parentElement
        .classList.remove("success");

    stateView({});

    setLoop(0);


    try {

        const response = await fetch(
            "/api/resolve",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    customer_id: scenario.customer_id,
                    order_id: scenario.order_id,
                    issue: $("#issue").value,
                    scenario: "auto"
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Resolution request failed."
            );
        }


        data.trace.forEach((event, index) => {

            setTimeout(() => {

                addEvent(event);

                updateLoopFromEvent(event);

                stateView(data.state);

            }, index * 320);

        });


        const totalDelay =
            data.trace.length * 320 + 300;


        setTimeout(() => {

            const result = $("#result");

            result.parentElement.classList.toggle(
                "success",
                data.success
            );


            if (data.success) {

                result.innerHTML = `
                    <div class="result-icon">✓</div>

                    <h3>
                        Resolution verified
                    </h3>

                    <p>
                        ${data.summary}
                    </p>
                `;

                $("#live").textContent =
                    "VERIFIED";

                $("#live").className =
                    "live-pill done";

                $("#headline").textContent =
                    "Case resolved autonomously";

                setLoop(6);

            } else {

                result.innerHTML = `
                    <div class="result-icon">!</div>

                    <h3>
                        Escalation required
                    </h3>

                    <p>
                        ${data.summary}
                    </p>
                `;

                $("#live").textContent =
                    "ESCALATE";

                $("#live").className =
                    "live-pill";

                $("#headline").textContent =
                    "Human review required";
            }


            $("#run").disabled = false;

            $("#run").innerHTML =
                'Run autonomous resolution <span>→</span>';

        }, totalDelay);


    } catch (error) {

        console.error(error);

        $("#headline").textContent =
            "Execution error";

        $("#live").textContent =
            "ERROR";

        $("#live").className =
            "live-pill";

        $("#run").disabled = false;

        $("#run").innerHTML =
            'Run autonomous resolution <span>→</span>';

        $("#timeline").innerHTML = `
            <div class="empty">
                ${error.message}
            </div>
        `;
    }
}


$("#run").addEventListener(
    "click",
    run
);

init();