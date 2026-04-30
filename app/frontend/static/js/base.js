// Access token stored in memory only (cleared on page reload by design)
let accessToken = null;

// Wrapper for authenticated API calls — handles refresh-on-401 automatically
async function fetchWithAuth(url, options = {}) {
    if (!options.headers) options.headers = {};
    if (accessToken) {
        options.headers["Authorization"] = `Bearer ${accessToken}`;
    }

    let response = await fetch(url, options);

    if (response.status === 401) {
        const refreshResponse = await fetch("/auth/refresh", {
            method: "POST",
        });
        if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            accessToken = data.access_token;
            options.headers["Authorization"] = `Bearer ${accessToken}`;
            response = await fetch(url, options);
        } else {
            window.location.href = "/auth/login-page";
            return response;
        }
    }

    return response;
}

// Add Todo JS
const todoForm = document.getElementById("todoForm");
if (todoForm) {
    todoForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: false,
        };

        try {
            const response = await fetchWithAuth("/todos/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                form.reset(); // Clear the form
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    });
}

// Edit Todo JS
const editTodoForm = document.getElementById("editTodoForm");
if (editTodoForm) {
    editTodoForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        var url = window.location.pathname;
        const todoId = url.substring(url.lastIndexOf("/") + 1);

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: data.complete === "on",
        };

        try {
            const response = await fetchWithAuth(`/todos/update/${todoId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                window.location.href = "/todos/todos-page"; // Redirect to the todo page
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    });

    document
        .getElementById("deleteButton")
        .addEventListener("click", async function () {
            var url = window.location.pathname;
            const todoId = url.substring(url.lastIndexOf("/") + 1);

            try {
                const response = await fetchWithAuth(
                    `/todos/delete/${todoId}`,
                    {
                        method: "DELETE",
                    },
                );

                if (response.ok) {
                    // Handle success
                    window.location.href = "/todos/todos-page"; // Redirect to the todo page
                } else {
                    // Handle error
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail}`);
                }
            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            }
        });
}

// Login JS
const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        const payload = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            payload.append(key, value);
        }

        try {
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: payload.toString(),
            });

            if (response.ok) {
                const data = await response.json();
                accessToken = data.access_token;
                window.location.href = "/todos/todos-page";
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    });
}

// Register JS
const registerForm = document.getElementById("registerForm");
if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.password2) {
            alert("Passwords do not match");
            return;
        }

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.firstname,
            last_name: data.lastname,
            role: data.role,
            phone_number: data.phone_number,
            password: data.password,
        };

        try {
            const response = await fetch("/users/create", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                window.location.href = "/auth/login-page";
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.message}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    });
}

// // Helper function to get a cookie by name
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// };

async function logout() {
    accessToken = null;
    await fetch("/auth/logout", { method: "POST" });
    window.location.href = "/auth/login-page";
}
