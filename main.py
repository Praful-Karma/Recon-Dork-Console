import sys
import webbrowser
from urllib.parse import quote

from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QScrollArea
)


def load_dorks_from_file(filepath):

    dorks = []

    try:

        with open(filepath, "r", encoding="utf-8") as file:

            lines = file.readlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            # FULL FORMAT
            if len(parts) == 4:

                dorks.append({
                    "category": parts[0],
                    "name": parts[1],
                    "query": parts[2],
                    "description": parts[3]
                })

            # SHORT FORMAT
            elif len(parts) == 3:

                dorks.append({
                    "category": "General",
                    "name": parts[0],
                    "query": parts[1],
                    "description": parts[2]
                })

            # QUERY ONLY FORMAT
            elif len(parts) == 1:

                dorks.append({
                    "category": "General",
                    "name": "Imported Dork",
                    "query": parts[0],
                    "description": "Imported Query"
                })

    except Exception as e:

        print("Error loading dorks:", e)

    return dorks


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Recon Dork Console")

        self.resize(1450, 850)

        self.setMinimumSize(1000, 600)

        self.all_dorks = []

        self.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                color: #e6edf3;
                font-size: 14px;
                font-family: Consolas;
            }

            QListWidget,
            QTextEdit,
            QLineEdit,
            QComboBox {

                background-color: #161b22;

                border: 1px solid #30363d;

                border-radius: 10px;

                padding: 8px;
            }

            QPushButton {

                background-color: #238636;

                border: none;

                border-radius: 10px;

                padding: 12px;

                font-weight: bold;
            }

            QPushButton:hover {

                background-color: #2ea043;
            }

            QLabel {

                font-weight: bold;
            }

            QListWidget::item {

                padding: 10px;
            }

            QListWidget::item:selected {

                background-color: #238636;
            }

            QScrollArea {

                border: none;
            }
        """)

        # MAIN LAYOUT
        main_layout = QHBoxLayout()

        # LEFT PANEL
        left_layout = QVBoxLayout()

        title = QLabel("Recon Dork Console")

        title.setFont(QFont("Consolas", 20))

        self.target_input = QLineEdit()

        self.target_input.setPlaceholderText(
            "Enter target domain"
        )

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Search dorks..."
        )

        self.category_dropdown = QComboBox()

        self.category_dropdown.addItem("All")

        self.import_button = QPushButton(
            "Import Dork TXT"
        )

        self.help_button = QPushButton(
            "Help / Import Guide"
        )

        self.dork_list = QListWidget()

        left_layout.addWidget(title)

        left_layout.addWidget(QLabel("Target"))

        left_layout.addWidget(self.target_input)

        left_layout.addWidget(QLabel("Search"))

        left_layout.addWidget(self.search_input)

        left_layout.addWidget(QLabel("Category"))

        left_layout.addWidget(self.category_dropdown)

        left_layout.addWidget(self.import_button)

        left_layout.addWidget(self.help_button)

        left_layout.addWidget(QLabel("Available Dorks"))

        left_layout.addWidget(self.dork_list)

        # RIGHT PANEL
        right_layout = QVBoxLayout()

        self.description_box = QTextEdit()

        self.description_box.setReadOnly(True)

        self.payload_editor = QTextEdit()

        # ENGINE BUTTONS
        engine_layout = QHBoxLayout()

        self.google_button = QPushButton(
            "Launch Google"
        )

        self.bing_button = QPushButton(
            "Launch Bing"
        )

        self.github_button = QPushButton(
            "Launch GitHub"
        )

        self.shodan_button = QPushButton(
            "Launch Shodan"
        )

        engine_layout.addWidget(self.google_button)

        engine_layout.addWidget(self.bing_button)

        engine_layout.addWidget(self.github_button)

        engine_layout.addWidget(self.shodan_button)

        right_layout.addWidget(QLabel("Purpose"))

        right_layout.addWidget(self.description_box)

        right_layout.addWidget(QLabel("Editable Payload"))

        right_layout.addWidget(self.payload_editor)

        right_layout.addLayout(engine_layout)

        main_layout.addLayout(left_layout, 2)

        main_layout.addLayout(right_layout, 3)

        # SCROLL AREA
        container = QWidget()

        container.setLayout(main_layout)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setWidget(container)

        outer_layout = QVBoxLayout()

        outer_layout.addWidget(scroll)

        self.setLayout(outer_layout)

        # EVENTS
        self.import_button.clicked.connect(
            self.import_dorks
        )

        self.help_button.clicked.connect(
            self.show_help
        )

        self.search_input.textChanged.connect(
            self.filter_dorks
        )

        self.category_dropdown.currentTextChanged.connect(
            self.filter_dorks
        )

        self.dork_list.currentRowChanged.connect(
            self.load_dork
        )

        self.target_input.textChanged.connect(
            self.update_payload
        )

        self.google_button.clicked.connect(
            lambda: self.launch_search("google")
        )

        self.bing_button.clicked.connect(
            lambda: self.launch_search("bing")
        )

        self.github_button.clicked.connect(
            lambda: self.launch_search("github")
        )

        self.shodan_button.clicked.connect(
            lambda: self.launch_search("shodan")
        )

    def import_dorks(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Dork TXT",
            "",
            "Text Files (*.txt)"
        )

        if not file_path:
            return

        imported_dorks = load_dorks_from_file(
            file_path
        )

        self.all_dorks.extend(imported_dorks)

        # REMOVE DUPLICATES
        unique_dorks = []

        seen_queries = set()

        for dork in self.all_dorks:

            if dork["query"] not in seen_queries:

                unique_dorks.append(dork)

                seen_queries.add(
                    dork["query"]
                )

        self.all_dorks = unique_dorks

        self.load_categories()

        self.filter_dorks()

    def load_categories(self):

        self.category_dropdown.clear()

        self.category_dropdown.addItem("All")

        categories = set()

        for dork in self.all_dorks:

            categories.add(
                dork["category"]
            )

        for category in sorted(categories):

            self.category_dropdown.addItem(
                category
            )

    def filter_dorks(self):

        self.dork_list.clear()

        search_text = (
            self.search_input.text().lower()
        )

        selected_category = (
            self.category_dropdown.currentText()
        )

        for dork in self.all_dorks:

            if selected_category != "All":

                if dork["category"] != selected_category:
                    continue

            if search_text:

                if search_text not in dork["name"].lower():
                    continue

            item = QListWidgetItem(
                f"[{dork['category']}] {dork['name']}"
            )

            self.dork_list.addItem(item)

    def get_visible_dorks(self):

        visible = []

        search_text = (
            self.search_input.text().lower()
        )

        selected_category = (
            self.category_dropdown.currentText()
        )

        for dork in self.all_dorks:

            if selected_category != "All":

                if dork["category"] != selected_category:
                    continue

            if search_text:

                if search_text not in dork["name"].lower():
                    continue

            visible.append(dork)

        return visible

    def load_dork(self):

        selected_index = (
            self.dork_list.currentRow()
        )

        if selected_index < 0:
            return

        visible_dorks = self.get_visible_dorks()

        dork = visible_dorks[selected_index]

        self.description_box.setText(
            dork["description"]
        )

        self.update_payload()

    def update_payload(self):

        selected_index = (
            self.dork_list.currentRow()
        )

        if selected_index < 0:
            return

        visible_dorks = self.get_visible_dorks()

        dork = visible_dorks[selected_index]

        target = (
            self.target_input.text().strip()
        )

        query = dork["query"].replace(
            "{target}",
            target
        )

        self.payload_editor.setText(
            query
        )

    def show_help(self):

        help_text = """
