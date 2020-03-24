import sys
from PySide2 import QtWidgets
from mca.gui.mainwindow import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.argv(app.exec_())
