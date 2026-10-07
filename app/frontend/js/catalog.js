const API_URL = "http://127.0.0.1:8000";


async function loadBooks(genre = null) {
    let url = `${API_URL}/books`;

    if (genre) {
        url += `?genre=${genre}`;
    }

    const response = await fetch(url);
    const books = await response.json();

    const booksContainer = document.querySelector("#books-container");
    booksContainer.innerHTML = "";
    books.forEach(book => {
        const bookCard = document.createElement("a");

        bookCard.href = `book.html?id=${book.id}`;
        bookCard.classList.add("book-card");

        bookCard.innerHTML = `
            <img
                src="${book.cover_path}"
                alt="Обложка книги"
                class="book-card__image"
            >

            <div class="book-card__info">

                <h2 class="book-card__title">
                    ${book.title}
                </h2>

                <p class="book-card__author">
                    ${book.author}
                </p>

                <div class="book-card__meta">
                    <span>${book.year}</span>
                    <span>${book.genre}</span>
                </div>

            </div>
        `;

        booksContainer.appendChild(bookCard);
    });
}

const urlParams = new URLSearchParams(window.location.search);
const genre = urlParams.get("genre");

loadBooks(genre);