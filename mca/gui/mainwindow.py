from PySide2 import QtWidgets, QtCore, QtGui
import inspect
import os

import mca.blocks
from mca.framework import block_registry
from mca.gui import block_list, block_display
from mca import config
from mca.language import _


class MainWindow(QtWidgets.QMainWindow):
    """Main window of the mca. Holds the main widgets of the application.

    Attributes:
        menu: Menu bar of the application.
        file_menu: File menu.
        language_menu: Language menu.
        blocks (list): List of all block classes.
        main_widget: Splitter widget to split the :class:`.BlockList` and the
                     :class:`.BlockScene`.
        scene: :class:`.BlockScene` to manage and hold blocks.
        view: :class:`.BlockView` to visualize the items of the
              :class:`.BlockScene`.
    """

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.resize(1000, 800)
        self.setWindowTitle(_("MCA"))

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu(_("File"))
        self.language_menu = self.menu.addMenu(_("Language"))
        languages = [("Deutsch", "de"), ("English", "en")]

        self.setWindowIcon(QtGui.QIcon(
            os.path.dirname(mca.blocks.__file__) + "/icons/emt_logo.png"))
        for i in languages:
            action = QtWidgets.QAction(i[0], self)
            action.triggered.connect(change_language(i[1]))
            self.language_menu.addAction(action)

        save_action = QtWidgets.QAction(_("Save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        self.save_file_path = None
        self.file_menu.addAction(save_action)

        save_as_action = QtWidgets.QAction(_("Save as"), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        self.file_menu.addAction(save_as_action)

        exit_action = QtWidgets.QAction(_("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip(_("Close Application"))
        exit_action.triggered.connect(self.exit_app)
        self.file_menu.addAction(exit_action)

        self.conf = config.Config()

        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.block_classes = mca.blocks.block_classes
        self.scene = block_display.BlockScene(self.main_widget)
        self.block_list = block_list.BlockList(self, self.block_classes,
                                               self.scene)
        self.main_layout.addWidget(self.block_list)
        self.view = block_display.BlockView(scene=self.scene, parent=self)
        self.view.show()
        self.main_layout.addWidget(self.view)
        self.setCentralWidget(self.main_widget)

    @QtCore.Slot()
    def exit_app(self):
        """Quit the application."""
        QtWidgets.QApplication.quit()

    def save_file_as(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, _("Save"), self.conf["save_file_dir"], "json (*.json)")
        if not file_name[0]:
            return
        if not file_name[0].endswith(".json"):
            QtWidgets.QMessageBox.warning(
                self, _("Error"), _("File has to be a .json!"))
        else:
            self.save_file_path = file_name[0]
            self.save_file()

    def save_file(self):
        if self.save_file_path:
            block_registry.Registry.save_block_structure(self.save_file_path)
        else:
            self.save_file_as()


def change_language(new_language):
    """Change the language in the config.

    Args:
        new_language (str): New language which should be applied.
    """

    def tmp():
        config.Config()["language"] = new_language
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(_("Changes will be applied after restart."))
        msg_box.exec()

    return tmp
