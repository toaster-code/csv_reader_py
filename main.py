import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QAction, QLineEdit, QLabel, QMenu, QHeaderView, QMessageBox
from PyQt5.QtGui import QKeySequence, QColor
from PyQt5.QtCore import Qt

import pandas as pd

class CSVReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Reader")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.file_label = QLabel("Enter CSV file path:")
        self.layout.addWidget(self.file_label)

        self.file_edit = QLineEdit()
        self.layout.addWidget(self.file_edit)

        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.load_button)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.create_menu()

        self.current_chunk_index = 0
        self.chunk_size = 1000

        self.scroll_percentage_trigger = 0.8
        self.table.verticalScrollBar().rangeChanged.connect(self.update_scroll_trigger)

        self.table.verticalScrollBar().valueChanged.connect(self.scroll_event)


    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.load_csv)
        file_menu.addAction(open_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_csv)
        file_menu.addAction(close_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def load_csv(self):
        file_path = self.file_edit.text().strip()
        if not file_path:
            default_path = os.path.join(os.path.expanduser("~"), "Downloads")
            file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", default_path, "CSV Files (*.csv)")
        if file_path:
            try:
                self.reader = pd.read_csv(file_path, iterator=True, chunksize=self.chunk_size)
                self.load_next_chunk()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading CSV: {e}")

    def close_csv(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def load_next_chunk(self):
        try:
            df = next(self.reader)
            if not df.empty:
                start_row = self.table.rowCount()  # Start row index for adding items
                num_rows = len(df)
                num_columns = len(df.columns)
                column_names = df.columns.tolist()
                print("Start Row:", start_row)
                print("Num Rows:", num_rows)
                print("Num Columns:", num_columns)
                print("Column Names:", column_names)
                self.table.setRowCount(start_row + num_rows)
                if self.table.columnCount() != num_columns:
                    self.table.setColumnCount(num_columns)  # Set column count if not already set
                    self.table.setHorizontalHeaderLabels(column_names)  # Set column labels
                for row_index in range(num_rows):
                    for col_index in range(num_columns):
                        item = QTableWidgetItem(str(df.iloc[row_index, col_index]))
                        self.table.setItem(start_row + row_index, col_index, item)
                        if (start_row + row_index) % 2 == 0:
                            item.setBackground(QColor(144, 238, 144))  # Light green color
        except StopIteration:
            pass

    def update_scroll_trigger(self, min_val, max_val):
        self.scroll_trigger_position = max_val * self.scroll_percentage_trigger

    def scroll_event(self, value):
        if value >= self.scroll_trigger_position:
            self.load_next_chunk()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVReaderApp()
    window.show()
    sys.exit(app.exec_())
