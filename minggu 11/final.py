import sys
import time
import random
import string
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt

def generate_random_isbn():
    parts = [
        ''.join(random.choices(string.digits, k=3)),
        ''.join(random.choices(string.digits, k=1)),
        ''.join(random.choices(string.digits, k=5)),
        ''.join(random.choices(string.digits, k=3)),
        ''.join(random.choices(string.digits, k=1))
    ]
    return '-'.join(parts)

def generate_random_words(num_words_min=2, num_words_max=5):
    num_words = random.randint(num_words_min, num_words_max)
    words = []
    for _ in range(num_words):
        word_len = random.randint(3, 10)
        word = ''.join(random.choices(string.ascii_lowercase, k=word_len))
        words.append(word.capitalize())
    return ' '.join(words)

def generate_random_author():
    first_name = generate_random_words(1,1)
    last_name = generate_random_words(1,1)
    return f"{first_name} {last_name}"

class Book:
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author

    def __str__(self):
        return f"ISBN: {self.isbn}, Title: \"{self.title}\", Author: {self.author}"
    
    def matches_term(self, term):
        t = term.lower()
        return (t in self.isbn.lower() or
                t in self.title.lower() or
                t in self.author.lower())

class Node:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, book):
        if not isinstance(book.isbn, str) or not book.isbn.strip():
            raise ValueError("ISBN tidak bisa kosong.")
        if not isinstance(book.title, str) or not book.title.strip():
            raise ValueError("Judul tidak bisa kosong.")
        if not isinstance(book.author, str) or not book.author.strip():
            raise ValueError("Penulis tidak bisa kosong.")

        if self.root is None:
            self.root = Node(book)
            return True
        return self._insert_recursive(self.root, book)

    def _insert_recursive(self, current, book):
        lt = book.title.lower()
        ct = current.book.title.lower()
        if lt == ct:
            raise ValueError(f"Buku dengan judul '{book.title}' sudah ada.")
        if lt < ct:
            if current.left is None:
                current.left = Node(book)
                return True
            return self._insert_recursive(current.left, book)
        else:
            if current.right is None:
                current.right = Node(book)
                return True
            return self._insert_recursive(current.right, book)

    def inorder_traversal(self):
        out = []
        self._inorder_recursive(self.root, out)
        return out

    def _inorder_recursive(self, node, out):
        if not node: return
        self._inorder_recursive(node.left, out)
        out.append(node.book)
        self._inorder_recursive(node.right, out)

    def filter_books(self, term):
        all_books = self.inorder_traversal()
        if not term:
            return all_books
        return [b for b in all_books if b.matches_term(term)]

class LibraryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.bst = BinarySearchTree()
        self.initUI()

    def _add_sample_data(self, num_random_books=0):
        sample = [
            Book("978-0321765723","The Lord of the Rings","J.R.R. Tolkien"),
            Book("978-0743273565","The Great Gatsby","F. Scott Fitzgerald"),
            Book("978-1984801989","Where the Crawdads Sing","Delia Owens"),
            Book("11211045","Algorithm Design Patterns","Ivander Nathanael Tindaon"),
            Book("11231025","Advanced Data Structures","Faiz Alrazi Hidayat"),
            Book("11231041","Computational Thinking","Mochammad Reezqi Pratama"),
            Book("11231042","Modern Database Systems","Mochammad Syachdan Pratama Sanjaya"),
            Book("11231059","Introduction to AI","Muhammad Nazril Ilham"),
            Book("978-3161484100","Effective Java","Joshua Bloch"),
            Book("978-0132350884","Clean Code: A Handbook of Agile Software Craftsmanship","Robert C. Martin"),
            Book("978-0201633610","Design Patterns: Elements of Reusable Object-Oriented Software","Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides"),
            Book("978-0134685991","Deep Learning","Ian Goodfellow, Yoshua Bengio, Aaron Courville"),
            Book("978-1491912445","Python for Data Analysis","Wes McKinney"),
            Book("978-0262033848","Introduction to Algorithms","Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein"),
            Book("978-0135957059","The Pragmatic Programmer","David Thomas, Andrew Hunt")
        ]
        
        t_start_sample_insert = time.perf_counter()
        sample_added_count = 0
        for b in sample:
            try:
                self.bst.insert(b)
                sample_added_count += 1
            except ValueError:
                pass 
        
        if num_random_books > 0:
            print(f"Generating {num_random_books} additional random books...")
            for i in range(num_random_books):
                isbn = generate_random_isbn()
                title = generate_random_words()
                author = generate_random_author()
                book = Book(isbn, title, author)
                try:
                    self.bst.insert(book)
                    sample_added_count +=1
                except ValueError:
                    pass 
        
        t_end_sample_insert = time.perf_counter()
        self.insert_time = t_end_sample_insert - t_start_sample_insert
        print(f"Berhasil menambahkan Buku {sample_added_count} waktu insert: {self.insert_time:.4f}s. (BST Insert: Avg O(log N), Worst O(N) per book)")


    def initUI(self):
        self.setWindowTitle('Sistem Pencarian Buku Perpustakaan (BST)')
        self.setGeometry(100, 100, 800, 600)
        L = QVBoxLayout(self)

        top_controls_group = QGroupBox("Kontrol")
        top_controls_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik untuk mencari...")
        self.search_input.textChanged.connect(self.perform_auto_search)
        top_controls_layout.addWidget(self.search_input)

        self.add_book_btn = QPushButton("Tambah Buku Acak")
        self.add_book_btn.clicked.connect(self.show_add_random_books_dialog)
        top_controls_layout.addWidget(self.add_book_btn)
        
        self.reset_btn = QPushButton("Tampilkan Semua / Reset")
        self.reset_btn.clicked.connect(lambda: self.search_input.clear() if self.search_input.text() else self.perform_auto_search())
        top_controls_layout.addWidget(self.reset_btn)

        top_controls_group.setLayout(top_controls_layout)
        L.addWidget(top_controls_group)
        
        Dg = QGroupBox("Data Buku")
        ld = QVBoxLayout()

        self.status_label = QLabel("")
        ld.addWidget(self.status_label)

        self.complexity_label = QLabel("") 
        ld.addWidget(self.complexity_label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ISBN","Judul","Penulis"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        ld.addWidget(self.table)

        Dg.setLayout(ld)
        L.addWidget(Dg)
        
        self.insert_time = 0 
        self._add_sample_data()
        self.perform_auto_search() 

    def show_add_random_books_dialog(self):
        num_books, ok = QInputDialog.getInt(self, "Tambah Buku Acak", 
                                            "Berapa banyak buku acak yang ingin ditambahkan?", 
                                            1, 1, 20000, 1)
        
        if ok and num_books > 0:
            books_added_count = 0
            
            
            t_start_insert = time.perf_counter()

            for i in range(num_books):
                isbn = generate_random_isbn()
                title = generate_random_words()
                author = generate_random_author()
                
                new_book = Book(isbn, title, author)
                try:
                    self.bst.insert(new_book)
                    books_added_count += 1
                except ValueError as e:
                    
                    pass
            
            t_end_insert = time.perf_counter()
            insert_duration = t_end_insert - t_start_insert
            self.insert_time = insert_duration 
            
            print(f"Waktu untuk menambahkan {books_added_count} dari {num_books} buku acak: {self.insert_time:.4f} detik.")

            if books_added_count > 0:
                QMessageBox.information(self, "Sukses", f"{books_added_count} dari {num_books} buku acak berhasil ditambahkan.\nWaktu: {self.insert_time:.4f} detik.")
                self.perform_auto_search() 
            elif num_books > 0: 
                QMessageBox.information(self, "Info", f"Tidak ada buku baru yang ditambahkan.")


    def perform_auto_search(self):
        term = self.search_input.text().strip()
        t0 = time.perf_counter()
        complexity_text = ""
        if term:
            results = self.bst.filter_books(term)
            title = f'Hasil Pencarian "{term}"'
            complexity_text = "Pencarian (filter_books):" 
        else:
            results = self.bst.inorder_traversal()
            title = "Menampilkan Semua Buku"
            complexity_text = "Tampil Semua (inorder_traversal): O(N)"
        dt = time.perf_counter() - t0
        self.display_results(results, title, dt, complexity_text)
        
        
        current_search_complexity_print = ""
        if term:
            current_search_complexity_print = "Search"
        else:
            current_search_complexity_print = "Show All (inorder O(N))"

        if hasattr(self, 'insert_time'):
            print(
                f"Waktu Search: {dt:.5f}s ({current_search_complexity_print})"
            )
        else:
            print(f"Waktu Search: {dt:.5f}s ({current_search_complexity_print})")


    def display_results(self, books, title, search_time, complexity_info):
        self.status_label.setText(f"{title} (Total: {len(books)})")
        self.table.setRowCount(len(books))
        for i, b in enumerate(books):
            self.table.setItem(i, 0, QTableWidgetItem(b.isbn))
            self.table.setItem(i, 1, QTableWidgetItem(b.title))
            self.table.setItem(i, 2, QTableWidgetItem(b.author))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LibraryApp()
    win.show()
    sys.exit(app.exec_())
