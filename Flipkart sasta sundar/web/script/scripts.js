const orders = [
    { id: 1, orderId: "O1", status: "Under Process" },
    { id: 2, orderId: "O2", status: "Done" },
    { id: 3, orderId: "O3", status: "Under Process" },
    { id: 4, orderId: "O4", status: "InActive" },
    { id: 5, orderId: "O5", status: "Done" },
    { id: 6, orderId: "O6", status: "Under Process" },
    { id: 7, orderId: "O7", status: "InActive" },
];

const stations = {
    "O1": [{ stationId: 1, dispatched: false }, { stationId: 3, dispatched: true }],
    "O2": [{ stationId: 2, dispatched: true }, { stationId: 4, dispatched: true }],
    "O3": [{ stationId: 5, dispatched: false }, { stationId: 6, dispatched: false }],
    "O4": [{ stationId: 7, dispatched: false }, { stationId: 8, dispatched: false }],
    "O5": [{ stationId: 3, dispatched: false }, { stationId: 9, dispatched: false }],
    "O6": [{ stationId: 2, dispatched: false }, { stationId: 4, dispatched: false }],
    "O7": [{ stationId: 2, dispatched: false }, { stationId: 4, dispatched: false }]
};

// Function to render table rows based on data
function renderTable(data) {
    const tableBody = document.getElementById("orderTableBody");
    tableBody.innerHTML = "";  // Clear previous rows

    data.forEach((order) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${order.id}</td>
            <td><a href="details.html?orderId=${order.orderId}">${order.orderId}</a></td>
            <td>${order.status}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Function to apply filters
function applyFilter() {
    const orderIdFilter = document.getElementById("orderIdFilter").value.trim().toLowerCase();
    const statusFilter = document.getElementById("statusFilter").value;

    const filteredData = orders.filter((order) => {
        const matchesOrderId = order.orderId.toLowerCase().includes(orderIdFilter);
        const matchesStatus = statusFilter === "" || order.status === statusFilter;

        return matchesOrderId && matchesStatus;
    });

    renderTable(filteredData);
}

// Function to reset filters and show all data
function resetFilter() {
    document.getElementById("orderIdFilter").value = "";
    document.getElementById("statusFilter").value = "";
    renderTable(orders);
}

// Initial rendering of the order table
if (document.getElementById("orderTableBody")) {
    renderTable(orders);
}

// Function to display station details on details.html
function displayOrderDetails() {
    const params = new URLSearchParams(window.location.search);
    const orderId = params.get("orderId");
    document.getElementById("orderIdDisplay").innerText = orderId;

    const stationData = stations[orderId] || [];
    const tableBody = document.getElementById("stationTableBody");

    tableBody.innerHTML = stationData
        .map(station => `
            <tr>
                <td>${station.stationId}</td>
                <td>${station.dispatched ? "Completed" : "Not Completed"}</td>
            </tr>
        `)
        .join("");
}

// Function to navigate back to the overview page
function goBack() {
    window.location.href = "index.html";
}

// Render the station details if on details.html
if (document.getElementById("stationTableBody")) {
    displayOrderDetails();
}
