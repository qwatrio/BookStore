const API_URL = "http://127.0.0.1:8000";
const urlParams = new URLSearchParams(window.location.search);
const bookId = urlParams.get("id");
const commentText = document.querySelector("#comment-text");
const commentSubmit = document.querySelector("#comment-submit");
const commentMessage = document.querySelector("#comment-message");

async function loadBook() {
    const response = await fetch(`${API_URL}/books/${bookId}`);

    const book = await response.json();


    document.querySelector("#book-title").textContent = book.title;

    document.querySelector("#book-author").textContent = book.author;

    document.querySelector("#book-year").textContent = book.year;

    document.querySelector("#book-genre").textContent = book.genre;

    document.querySelector("#book-isbn").textContent = book.isbn;

    document.querySelector("#book-summary").textContent = book.summary;

    document.querySelector("#book-cover").src = book.cover_path;
}

async function loadComments() {
    const response = await fetch(
        `${API_URL}/books/${bookId}/comments`
    );

    const comments = await response.json();

    const commentsContainer =
        document.querySelector("#comments-container");


    comments.forEach(comment => {

        const commentElement = document.createElement("div");

        commentElement.classList.add("comment");

        commentElement.innerHTML = `
            <div class="comment__header">

                <strong>
                    ${comment.user.name}
                </strong>

                <span>
                    ${new Date(comment.created_at).toLocaleDateString("ru-RU")}
                </span>

            </div>

            <p class="comment__text">
                ${comment.text}
            </p>
        `;

        commentsContainer.appendChild(commentElement);
    });
}

function checkAuth() {
    const token = localStorage.getItem("access_token");

    const commentForm = document.querySelector(".comment-form");

    if (!token) {
        commentForm.style.display = "none";
    }
}

commentSubmit.addEventListener("click", async () => {
    const token = localStorage.getItem("access_token");

    const text = commentText.value.trim();

    if (!text) {
        commentMessage.textContent = "Введите комментарий";
        return;
    }

    const response = await fetch(
        `${API_URL}/books/${bookId}/comments`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                text: text
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        commentMessage.textContent = data.detail;
        return;
    }

    commentMessage.textContent = "Комментарий добавлен!";
    commentText.value = "";
});

loadBook();
loadComments();
checkAuth();