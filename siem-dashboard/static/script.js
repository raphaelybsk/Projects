const eventList = document.getElementById("event-list");
const alertList = document.getElementById("alert-list");
const statusMessage = document.getElementById("status");
const severityFilter = document.getElementById("severity-filter");
const refreshButton = document.getElementById("refresh-button");
const addButton = document.getElementById("add-button");

async function loadDashboard() {
    statusMessage.textContent = "Loading...";
    refreshButton.disabled = true;
    severityFilter.disabled = true;
    addButton.disabled = true;

    try {
        // Ask Python for the events and current alerts.
        const eventResponse = await fetch("/api/events?severity=" + severityFilter.value);
        const alertResponse = await fetch("/api/alerts");
        if (!eventResponse.ok || !alertResponse.ok) {
            throw new Error("The server could not load the dashboard.");
        }
        const events = await eventResponse.json();
        const alerts = await alertResponse.json();

        eventList.replaceChildren();
        for (const event of events) {
            const row = document.createElement("tr");
            const values = [event.timestamp, event.source, event.source_ip,
                event.event_type, event.severity, event.message];

            for (const value of values) {
                const cell = document.createElement("td");
                // Show log contents as text, never as HTML code.
                cell.textContent = value;
                row.appendChild(cell);
            }
            eventList.appendChild(row);
        }
        document.getElementById("event-count").textContent = "Events shown: " + events.length;

        alertList.replaceChildren();
        if (alerts.length === 0) {
            const item = document.createElement("li");
            item.textContent = "No repeated failed logins found.";
            alertList.appendChild(item);
        }
        for (const alert of alerts) {
            const item = document.createElement("li");
            item.textContent = alert.source_ip + ": " + alert.failed_logins + " failed logins.";
            alertList.appendChild(item);
        }
        statusMessage.textContent = "Dashboard updated.";
    } catch (error) {
        statusMessage.textContent = "Could not refresh. Check that python app.py is running. Displayed data may be outdated.";
    } finally {
        refreshButton.disabled = false;
        severityFilter.disabled = false;
        addButton.disabled = false;
    }
}

async function addEvent(event) {
    // Stop the form from reloading the whole page.
    event.preventDefault();
    addButton.disabled = true;
    const newEvent = {
        source: document.getElementById("source").value,
        source_ip: document.getElementById("source-ip").value,
        event_type: document.getElementById("event-type").value,
        severity: document.getElementById("severity").value,
        message: document.getElementById("message").value
    };

    try {
        const response = await fetch("/api/events", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newEvent)
        });
        if (!response.ok) {
            throw new Error("Event rejected. Check the IP address and required fields.");
        }
    } catch (error) {
        statusMessage.textContent = "Event could not be added. Check the server, IP address, and required fields.";
        addButton.disabled = false;
        return;
    }
    await loadDashboard();
}

refreshButton.addEventListener("click", loadDashboard);
severityFilter.addEventListener("change", loadDashboard);
document.getElementById("event-form").addEventListener("submit", addEvent);
loadDashboard();
