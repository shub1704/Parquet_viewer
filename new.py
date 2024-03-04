from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("My Window")

        try:
            # Code that may raise an exception
            a = 1 / 0
        except Exception as e:
            # Show error message box
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
