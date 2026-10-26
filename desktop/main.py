import sys
import asyncio
import httpx
import qasync
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout, QSizePolicy, QDialog, QPushButton
from PyQt6.QtCore import QByteArray
from urllib.parse import urljoin
from qasync import asyncSlot
from pathlib import Path
from PyQt6.QtGui import QPixmap
API_URL = "https://backendbookstore-blei.onrender.com"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "app" / "frontend"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)
        #css стили:----
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F5F0E8;
                color: #30251F;
                font-family: "Segoe UI";
                font-size: 10pt;
            }

            QLabel#titleLabel {
                font-size: 24pt;
                font-weight: bold;
                color: #6C4938;
            }

            QLabel#subtitleLabel {
                color: #77675B;
                font-size: 11pt;
            }

            QLabel#catalogLabel {
                font-size: 18pt;
                font-weight: bold;
            }

            QComboBox {
                background-color: #FFFCF7;
                border: 1px solid #D8C9B9;
                border-radius: 8px;
                padding: 6px;
            }

            QPushButton {
                background-color: #6C4938;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
            }

            QPushButton:hover {
                background-color: #825D49;
            }

            QPushButton:disabled {
                background-color: #B7A597;
            }

            QScrollArea {
                border: 1px solid #D8C9B9;
                border-radius: 8px;
                background-color: #F5F0E8;
            }

            QScrollArea QWidget#booksContainer {
                background-color: #F5F0E8;
            }

            QFrame#bookCard {
                background-color: #FFFCF7;
                border: 1px solid #D8C9B9;
                border-radius: 6px;
            }

            QLabel#bookCover {
                background-color: #E8DCCB;
                border: 1px solid #C6B29D;
                font-size: 42pt;
            }

            QLabel#bookTitle {
                font-size: 11pt;
                font-weight: bold;
                color: #6C4938;
            }

            QLabel#bookAuthor {
                color: #77675B;
                font-size: 9pt;
            }
        """)
        #--------------
        self.booksGridLayout = self.booksContainer.layout()
        self.genreComboBox.clear()
        self.genreComboBox.addItem("Все жанры", None)
        self.genreComboBox.addItem("Психология", "psychology")
        self.genreComboBox.addItem("Классика", "classic")
        self.genreComboBox.addItem("Проза", "prose")
        self.genreComboBox.addItem("Ужасы", "horror")
        self.genreComboBox.addItem("Нон-фикшн", "non_fiction")
        self.refreshButton.clicked.connect(self.load_books)
        self.genreComboBox.currentIndexChanged.connect(
            self.load_books
        )

        self.statusLabel.setText("Готов к загрузке книг")
        self.load_books()

    def create_book_card(self, book):
        card = QFrame()
        card.setObjectName("bookCard")

        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        # Вертикальная компоновка содержимого карточки.
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Временная заглушка вместо обложки.
        cover = QLabel()
        cover.setObjectName("bookCover")
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setFixedSize(180, 240)

        cover_path = book.get("cover_path") or book.get("coverPath")

        if cover_path:
            # Например: images/books/all.jpeg
            image_path = FRONTEND_DIR / cover_path

            if image_path.is_file():
                pixmap = QPixmap(str(image_path))

                if not pixmap.isNull():
                    cover.setPixmap(
                        pixmap.scaled(
                            cover.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                else:
                    cover.setText("Ошибка изображения")
            else:
                cover.setText("Обложка не найдена")
        else:
            cover.setText("Нет обложки")

        # Название книги.
        title = QLabel(
            str(book.get("title") or "Без названия")
        )
        title.setObjectName("bookTitle")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Автор книги.
        author = QLabel(
            str(book.get("author") or "Автор неизвестен")
        )
        author.setObjectName("bookAuthor")
        author.setWordWrap(True)
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Год издания.
        year = QLabel(
            str(book.get("year") or "Год неизвестен")
        )
        year.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем элементы в карточку.
        layout.addWidget(cover)
        layout.addWidget(title)
        layout.addWidget(author)
        layout.addWidget(year)
        card.cover_label = cover
        return card

    def clear_books(self):
        while self.booksGridLayout.count():
            item = self.booksGridLayout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        # Сбрасываем растяжение предыдущей сетки.
        while self.booksGridLayout.columnCount() > 0:
            self.booksGridLayout.setColumnStretch(
                self.booksGridLayout.columnCount() - 1,
                0,
            )
            break

    @asyncSlot()
    async def load_books(self):
        """Асинхронно загружает книги из FastAPI."""

        self.refreshButton.setEnabled(False)
        self.statusLabel.setText("Загружаем книги...")

        self.clear_books()

        try:
            # Получаем выбранный жанр.
            genre = self.genreComboBox.currentData()

            params = {}

            if genre:
                params["genre"] = genre

            # Открываем HTTP-клиент и отправляем GET-запрос.
            async with httpx.AsyncClient(
                    timeout=30.0
            ) as client:

                response = await client.get(
                    f"{API_URL}/books",
                    params=params,
                )

                # Вызывает исключение при HTTP-ошибке.
                response.raise_for_status()

                # Преобразуем JSON-ответ в Python-объект.
                books = response.json()

            if not isinstance(books, list):
                raise ValueError(
                    "API вернул данные не в формате списка книг."
                )

            # Размещаем книги по три в ряд.
            for index, book in enumerate(books):
                card = self.create_book_card(book)

                row = index // 3
                column = index % 3

                self.booksGridLayout.addWidget(
                    card,
                    row,
                    column,
                )

            self.booksGridLayout.setAlignment(
                Qt.AlignmentFlag.AlignTop
            )

            # Показываем результат пользователю.
            self.statusLabel.setText(
                f"Загружено книг: {len(books)}"
            )

            if not books:
                self.statusLabel.setText(
                    "В этом жанре пока нет книг."
                )

        except httpx.HTTPError as error:
            self.statusLabel.setText(
                f"Ошибка HTTP: {error}"
            )

        except (ValueError, TypeError) as error:
            self.statusLabel.setText(
                f"Ошибка обработки ответа: {error}"
            )

        finally:
            self.refreshButton.setEnabled(True)


def main():
    # Создаём приложение Qt.
    app = QApplication(sys.argv)

    # Объединяем цикл событий Qt с asyncio.
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Создаём и показываем главное окно.
    window = MainWindow()
    window.show()

    # Запускаем цикл событий.
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
