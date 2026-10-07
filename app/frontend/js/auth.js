const token = localStorage.getItem("access_token");

const loginLink = document.querySelector("#login-link");
const registerLink = document.querySelector("#register-link");
const logoutLink = document.querySelector("#logout-link");

if (token) {
    loginLink.style.display = "none";
    registerLink.style.display = "none";
} else {
    logoutLink.style.display = "none";
}

logoutLink.addEventListener("click", (event) => {
    event.preventDefault();

    localStorage.removeItem("access_token");

    window.location.reload();
});