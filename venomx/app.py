import sys
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QTextEdit, QFileDialog, QMenu, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VenomX")
        self.resize(800, 800)
        self.tab_counter = 0
        self.tab_file_paths = []
        self.recent_files = []
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
        open_button = QAction("Open", self)
        open_button.setShortcut("Ctrl+O")
        open_button.triggered.connect(self.open_file)
        save_button = QAction("Save", self)
        save_button.triggered.connect(self.save_file)
        save_as_button = QAction("Save As", self)
        save_as_button.setShortcut("Ctrl+S")
        save_as_button.triggered.connect(self.save_as_file)
        print_button = QAction("Print", self)
        print_button.setShortcut("Ctrl+P")
        print_button.triggered.connect(self.print_file)
        self.recent_files_menu = QMenu("Recent Files", self)
        self.update_recent_files_menu()
        exit_button = QAction("Exit", self)
        exit_button.setShortcut("Esc")
        exit_button.triggered.connect(self.close)
        file_menu.addAction(new_button)
        file_menu.addAction(open_button)
        file_menu.addAction(save_button)
        file_menu.addAction(save_as_button)
        file_menu.addAction(print_button)
        file_menu.addMenu(self.recent_files_menu)
        file_menu.addAction(exit_button)

        edit_menu = menu_bar.addMenu("Edit")
        find_button = QAction("Find", self)
        find_button.setShortcut("Ctrl+F")
        find_button.triggered.connect(self.close)
        find_and_replace_button = QAction("Find and Replace", self)
        find_and_replace_button.setShortcut("Ctrl+R")
        find_and_replace_button.triggered.connect(self.close)
        edit_menu.addAction(find_button)
        edit_menu.addAction(find_and_replace_button)
        
        # view_menu = menu_bar.addMenu("View")
        # run_menu = menu_bar.addMenu("Run")
        # tools_menu = menu_bar.addMenu("Tools")
        # help_menu = menu_bar.addMenu("Help")

    def create_new_file_tab(self):
        self.tab_counter += 1
        new_tab = QTextEdit()
        self.file_bar.addTab(new_tab, f"Tab {self.tab_counter}")
        self.tab_file_paths.append(None)

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