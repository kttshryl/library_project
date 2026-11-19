# main.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта библиотеки")
        self.root.geometry("800x500")

        # Путь к файлу сохранения
        self.data_file = "library_data.json"
        self.load_data()

        title_label = ttk.Label(root, text="Система учёта библиотеки", font=("Arial", 14))
        title_label.pack(pady=20)
        
        action_frame = ttk.Frame(root)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="1. Добавить книгу", width=20, command=self.add_book).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(action_frame, text="2. Выдать книгу", width=20, command=self.issue_book).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(action_frame, text="3. Найти книгу", width=20, command=self.find_book).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(action_frame, text="4. Отметить возврат", width=20, command=self.return_book).grid(row=3, column=0, padx=5, pady=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Название", "Автор", "Читатель", "Дата"), show="headings")
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Читатель", text="Читатель")
        self.tree.heading("Дата", text="Дата выдачи")
        
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Отрисовываем данные при запуске
        self.refresh_tree()

        # Сохраняем данные при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        """Загружает данные из JSON файла, если он есть"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books_data = data.get('books', [])
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, IOError):
                self.books_data = []
                self.next_id = 1
        else:
            self.books_data = []
            self.next_id = 1

    def save_data(self):
        """Сохраняет данные в JSON файл"""
        data = {'books': self.books_data, 'next_id': self.next_id}
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def on_closing(self):
        """Вызывается при нажатии на крестик окна"""
        self.save_data()
        self.root.destroy()

    def refresh_tree(self):
        """Очищает и перерисовывает таблицу"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in self.books_data:
            self.tree.insert("", "end", values=(
                book["id"], 
                book["title"], 
                book["author"], 
                book["reader"] or "", 
                book["date"] or ""
            ))

    def add_book(self):
        title = simpledialog.askstring("Добавление книги", "Введите название книги:")
        if not title or not title.strip():
            return
        
        author = simpledialog.askstring("Добавление книги", "Введите автора книги:")
        if not author or not author.strip():
            return

        self.books_data.append({
            "id": self.next_id,
            "title": title.strip(),
            "author": author.strip(),
            "reader": None,
            "date": None
        })
        self.next_id += 1
        self.refresh_tree()
        self.save_data()
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена.")

    def issue_book(self):
        available_books = [b for b in self.books_data if b["reader"] is None]
        if not available_books:
            messagebox.showwarning("Ошибка", "Нет доступных книг для выдачи.")
            return
        
        book_list_str = "\n".join([f"{b['id']}. {b['title']} ({b['author']})" for b in available_books])
        book_id_str = simpledialog.askstring("Выдача книги", f"Выберите ID книги:\n{book_list_str}")
        if not book_id_str:
            return
        
        try:
            book_id = int(book_id_str)
            book = next((b for b in available_books if b["id"] == book_id), None)
            if not book:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ID.")
            return

        reader = simpledialog.askstring("Выдача книги", f"Введите имя читателя для '{book['title']}':")
        if not reader or not reader.strip():
            return
            
        date = simpledialog.askstring("Выдача книги", "Введите дату выдачи (ДД.ММ.ГГГГ):")
        if not date:
            return

        book["reader"] = reader.strip()
        book["date"] = date.strip()
        self.refresh_tree()
        self.save_data()
        messagebox.showinfo("Успех", f"Книга выдана {reader}.")

    def find_book(self):
        term = simpledialog.askstring("Поиск", "Введите часть названия или автора:")
        if not term:
            return
        
        term = term.lower()
        results = [b for b in self.books_data if term in b["title"].lower() or term in b["author"].lower()]
        
        if not results:
            messagebox.showinfo("Результат", "Ничего не найдено.")
            self.refresh_tree() # Сбрасываем фильтры, если искали и не нашли
        else:
            self.refresh_tree(results)

    def return_book(self):
        issued_books = [b for b in self.books_data if b["reader"] is not None]
        if not issued_books:
            messagebox.showwarning("Ошибка", "Нет выданных книг.")
            return
        
        book_list_str = "\n".join([f"{b['id']}. {b['title']} — у {b['reader']}" for b in issued_books])
        book_id_str = simpledialog.askstring("Возврат", f"Выберите ID возвращаемой книги:\n{book_list_str}")
        if not book_id_str:
            return
        
        try:
            book_id = int(book_id_str)
            book = next((b for b in issued_books if b["id"] == book_id), None)
            if not book:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ID.")
            return

        if messagebox.askyesno("Подтверждение", f"Отметить возврат '{book['title']}' от {book['reader']}?"):
            book["reader"] = None
            book["date"] = None
            self.refresh_tree()
            self.save_data()
            messagebox.showinfo("Успех", "Возврат отмечен.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()