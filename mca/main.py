import sys
from PySide2 import QtWidgets
from mca.gui.mainwindow import MainWindow


def main():
    # Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # QWidget
    # QMainWindow using QWidget as central widget
    window = MainWindow()

    window.show()
    # Execute application
    sys.exit(app.exec_())

    app = QApplication(sys.argv)
    ex = MyAppMainWindow()

    while currentExitCode == ex.EXIT_CODE_REBOOT:
        currentExitCode = app.exec_()

        return currentExitCode
