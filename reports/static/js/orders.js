document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".order-detail").forEach(function (element) {
        element.addEventListener("click", function (event) {
            event.preventDefault();
            let orderId = this.getAttribute("data-order-id");

            fetch(`/report/orders/detail/${orderId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Failed to fetch order details");
                    }
                    return response.json();
                })
                .then(data => {
                    document.getElementById("modal-order-id").textContent = data.order_id;
                    document.getElementById("modal-report-name").textContent = data.report_name;
                    document.getElementById("modal-progress").textContent = data.progress;
                    document.getElementById("modal-status").textContent = data.status;
                    document.getElementById("modal-message").textContent = data.message || "No message";
                    document.getElementById("modal-date-begin").textContent = data.date_begin;
                    document.getElementById("modal-date-end").textContent = data.date_end || "Not finished yet";

                    let parametersTable = document.getElementById("modal-parameters");
                    parametersTable.innerHTML = ""; // Clear old data
                    data.parameters.forEach(param => {
                        let row = `<tr><td>${param.name}</td><td>${param.value}</td></tr>`;
                        parametersTable.innerHTML += row;
                    });

                    let orderModal = new bootstrap.Modal(document.getElementById("orderDetailModal"));
                    orderModal.show();
                })
                .catch(error => {
                    console.error("Error fetching order details:", error);
                    alert("Error fetching order details. Please try again later.");
                });
        });
    });
});
