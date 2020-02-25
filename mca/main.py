import sys
from PySide2 import QtWidgets
from mca.gui.mainwindow import MainWindow
import os


def main():
    os.environ['QT_PLUGIN_PATH'] = "/upb/users/k/kevink2/profiles/unix/emt/.local/lib/python3.7/site-packages/PySide2/Qt/plugins"
    # Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # QWidget
    # QMainWindow using QWidget as central widget
    window = MainWindow()

    window.show()
    # Execute application
    sys.exit(app.exec_())
