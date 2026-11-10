import sys
import asyncio
import httpx
import qasync
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QVBoxLayout, QSizePolicy
from qasync import asyncSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QListWidgetItem

API_URL = "https://backendbookstore-blei.onrender.com"


class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("_internal/mainwindow.ui", self)
        self.access_token = None
        self.current_user = None
        self.current_book = None
        self.loginSubmitButton.clicked.connect(
            self.login
        )
        self.sendCommentButton.clicked.connect(
            self.send_comment
        )
        self.loginButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(
                self.loginPage
            )
        )

        self.registerSubmitButton.clicked.connect(
            self.register_user
        )

        self.registerButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(
                self.registrationPage
            )
        )

        # Переход между входом и регистрацией
        self.goToRegistrationButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(
                self.registrationPage
            )
        )

        self.goToLoginButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(
                self.loginPage
            )
        )

        # Возвращение в каталог
        self.loginBackButton.clicked.connect(
            self.show_catalog
        )

        self.registerBackButton.clicked.connect(
            self.show_catalog
        )
        self.stackedWidget.setCurrentWidget(self.catalogPage)
        self.backButton.clicked.connect(
            self.show_catalog
        )
        # css стили:----
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
        # --------------
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
        card = ClickableFrame()
        card.setObjectName("bookCard")

        card.clicked.connect(
            lambda book=book: self.show_book_page(book)
        )

        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        # Вертикальная компоновка содержимого карточки.
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        cover = QLabel()
        cover.setObjectName("bookCover")
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setFixedSize(180, 240)
        cover_path = book.get("cover_path")
        pixmap = QPixmap(str(cover_path))
        cover.setPixmap(pixmap.scaled(
            cover.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        title = QLabel(
            str(book.get("title") or "Без названия")
        )
        title.setObjectName("bookTitle")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author = QLabel(
            str(book.get("author") or "Автор неизвестен")
        )
        author.setObjectName("bookAuthor")
        author.setWordWrap(True)
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        year = QLabel(
            str(book.get("year") or "Год неизвестен")
        )
        year.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )

        title.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )

        author.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )

        year.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )
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

        while self.booksGridLayout.columnCount() > 0:
            self.booksGridLayout.setColumnStretch(
                self.booksGridLayout.columnCount() - 1,
                0,
            )
            break

    @asyncSlot()
    async def register_user(self):
        name = self.registerNameInput.text().strip()
        email = self.registerEmailInput.text().strip()
        password = self.registerPasswordInput.text()

        # Проверяем заполнение полей
        if not name or not email or not password:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Заполни все поля."
            )
            return

        self.registerSubmitButton.setEnabled(False)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{API_URL}/auth/register",
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                    },
                )

            if response.is_success:
                QMessageBox.information(
                    self,
                    "Успех",
                    "Аккаунт успешно создан! Теперь можешь войти."
                )

                self.registerNameInput.clear()
                self.registerEmailInput.clear()
                self.registerPasswordInput.clear()

                self.stackedWidget.setCurrentWidget(
                    self.loginPage
                )

            else:
                try:
                    detail = response.json().get(
                        "detail",
                        "Не удалось зарегистрироваться."
                    )
                except ValueError:
                    detail = "Не удалось зарегистрироваться."

                QMessageBox.warning(
                    self,
                    "Ошибка регистрации",
                    str(detail)
                )

        except httpx.HTTPError as error:
            QMessageBox.critical(
                self,
                "Ошибка соединения",
                f"Не удалось связаться с сервером:\n{error}"
            )

        finally:
            self.registerSubmitButton.setEnabled(True)

    def show_catalog(self):
        self.stackedWidget.setCurrentWidget(
            self.catalogPage
        )

    @asyncSlot()
    async def login(self):
        # Получаем данные из полей ввода
        email = self.loginEmailInput.text().strip()
        password = self.loginPasswordInput.text()

        # Проверяем, что поля заполнены
        if not email or not password:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Заполни email и пароль."
            )
            return

        try:
            # Отправляем данные на FastAPI
            async with httpx.AsyncClient(
                    timeout=30.0
            ) as client:

                response = await client.post(
                    f"{API_URL}/auth/login",
                    json={
                        "email": email,
                        "password": password,
                    },
                )

            # Обрабатываем ошибку авторизации
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get(
                        "detail",
                        "Не удалось войти."
                    )
                except ValueError:
                    error_message = "Не удалось войти."

                QMessageBox.warning(
                    self,
                    "Ошибка входа",
                    str(error_message),
                )
                return

            # Получаем JWT-токен из ответа сервера
            data = response.json()
            token = data.get("access_token")

            if not token:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Сервер не вернул токен авторизации."
                )
                return

            # Сохраняем данные текущей сессии
            self.access_token = token
            self.current_user = {
                "email": email,
            }

            # Возвращаемся в каталог
            self.show_catalog()

            self.statusLabel.setText(
                f"Вы вошли как {email}"
            )

            QMessageBox.information(
                self,
                "Успешный вход",
                f"Добро пожаловать!\n{email}",
            )

        except httpx.RequestError:
            QMessageBox.critical(
                self,
                "Ошибка соединения",
                "Не удалось подключиться к серверу.\n"
                "Проверь интернет-соединение и попробуй снова."
            )

        except (ValueError, TypeError):
            QMessageBox.critical(
                self,
                "Ошибка",
                "Сервер вернул некорректный ответ."
            )

    def show_book_page(self, book):
        self.current_book = book
        self.bookTitleLabel.setText(
            book.get("title", "Без названия")
        )
        self.authorLabel.setText(
            f"Автор: {book.get('author', 'Неизвестен')} "
            f"({book.get('year', '—')})"
        )
        self.genreLabel.setText(
            f"Жанр: {book.get('genre', 'Не указан')}"
        )
        self.summaryLabel.setText(
            book.get("summary") or "Описание отсутствует."
        )
        # Получаем путь к обложке из данных книги
        cover_path = book.get("cover_path")
        pixmap = QPixmap(str(cover_path))
        self.coverLabel.setPixmap(pixmap.scaled(
            self.coverLabel.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

        self.commentsListWidget.clear()
        self.stackedWidget.setCurrentWidget(self.page_2)
        asyncio.create_task(self.load_comments())

    async def load_comments(self):
        if not self.current_book:
            return

        book_id = self.current_book.get("id")

        if book_id is None:
            return

        try:
            async with httpx.AsyncClient(
                    timeout=30.0
            ) as client:

                response = await client.get(
                    f"{API_URL}/books/{book_id}/comments"
                )

                response.raise_for_status()
                comments = response.json()

            if not isinstance(comments, list):
                raise ValueError(
                    "Сервер вернул некорректный список комментариев."
                )

            self.commentsListWidget.clear()

            if not comments:
                self.commentsListWidget.addItem(
                    "Пока нет комментариев. Будь первым!"
                )
                return

            for comment in comments:
                user = comment.get("user") or {}

                name = user.get("name", "Неизвестный автор")
                text = comment.get("text", "")
                created_at = comment.get("created_at", "")

                item_text = f"{name}\n{text}"

                if created_at:
                    item_text += f"\n{created_at}"

                self.commentsListWidget.addItem(
                    QListWidgetItem(item_text)
                )

        except httpx.HTTPError as error:
            self.commentsListWidget.addItem(
                f"Не удалось загрузить комментарии: {error}"
            )

        except (ValueError, TypeError):
            self.commentsListWidget.addItem(
                "Ошибка обработки комментариев."
            )

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

    @asyncSlot()
    async def send_comment(self):
        # Проверяем авторизацию
        if not self.access_token:
            QMessageBox.warning(
                self,
                "Требуется вход",
                "Войди в аккаунт, чтобы оставить комментарий."
            )
            return

        if not self.current_book:
            return

        book_id = self.current_book.get("id")
        text = self.commentInput.toPlainText().strip()

        if not text:
            QMessageBox.warning(
                self,
                "Пустой комментарий",
                "Напиши что-нибудь перед отправкой."
            )
            return

        self.sendCommentButton.setEnabled(False)

        try:
            async with httpx.AsyncClient(
                    timeout=30.0
            ) as client:

                response = await client.post(
                    f"{API_URL}/books/{book_id}/comments",
                    json={"text": text},
                    headers={
                        "Authorization": (
                            f"Bearer {self.access_token}"
                        )
                    },
                )

            if response.status_code not in (200, 201):
                try:
                    detail = response.json().get(
                        "detail",
                        "Не удалось отправить комментарий."
                    )
                except ValueError:
                    detail = "Не удалось отправить комментарий."

                QMessageBox.warning(
                    self,
                    "Ошибка отправки",
                    str(detail)
                )
                return

            # Очищаем поле после успешной отправки
            self.commentInput.clear()

            # Повторно загружаем комментарии с сервера
            await self.load_comments()

            QMessageBox.information(
                self,
                "Готово",
                "Комментарий успешно добавлен!"
            )

        except httpx.RequestError:
            QMessageBox.critical(
                self,
                "Ошибка соединения",
                "Не удалось подключиться к серверу."
            )

        finally:
            self.sendCommentButton.setEnabled(True)


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
