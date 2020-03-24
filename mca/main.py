import sys
from PySide2 import QtWidgets, QtCore
from mca.gui.mainwindow import MainWindow


def main():
    while True:
        try:
            app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            app = QtCore.QCoreApplication.instance()
        window = MainWindow()
        window.show()
        exit_code = app.exec_()
        if exit_code != window.exit_code_reboot:
            break
    return exit_code
