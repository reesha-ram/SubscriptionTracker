document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const alertBox = document.getElementById("alert-box");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new URLSearchParams();
            formData.append("username", document.getElementById("username").value);
            formData.append("password", document.getElementById("password").value);

            try {
                const response = await fetch("/auth/token", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    document.cookie = `access_token=${data.access_token}; path=/; max-age=3600; SameSite=Lax`;
                    window.location.href = "/dashboard/";
                } else {
                    showAlert(data.detail || "Login failed");
                }
            } catch (err) {
                showAlert("Server connection error.");
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                username: document.getElementById("username").value,
                email: document.getElementById("email").value,
                password: document.getElementById("password").value,
                currency: document.getElementById("currency").value
            };

            try {
                const response = await fetch("/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = "/auth/login-page?registered=true";
                } else {
                    showAlert(data.detail || "Registration failed");
                }
            } catch (err) {
                showAlert("Server connection error.");
            }
        });
    }

    function showAlert(msg) {
        if (alertBox) {
            alertBox.textContent = msg;
            alertBox.classList.remove("d-none");
        }
    }
});