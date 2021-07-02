from PySide2 import QtWidgets, QtGui
import os
import ntpath

from mca import blocks, config
from mca.framework import block_registry
from mca.gui.pyside2 import block_list, block_display, about_window
from mca.language import _


class MainWindow(QtWidgets.QMainWindow):
    """Main window of the mca. Holds the main widgets of the application.

    Attributes:
        conf: Reference of the user config :class:`.Config`.
        menu: Menu bar of the application.
        file_menu: File menu.
        language_menu: Language menu.
        main_widget: Main widget with horizontal layout for child widgets.
        main_layout: Horizontal layout of the main widget
        scene: :class:`.BlockScene` to manage and hold blocks.
        view: :class:`.BlockView` to visualize the items of the
              :class:`.BlockScene`.
        search_widget: Widget with vertical layout holding the search bar and
                       the :class:`.BlockList`.
        search_bar: Reference of the search bar.
        block_list: Reference of the :class:`.BlockList`.
        save_file_path: Path of the file to save the block structure to.
    """

    def __init__(self):
        """Initializes MainWindow."""
        QtWidgets.QMainWindow.__init__(self)
        self.resize(1000, 800)

        self.conf = config.Config()

        self.about_window = about_window.AboutWindow(self)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu(_("File"))
        self.language_menu = self.menu.addMenu(_("Language"))

        open_about_window = QtWidgets.QAction(_("About"), self)
        open_about_window.triggered.connect(self.about_window.show)

        self.menu.addAction(open_about_window)
        languages = [("Deutsch", "de"), ("English", "en")]

        self.setWindowIcon(QtGui.QIcon(
            os.path.dirname(__file__) + "/../../images/emt_logo.png"))
        for i in languages:
            action = QtWidgets.QAction(i[0], self)
            action.triggered.connect(change_language(i[1]))
            self.language_menu.addAction(action)

        new_action = QtWidgets.QAction(_("New"), self)
        new_action.triggered.connect(self.new_file)
        self.file_menu.addAction(new_action)

        open_action = QtWidgets.QAction(_("Open"), self)
        open_action.triggered.connect(self.open_file_dialog)
        self.file_menu.addAction(open_action)

        self.open_recent_menu = QtWidgets.QMenu(_("Open Recent"), self)
        self.update_recent_menu()

        self.file_menu.addMenu(self.open_recent_menu)

        save_action = QtWidgets.QAction(_("Save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        self.save_file_path = None
        self.file_menu.addAction(save_action)

        save_as_action = QtWidgets.QAction(_("Save as"), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        self.file_menu.addAction(save_as_action)

        clear_action = QtWidgets.QAction(_("Clear all blocks"), self)
        clear_action.triggered.connect(self.clear_all_blocks)
        self.file_menu.addAction(clear_action)

        exit_action = QtWidgets.QAction(_("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip(_("Close Application"))
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        self.modified = False

        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)

        self.search_widget = QtWidgets.QWidget(self.main_widget)
        self.search_widget.setMaximumSize(250, 16777215)
        self.search_widget.setMinimumSize(200, 0)
        self.search_widget.setLayout(QtWidgets.QVBoxLayout())

        self.scene = block_display.BlockScene(self.main_widget)
        self.view = block_display.BlockView(scene=self.scene, parent=self)
        self.view.show()

        self.search_bar = QtWidgets.QLineEdit(self.search_widget)
        self.search_bar.setPlaceholderText(_("Search..."))
        self.search_bar.setClearButtonEnabled(True)
        self.block_list = block_list.BlockList(self.search_widget,
                                               self.scene, self.search_bar)
        self.search_widget.layout().addWidget(self.search_bar)
        self.search_widget.layout().addWidget(self.block_list)

        self.scene.block_list = self.block_list

        self.main_layout.addWidget(self.search_widget)
        self.main_layout.addWidget(self.view)
        self.setCentralWidget(self.main_widget)
        # Save warning message
        self.save_warning_message = QtWidgets.QMessageBox(
            parent=self,
            icon=QtWidgets.QMessageBox.Warning,
            text=_("The document has been modified.\nDo you want to save your changes?"),
        )
        self.save_warning_message.setStandardButtons(QtWidgets.QMessageBox.Yes
                                                     | QtWidgets.QMessageBox.Cancel
                                                     | QtWidgets.QMessageBox.No)
        self.save_warning_message.button(QtWidgets.QMessageBox.Yes).setText(_("Yes"))
        self.save_warning_message.button(QtWidgets.QMessageBox.Cancel).setText(
            _("Cancel"))
        self.save_warning_message.button(QtWidgets.QMessageBox.No).setText(
            _("No"))

    def closeEvent(self, event):
        """Method invoked when the application gets closed. Asks the user to
        save unsaved changes.
        """
        if self.save_maybe():
            event.accept()
        else:
            event.ignore()

    def new_file(self):
        """Creates a new file."""
        if self.save_maybe():
            self.scene.clear()
            self.save_file_path = None
            self.modified = False

    def open_file_dialog(self):
        """Opens file dialog to let the user select a file to open."""
        if self.save_maybe():
            file_name = QtWidgets.QFileDialog.getOpenFileName(
                self, _("Select a file to open"), self.conf["load_file_dir"],
                "json (*json)")
            if file_name[0]:
                self.open_file(file_name[0])

    def open_file_direct(self, file_name):
        """Returns a function that opens a specific file.

        Args:
            file_name (str): Path of the file to open.
        """
        def tmp():
            if self.save_maybe():
                self.open_file(file_name)
        return tmp

    def open_file(self, file_path):
        """Opens given file path. Loads the blocks in the file into the block
        structure and then tells the :class:`.BlockScene` to visualize them.

        Args:
            file_path (str): Path of the file to open.
        """
        self.scene.clear()
        loaded_blocks = block_registry.Registry.load_block_structure(file_path)
        self.save_file_path = file_path
        self.conf["load_file_dir"] = file_path
        if file_path in self.conf["recent_files"]:
            self.conf["recent_files"].remove(file_path)
        self.conf["recent_files"] = [file_path] + self.conf["recent_files"][:3]
        self.update_recent_menu()
        self.scene.create_blocks(loaded_blocks)
        self.modified = False

    def update_recent_menu(self):
        """Updates the actions in the recent menu based on the last chosen
        files.
        """
        self.open_recent_menu.clear()
        for file_name in self.conf["recent_files"]:
            open_file_action = QtWidgets.QAction(
                ntpath.basename(file_name), self)
            open_file_action.triggered.connect(
                self.open_file_direct(file_name))
            self.open_recent_menu.addAction(open_file_action)

    def save_file_as(self):
        """Opens file dialog and save the current state to the given file.

        Returns:
            bool: True, if saving has been successful. False, otherwise.
        """
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, _("Save"), self.conf["save_file_dir"], "json (*.json)")[0]
        if not file_name:
            return False
        elif "." in file_name and not file_name.endswith(".json"):
            QtWidgets.QMessageBox.warning(
                self, _("MCA"),
                _("File has to be a .json"), QtWidgets.QMessageBox.Ok)
            return False
        if not file_name.endswith(".json"):
            file_name += ".json"
        self.save_file_path = file_name
        self.conf["save_file_dir"] = os.path.dirname(self.save_file_path)
        self.save_file()

        self.conf["recent_files"] = [file_name] + self.conf["recent_files"][:3]
        self.update_recent_menu()
        return True

    def save_file(self):
        """Saves the current state.

        Opens up a file dialog if no safe file path has been specified yet.

        Returns:
            bool: True, if the file has been saved successfully.
                  Otherwise False.
        """
        if self.save_file_path:
            block_registry.Registry.save_block_structure(self.save_file_path)
            self.modified = False
            return True
        else:
            return self.save_file_as()

    def save_maybe(self):
        """Opens up a message dialogue asking if the user wants to save
        changes if the document has been modified.

        Returns:
            bool: True, if the action was accepted regardless
                  if the file was saved or not. False, if the action was
                  cancelled.
        """
        if self.modified:
            result = self.save_warning_message.exec_()
        else:
            return True
        if result == QtWidgets.QMessageBox.Yes:
            return self.save_file()
        elif result == QtWidgets.QMessageBox.No:
            return True
        else:
            return False

    def clear_all_blocks(self):
        """Clears the :class:`.BlockScene` from all blocks."""
        message_box = QtWidgets.QMessageBox(parent=self,
                                            icon=QtWidgets.QMessageBox.Question,
                                            text=_("Are you sure you want to remove all blocks?"))
        message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        message_box.button(QtWidgets.QMessageBox.Cancel).setText(_("Cancel"))
        message_box.button(QtWidgets.QMessageBox.Yes).setText(
            _("Yes"))
        result = message_box.exec_()
        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            self.scene.clear()

    @property
    def modified(self):
        """Gets or sets whether there are any unsaved changes.

        Setting this property causes an update of the window title.
        """
        return self._modified

    @modified.setter
    def modified(self, value):
        self._modified = value
        if self.save_file_path:
            show_file = self.save_file_path
        else:
            show_file = _("untitled.json")
        if self._modified:
            show_file = "*" + show_file
        self.setWindowTitle("{} - {}".format(show_file, _("MCA")))


def change_language(language):
    """Returns a function which changes the language in the config.

    Args:
        language (str): Language the function changes to.
    """

    def tmp():
        config.Config()["language"] = language
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(_("Changes will be applied after restart."))
        msg_box.exec()

    return tmp