RECON DORK CONSOLE - HELP GUIDE

========================================
SUPPORTED IMPORT FORMATS
========================================

1. FULL FORMAT

CATEGORY|NAME|QUERY|DESCRIPTION

Example:
Sensitive Files|ENV Files|site:{target} ext:env|Find exposed environment configuration files.


========================================
2. SHORT FORMAT
========================================

NAME|QUERY|DESCRIPTION

Example:
ENV Files|site:{target} ext:env|Find exposed environment configuration files.

Category automatically becomes:
General


========================================
3. QUERY ONLY FORMAT
========================================

site:{target} ext:env

Automatically generated:
- Category: General
- Name: Imported Dork
- Description: Imported Query


========================================
TARGET PLACEHOLDER
========================================

Use:
{target}

Example:
site:{target} ext:sql

If target entered:
example.com

Generated query:
site:example.com ext:sql


========================================
SUPPORTED SEARCH ENGINES
========================================

- Google
- Bing
- GitHub
- Shodan


========================================
NOTES
========================================

- One dork per line
- Empty lines ignored
- UTF-8 encoding recommended
- Duplicate queries removed automatically
"""

        msg = QMessageBox(self)

        msg.setWindowTitle(
            "Recon Dork Console Help"
        )

        msg.setText(help_text)

        msg.exec()

    def launch_search(self, engine):

        query = (
            self.payload_editor
            .toPlainText()
            .strip()
        )

        if not query:
            return

        encoded_query = quote(query)

        urls = {

            "google":
            f"https://www.google.com/search?q={encoded_query}",

            "bing":
            f"https://www.bing.com/search?q={encoded_query}",

            "github":
            f"https://github.com/search?q={encoded_query}",

            "shodan":
            f"https://www.shodan.io/search?query={encoded_query}"
        }

        webbrowser.open(
            urls[engine]
        )


app = QApplication(sys.argv)

window = MainWindow()

window.show()

sys.exit(app.exec())