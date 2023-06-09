from pathlib import Path
from mca.language import _

from PySide2 import QtWidgets, QtGui


resource_path = Path(__file__).parent / "../../resources/"

gifs_to_descriptions = ((resource_path / "create_block.gif",
                         "Create a block"),
                        (resource_path / "connect_blocks.gif",
                         "Connect two blocks"),
                        (resource_path / "plot_signal.gif",
                         "Plot a signal"),
                        (resource_path / "edit_parameters.gif",
                         "Edit parameters")
                        )


class IntroductionWindow(QtWidgets.QDialog):
    """Window opening on first startup of mca. Plays gifs to introduce the
    user to the program.

    Attributes:
        video_label: Label holding the movie.
        movie: Movie playing the current gif.
        button_box: Holds the next previous and close buttons.
        previous_button: Plays the previous gif when clicked.
        next_button: Plays the next gif when clicked.
        close_button: Closes the introduction window.
    """
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.setWindowTitle(_("MCA"))
        self.setLayout(QtWidgets.QVBoxLayout())
        # Set maximum since the movie does not scale
        self.setMaximumWidth(800)
        self.setMaximumHeight(600)

        self.video_label = QtWidgets.QLabel()
        self.movie = QtGui.QMovie()

        self.index = 0

        self.video_label.setMovie(self.movie)

        self.button_box = QtWidgets.QDialogButtonBox()
        self.previous_button = QtWidgets.QPushButton("Previous")
        self.next_button = QtWidgets.QPushButton("Next")
        self.previous_button.pressed.connect(self.prev_index)
        self.next_button.pressed.connect(self.next_index)
        self.previous_button.setDisabled(True)
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.pressed.connect(self.close)
        self.button_box.addButton(self.next_button,
                                  QtWidgets.QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.previous_button,
                                  QtWidgets.QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.close_button, QtWidgets.QDialogButtonBox.DestructiveRole)

        self.layout().addWidget(self.video_label)
        self.layout().addWidget(self.button_box)
        self.apply_current_index()

    def next_index(self):
        """Increases the index for playing the next gif."""
        self.index += 1
        if self.index == len(gifs_to_descriptions)-1:
            self.next_button.setDisabled(True)
        if self.index > 0:
            self.previous_button.setDisabled(False)
        self.apply_current_index()

    def prev_index(self):
        """Decreases the index for playing the previous gif."""
        self.index -= 1
        if self.index == 0:
            self.previous_button.setDisabled(True)
        if self.index < len(gifs_to_descriptions)-1:
            self.next_button.setDisabled(False)
        self.apply_current_index()

    def apply_current_index(self):
        """Applies the movie and window title according to the current index."""
        gif_name, description = gifs_to_descriptions[self.index]
        self.movie.stop()
        self.movie.setFileName(str(gif_name))
        self.setWindowTitle(description)
        self.movie.start()
