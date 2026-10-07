const API_URL = "http://127.0.0.1:8000";


const loginForm = document.querySelector("#login-form");

const loginMessage = document.querySelector("#login-message");


loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();


    const email = document.querySelector("#email").value;

    const password = document.querySelector("#password").value;


    const response = await fetch(`${API_URL}/auth/login`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: email,
            password: password
        })

    });


    const data = await response.json();


    if (!response.ok) {

        loginMessage.textContent = data.detail;

        return;
    }


    localStorage.setItem(
        "access_token",
        data.access_token
    );


    loginMessage.textContent = "Вход выполнен!";

    console.log("JWT:", data.access_token);

});