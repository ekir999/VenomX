from PyQt6.QtWidgets import QMainWindow, QTabWidget, QTextEdit, QFileDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VenomX")
        self.resize(800, 800)
        self.setup_menu()
        self.python_file_tab_bar()
        self.debug_tab_bar()
        self.tab_counter = 0
        self.tab_file_paths = []

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
        exit_button = QAction("Exit", self)
        exit_button.setShortcut("Esc")
        exit_button.triggered.connect(self.close)
        file_menu.addAction(new_button)
        file_menu.addAction(open_button)
        file_menu.addAction(save_button)
        file_menu.addAction(save_as_button)
        file_menu.addAction(exit_button)

        # edit_menu = menu_bar.addMenu("Edit")
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