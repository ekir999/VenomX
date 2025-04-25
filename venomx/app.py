import sys, re, os
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QTextEdit, QFileDialog, QMenu,
    QLineEdit, QVBoxLayout, QWidget, QDialog, QPushButton, QLabel
)
from PyQt6.QtGui import QKeySequence, QTextCharFormat, QSyntaxHighlighter, QColor, QAction, QShortcut, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

class Highlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighted_terms = []
        self.keywords = [
            "def", "class", "if", "else", "elif", "import", "from", "as",
            "try", "except", "finally", "with", "return", "break", "continue",
            "for", "while", "in", "is", "not", "and", "or", "lambda", "global",
            "nonlocal", "assert", "async", "await"
        ]
        self.builtin_functions = [
            "abs", "all", "any", "ascii", "bin", "bool", "breakpoint", 
            "bytearray", "bytes", "callable", "chr", "classmethod", 
            "compile", "complex", "copyright", "credits", "delattr", 
            "dict", "dir", "divmod", "enumerate", "eval", "exec", 
            "exit", "filter", "float", "format", "frozenset", 
            "getattr", "globals", "hasattr", "hash", "help", "hex", 
            "id", "input", "int", "isinstance", "issubclass", "iter", 
            "len", "license", "list", "locals", "map", "max", 
            "memoryview", "min", "next", "object", "oct", "open", 
            "ord", "pow", "print", "property", "quit", "range", 
            "repr", "reversed", "round", "set", "setattr", "slice", 
            "sorted", "staticmethod", "str", "sum", "super", 
            "tuple", "type", "vars", "zip"
        ]

    def highlightBlock(self, text):
        for function in self.builtin_functions:
            pattern = r'\b' + re.escape(function) + r'\s*\('
            for match in re.finditer(pattern, text):
                length = match.end() - match.start()
                format = QTextCharFormat()
                format.setForeground(QColor("orange"))
                self.setFormat(match.start(), length, format)

        operators_pattern = r'(?<!\w)([+\-*/%&|^=<>!]=?|==|!=|and|or|not)(?!\w)'
        for match in re.finditer(operators_pattern, text):
            length = match.end() - match.start()
            format = QTextCharFormat()
            format.setForeground(QColor("darkgray"))
            self.setFormat(match.start(), length, format)

        annotation_pattern = r'@\w+'
        for match in re.finditer(annotation_pattern, text):
            length = match.end() - match.start()
            format = QTextCharFormat()
            format.setForeground(QColor("lightgray"))
            self.setFormat(match.start(), length, format)

        single_line_comment_pattern = r'#.*'
        multi_line_comment_pattern = r"'''(.*?)'''|\"\"\"(.*?)\"\"\""
        
        for match in re.finditer(single_line_comment_pattern, text):
            length = match.end() - match.start()
            format = QTextCharFormat()
            format.setForeground(QColor("lightgreen"))
            self.setFormat(match.start(), length, format)

        for match in re.finditer(multi_line_comment_pattern, text, flags=re.DOTALL):
            length = match.end() - match.start()
            format = QTextCharFormat()
            format.setForeground(QColor("lightgreen"))
            self.setFormat(match.start(), length, format)

        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                length = match.end() - match.start()
                format = QTextCharFormat()
                format.setForeground(QColor("blue"))
                self.setFormat(match.start(), length, format)

        string_patterns = [
            r"'(.*?)'",
            r'"(.*?)"',
            r"'''(.*?)'''",
            r'"""(.*?)"""'
        ]
        for pattern in string_patterns:
            for match in re.finditer(pattern, text, flags=re.DOTALL):
                length = match.end() - match.start()
                format = QTextCharFormat()
                format.setForeground(QColor("red"))
                self.setFormat(match.start(), length, format)

        for term in self.highlighted_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                length = match.end() - match.start()
                format = QTextCharFormat()
                format.setBackground(QColor("yellow"))
                self.setFormat(match.start(), length, format)

    def highlight_terms(self, terms):
        self.highlighted_terms = terms
        self.rehighlight()

