from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.language import _


class AboutWindow(QtWidgets.QDialog):
    """Window to display the about window information.

    Attributes:
        emt_logo: Logo of the window.
        about_info: Widget to display the information.
        about_info_layout: Arranges the labels.
        button_box: Button to close the window.
    """
    def __init__(self, parent):
        """Initializes the AboutWindow class.

        Args:
            parent: Parent of this window.
        """
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.setWindowTitle(_("MCA"))
        self.setFixedSize(510, 430)
        # Create button box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setGeometry(QtCore.QRect(160, 385, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.button_box.button(QtWidgets.QDialogButtonBox.Close).setText(_("Close"))
        # Add logo
        self.emt_logo = QtWidgets.QLabel(self)
        self.emt_logo.setGeometry(QtCore.QRect(10, 10, 451, 241))
        self.emt_logo.setPixmap(QtGui.QPixmap(
            os.path.dirname(__file__) + "/../../images/emt_logo.png"))
        self.emt_logo.setScaledContents(False)
        # Create widget for the info
        self.about_info = QtWidgets.QWidget(self)
        self.about_info.setGeometry(QtCore.QRect(20, 300, 726, 90))
        self.about_info_layout = QtWidgets.QFormLayout(self.about_info)
        # Create labels
        font = QtGui.QFont()
        font.setPointSize(13)

        develop_label = QtWidgets.QLabel(self.about_info)
        develop_label.setText(_("Developed by:"))
        develop_label.setFont(font)

        develop_field_label = QtWidgets.QLabel(self.about_info)
        develop_field_label.setText(_("Measurement Engineering Group"))
        develop_field_label.setFont(font)

        homepage_label = QtWidgets.QLabel(self.about_info)
        homepage_label.setText(_("Homepage:"))
        homepage_label.setFont(font)

        homepage_field_label = QtWidgets.QLabel(self.about_info)
        homepage_field_label.setText(_('<a href="https://ei.uni-paderborn.de/en/electrical-engineering/emt/electrical-engineering/home">EMT</a>'))
        homepage_field_label.setOpenExternalLinks(True)
        homepage_field_label.setFont(font)

        version_label = QtWidgets.QLabel(self.about_info)
        version_label.setText(_("Version:"))
        version_label.setFont(font)

        mca_path = os.path.abspath(os.path.dirname(mca.__file__))
        with open(os.path.join(mca_path, 'version.txt')) as version_file:
            version = version_file.read()
        version_field_label = QtWidgets.QLabel(self.about_info)
        version_field_label.setText(version)
        version_field_label.setFont(font)
        # Add labels
        self.about_info_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, develop_label)
        self.about_info_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, develop_field_label)
        self.about_info_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, homepage_label)
        self.about_info_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, homepage_field_label)
        self.about_info_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, version_label)
        self.about_info_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, version_field_label)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
