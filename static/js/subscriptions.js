async function loadDashboardData() {
    try {
        const summaryRes = await fetch("/dashboard/summary");
        if (summaryRes.ok) {
            const data = await summaryRes.json();
            const sym = data.currency === 'INR' ? '₹' : '$';
            document.getElementById("monthly-burn").textContent = `${sym}${data.monthly_burn_rate}`;
            document.getElementById("annual-spend").textContent = `${sym}${data.annual_spend}`;
            document.getElementById("active-subs").textContent = data.total_active_subscriptions;
            document.getElementById("upcoming-count").textContent = data.upcoming_renewals_count;
        }

        const upcomingRes = await fetch("/dashboard/upcoming-renewals");
        const tbody = document.getElementById("upcoming-table-body");
        if (upcomingRes.ok) {
            const subs = await upcomingRes.json();
            if (subs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center py-3 text-muted">No upcoming renewals in the next 7 days.</td></tr>`;
                return;
            }
            tbody.innerHTML = subs.map(s => `
                <tr>
                    <td><strong>${s.service_name}</strong></td>
                    <td><span class="badge bg-secondary">${s.category}</span></td>
                    <td>${s.price}</td>
                    <td>${s.next_billing_date}</td>
                    <td>${s.days_until_renewal} days</td>
                    <td><span class="badge badge-${s.urgency_level}">${s.urgency_level.toUpperCase()}</span></td>
                </tr>
            `).join('');
        }
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

async function loadSubscriptionsList() {
    const category = document.getElementById("filter-category").value;
    const status = document.getElementById("filter-status").value;

    let url = "/subscriptions/?";
    if (category) url += `category=${encodeURIComponent(category)}&`;
    if (status) url += `status=${encodeURIComponent(status)}`;

    try {
        const res = await fetch(url);
        const tbody = document.getElementById("subscriptions-table-body");
        if (res.ok) {
            const subs = await res.json();
            if (subs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-3 text-muted">No subscriptions found.</td></tr>`;
                return;
            }
            tbody.innerHTML = subs.map(s => `
                <tr>
                    <td><strong>${s.service_name}</strong></td>
                    <td>${s.price}</td>
                    <td><span class="badge bg-info text-dark">${s.billing_cycle}</span></td>
                    <td><span class="badge bg-secondary">${s.category}</span></td>
                    <td>${s.next_billing_date}</td>
                    <td><span class="badge ${s.status === 'Active' ? 'bg-success' : 'bg-danger'}">${s.status}</span></td>
                    <td><span class="badge badge-${s.urgency_level}">${s.urgency_level.toUpperCase()}</span></td>
                    <td class="text-end">
                        <a href="/subscriptions/edit-page/${s.id}" class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-pencil"></i></a>
                        <button onclick="deleteSubscription(${s.id})" class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (err) {
        console.error("List load error:", err);
    }
}

async function deleteSubscription(id) {
    if (!confirm("Are you sure you want to delete this subscription?")) return;
    try {
        const res = await fetch(`/subscriptions/${id}`, { method: "DELETE" });
        if (res.ok) {
            loadSubscriptionsList();
        }
    } catch (err) {
        alert("Failed to delete.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const addForm = document.getElementById("add-subscription-form");
    const editForm = document.getElementById("edit-subscription-form");

    if (addForm) {
        addForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                service_name: document.getElementById("service_name").value,
                price: parseFloat(document.getElementById("price").value),
                billing_cycle: document.getElementById("billing_cycle").value,
                next_billing_date: document.getElementById("next_billing_date").value,
                category: document.getElementById("category").value,
                status: document.getElementById("status").value,
                auto_renew: document.getElementById("auto_renew").checked
            };

            const res = await fetch("/subscriptions/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                window.location.href = "/subscriptions/manage-page";
            } else {
                alert("Failed to save subscription.");
            }
        });
    }

    if (editForm) {
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const subId = editForm.dataset.id;
            const payload = {
                service_name: document.getElementById("service_name").value,
                price: parseFloat(document.getElementById("price").value),
                billing_cycle: document.getElementById("billing_cycle").value,
                next_billing_date: document.getElementById("next_billing_date").value,
                category: document.getElementById("category").value,
                status: document.getElementById("status").value,
                auto_renew: document.getElementById("auto_renew").checked
            };

            const res = await fetch(`/subscriptions/${subId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                window.location.href = "/subscriptions/manage-page";
            } else {
                alert("Failed to update subscription.");
            }
        });
    }
});