class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()

        self.label_find = QLabel("Enter term to find:")
        self.line_edit_find = QLineEdit(self)
        self.label_replace = QLabel("Enter term to replace with:")
        self.line_edit_replace = QLineEdit(self)
        self.find_button = QPushButton("Find", self)
        self.replace_button = QPushButton("Replace", self)

        self.find_button.clicked.connect(self.find_text)
        self.replace_button.clicked.connect(self.replace_text)

        layout.addWidget(self.label_find)
        layout.addWidget(self.line_edit_find)
        layout.addWidget(self.label_replace)
        layout.addWidget(self.line_edit_replace)
        layout.addWidget(self.find_button)
        layout.addWidget(self.replace_button)
        self.setLayout(layout)

    def find_text(self):
        term = self.line_edit_find.text()
        self.parent().highlight_terms(term)

    def replace_text(self):
        find_term = self.line_edit_find.text()
        replace_term = self.line_edit_replace.text()
        self.parent().replace_text(find_term, replace_term)

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VenomX")
        self.resize(800, 800)
        self.tab_counter = 0
        self.tab_file_paths = []
        self.recent_files = []
        icon_path = os.path.join("assets", "VenomX X Logo.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setup_menu()
        self.python_file_tab_bar()
        self.debug_tab_bar()

    def python_file_tab_bar(self):
        self.file_bar = QTabWidget(self)
        self.file_bar.setGeometry(20, 100, 500, 300)
        self.file_bar.setTabsClosable(True)
        self.file_bar.tabCloseRequested.connect(self.close_file_tab)

    def debug_tab_bar(self):
        debug_bar = QTabWidget(self)
        debug_bar.setGeometry(550, 100, 200, 500)

    def setup_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        new_button = QAction("New", self)
        new_button.setShortcut("Ctrl+N")
        new_button.triggered.connect(self.create_new_file_tab)
        new_icon_path = os.path.join("assets", "New-File.png")
        new_button.setIcon(QIcon(new_icon_path))
        open_button = QAction("Open", self)
        open_button.setShortcut("Ctrl+O")
        open_button.triggered.connect(self.open_file)
        open_icon_path = os.path.join("assets", "Open-File.png")
        open_button.setIcon(QIcon(open_icon_path))
        save_button = QAction("Save", self)
        save_button.triggered.connect(self.save_file)
        save_icon_path = os.path.join("assets", "Save.png")
        save_button.setIcon(QIcon(save_icon_path))
        save_as_button = QAction("Save As", self)
        save_as_button.setShortcut("Ctrl+S")
        save_as_button.triggered.connect(self.save_as_file)
        save_as_icon_path = os.path.join("assets", "Save-As.png")
        save_as_button.setIcon(QIcon(save_as_icon_path))
        print_button = QAction("Print", self)
        print_button.setShortcut("Ctrl+P")
        print_button.triggered.connect(self.print_file)
        print_icon_path = os.path.join("assets", "Print.png")
        print_button.setIcon(QIcon(print_icon_path))
        self.recent_files_menu = QMenu("Recent Files", self)
        recent_files_icon_path = os.path.join("assets", "Recent-Files.png")
        self.recent_files_menu.setIcon(QIcon(recent_files_icon_path))
        self.update_recent_files_menu()
        exit_button = QAction("Exit", self)
        exit_button.setShortcut("Esc")
        exit_button.triggered.connect(self.close)
        exit_icon_path = os.path.join("assets", "Exit.png")
        exit_button.setIcon(QIcon(exit_icon_path))
        file_menu.addAction(new_button)
        file_menu.addAction(open_button)
        file_menu.addAction(save_button)
        file_menu.addAction(save_as_button)
        file_menu.addAction(print_button)
        file_menu.addMenu(self.recent_files_menu)
        file_menu.addAction(exit_button)

        edit_menu = menu_bar.addMenu("Edit")
        undo_button = QAction("Undo", self)
        redo_button = QAction("Redo", self)
        cut_button = QAction("Cut", self)
        copy_button = QAction("Copy", self)
        paste_button = QAction("Paste", self)
        indent_selected_lines_button = QAction("Indent Selected Lines", self)
        dedent_selected_lines_button = QAction("Dedent Selected Lines", self)
        comment_button = QAction("Comment Out", self)
        uncomment_button = QAction("Uncomment Out", self)
        go_to_line_button = QAction("Go To Line", self)
        find_and_replace_button = QAction("Find And Replace", self)
        find_and_replace_button.setShortcut("Ctrl+R")
        find_and_replace_button.triggered.connect(self.open_find_replace_dialog)
        find_and_replace_icon_path = os.path.join("assets", "Find-Replace.png")
        find_and_replace_button.setIcon(QIcon(find_and_replace_icon_path))
        edit_menu.addAction(undo_button)
        edit_menu.addAction(redo_button)
        edit_menu.addAction(find_and_replace_button)

        view_menu = menu_bar.addMenu("View")
        increase_font_size_button = QAction("Increase Font Size", self)
        increase_font_size_button.setShortcut(QKeySequence("Ctrl+Up"))
        increase_font_size_button.triggered.connect(self.increase_font_size)
        increase_font_icon_path = os.path.join("assets", "Increase-Font.png")
        increase_font_size_button.setIcon(QIcon(increase_font_icon_path))
        decrease_font_size_button = QAction("Decrease Font Size", self)
        decrease_font_size_button.setShortcut(QKeySequence("Ctrl+Down"))
        decrease_font_size_button.triggered.connect(self.decrease_font_size)
        decrease_font_icon_path = os.path.join("assets", "Decrease-Font.png")
        decrease_font_size_button.setIcon(QIcon(decrease_font_icon_path))
        view_menu.addAction(increase_font_size_button)
        view_menu.addAction(decrease_font_size_button)

        # run_menu = menu_bar.addMenu("Run")
        # tools_menu = menu_bar.addMenu("Tools")
        # help_menu = menu_bar.addMenu("Help")

    def create_new_file_tab(self):
        self.tab_counter += 1
        new_tab = QTextEdit()
        self.file_bar.addTab(new_tab, f"Tab {self.tab_counter}")
        self.tab_file_paths.append(None)
        highlighter = Highlighter(new_tab.document())
        new_tab.highlighter = highlighter

    def close_file_tab(self, index):
        if index >= 0:
            self.file_bar.removeTab(index)
            self.tab_file_paths.pop(index)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Python File", 
            "", 
            "Python Files (*.py);;All Files (*)"
        )
        if file_name:
            with open(file_name, 'r') as file:
                content = file.read()
                self.create_new_tab_with_content(content, file_name)
                self.add_to_recent_files(file_name)

    def create_new_tab_with_content(self, content, file_name):
        self.tab_counter += 1
        new_tab = QTextEdit()
        new_tab.setPlainText(content)
        self.file_bar.addTab(new_tab, file_name)
        self.tab_file_paths.append(file_name)
        highlighter = Highlighter(new_tab.document())
        new_tab.highlighter = highlighter

    def save_file(self):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            file_path = self.tab_file_paths[current_index]
            if file_path:
                self.save_to_file(file_path)
            else:
                self.save_as_file()

    def save_as_file(self):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            file_name, _ = QFileDialog.getSaveFileName(
                self, 
                "Save File", 
                "", 
                "Python Files (*.py);;All Files (*)"
            )
            if file_name:
                self.save_to_file(file_name)
                self.tab_file_paths[current_index] = file_name

    def save_to_file(self, file_path):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            text_edit = self.file_bar.widget(current_index)
            with open(file_path, 'w') as file:
                file.write(text_edit.toPlainText())
            self.file_bar.setTabText(current_index, file_path.split('/')[-1])

    def print_file(self):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            text_edit = self.file_bar.widget(current_index)
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
                text_edit.print(printer)

    def add_to_recent_files(self, file_path):
        if file_path not in self.recent_files:
            self.recent_files.append(file_path)
            if len(self.recent_files) > 5:
                self.recent_files.pop(0)
            self.update_recent_files_menu()

    def update_recent_files_menu(self):
        self.recent_files_menu.clear()
        for file_path in self.recent_files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_files_menu.addAction(action)

    def open_recent_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            self.create_new_tab_with_content(content, file_path)

    @pyqtSlot()
    def open_find_replace_dialog(self):
        dialog = FindDialog(self)
        dialog.find_button.setText("Find")
        dialog.replace_button.setText("Replace")
        dialog.exec()

    @pyqtSlot(str)
    def highlight_terms(self, text):
        terms = text.split()
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            text_edit = self.file_bar.widget(current_index)
            if hasattr(text_edit, 'highlighter'):
                text_edit.highlighter.highlight_terms(terms)

    @pyqtSlot(str, str)
    def replace_text(self, find_term, replace_term):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            text_edit = self.file_bar.widget(current_index)
            content = text_edit.toPlainText()
            new_content = content.replace(find_term, replace_term)
            text_edit.setPlainText(new_content)

    @pyqtSlot()
    def increase_font_size(self):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            text_edit = self.file_bar.widget(current_index)
            font = text_edit.font()
            font.setPointSize(font.pointSize() + 1)
            text_edit.setFont(font)

    @pyqtSlot()
    def decrease_font_size(self):
        current_index = self.file_bar.currentIndex()
        if current_index >= 0:
            text_edit = self.file_bar.widget(current_index)
            font = text_edit.font()
            font.setPointSize(max(1, font.pointSize() - 1))
            text_edit.setFont(font)