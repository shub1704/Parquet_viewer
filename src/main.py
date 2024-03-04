import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QFileDialog, QLineEdit, QPushButton, QLabel,QMessageBox
from PyQt5.QtGui import QStandardItemModel, QColor, QStandardItem, QIcon
from PyQt5.QtCore import Qt
from operations import PandasModel


class ParquetViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Parquet Viewer")
        # Set window icon
        self.setWindowIcon(QIcon(r'logo\viewer.png'))

        # Create table view to display data
        self.table_view = QTableView(self)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.setCentralWidget(self.table_view)

        # Create a search box and search button to show dataframe
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search column...")
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.search_columns)
        self.toolBar = self.addToolBar("Search")
        self.toolBar.addWidget(self.search_box)
        self.toolBar.addWidget(self.search_button)


        # Create the button to show column names
        self.button = QPushButton('Columns', self)
        self.button.clicked.connect(self.toggle_show_column_names)
        self.toolBar.addWidget(self.button)

        # Add label to show the dimensions of DataFrame
        self.df_dim_label = QLabel(self)
        self.toolBar.addWidget(self.df_dim_label)
        #self.layout.addWidget(self.df_dim_label)

        # Initialize the DataFrame to be displayed
        self.df = None
        # Create menu bar
        menu_bar = self.menuBar()
        # Create file menu
        file_menu = menu_bar.addMenu("File")

        # Create open action
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.open_file)

        # Initialize highlighted column indices
        self.highlighted_columns = set()

    def open_file(self):
        try:
            # Get file path using QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Parquet File", "", "Parquet Files (*.parquet)")

            # Read Parquet file into a Pandas DataFrame
            self.df = pd.read_parquet(file_path)

            # Create QStandardItemModel to hold the DataFrame data
            model = QStandardItemModel(self.df.shape[0], self.df.shape[1], self)
            model.setHorizontalHeaderLabels(self.df.columns)

            # Populate the model with the DataFrame data
            for row in range(self.df.shape[0]):
                for column in range(self.df.shape[1]):
                    item = QStandardItem(str(self.df.iloc[row, column]))
                    item.setTextAlignment(Qt.AlignCenter)
                    model.setItem(row, column, item)

            # Set the model on the table view
            self.table_view.setModel(model)
            # Update the DataFrame dimensions label
            self.update_df_dim_label() 
        except Exception as e:
            # Show error message box
            QMessageBox.critical(self, "Error", str(e))


    def highlight_columns(self):
        # Get search text and split into column names
        search_text = self.search_box.text().lower()
        column_names = [name.strip() for name in search_text.split(",")]

        # Get model from table view
        model = self.table_view.model()

        # Clear previous column highlights
        for column in self.highlighted_columns:
            for row in range(model.rowCount()):
                item = model.item(row, column)
                item.setBackground(Qt.white)

        # Highlight matching columns
        if column_names:
            for column in range(model.columnCount()):
                if model.headerData(column, Qt.Horizontal).lower() in column_names:
                    self.highlighted_columns.add(column)
                    for row in range(model.rowCount()):
                        item = model.item(row, column)
                        item.setBackground(QColor(215, 231, 255))

        # Remove non-matching columns from highlighted columns set
        self.highlighted_columns -= set(range(model.columnCount())) - set(self.highlighted_columns)

    def toggle_show_column_names(self):
        if self.button.text() == 'Columns':
            # Create a new DataFrame with only the column names
            col_names = self.df.columns.tolist()
            col_df = pd.DataFrame(col_names, columns=['Column Names'])
            # Set the new DataFrame in the table view
            model = PandasModel(col_df)
            self.table_view.setModel(model)
            # Update the button text
            self.button.setText('DataFrame')
        else:
            # Set the original DataFrame in the table view
            model = PandasModel(self.df)
            self.table_view.setModel(model)
            # Update the button text
            self.button.setText('Columns')  
        
    def update_df_dim_label(self):
        # Update the DataFrame dimensions label with the current dimensions
        if self.df is not None:
            self.df_dim_label.setText(f"Dimensions: {self.df.shape[0]} rows x {self.df.shape[1]} columns")
        else:
            self.df_dim_label.setText("")

    def search_columns(self):
        try:
            # Get the text entered in the search box
            search_text = self.search_box.text()
            if search_text:
                # Split the search text into a list of column names
                search_columns = [col.strip() for col in search_text.split(',')]
                # Get a list of columns to show based on the search text
                columns_to_show = [col for col in self.df.columns.tolist() if col in search_columns]
                if self.search_button.text() == 'Search':
                    if columns_to_show:
                        # Create a new DataFrame with only the selected columns
                        selected_df = self.df[columns_to_show]
                        # Set the new DataFrame in the table view
                        model = PandasModel(selected_df)
                        self.table_view.setModel(model)
                        # Update the DataFrame dimensions label
                        self.df_dim_label.setText(f"Dimensions: {selected_df.shape[0]} rows x {selected_df.shape[1]} columns")
                    else:
                        # If no columns match the search text, show an empty DataFrame
                        empty_df = pd.DataFrame()
                        model = PandasModel(empty_df)
                    self.search_button.setText('Dataframe')
                else:
                    # If the button has not been clicked before, perform the search
                    model = PandasModel(self.df)
                    self.table_view.setModel(model)
                    self.search_button.setText('Search')
                    self.update_df_dim_label() 
        except Exception as e:
            # Show error message box
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    # Create QApplication
    app = QApplication(sys.argv)
    parquet_viewer = ParquetViewer()
    parquet_viewer.show()
    sys.exit(app.exec_())
