from PySide2 import QtWidgets, QtCore, QtGui
import os

from mca.language import _


class AboutWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.setFixedSize(510, 380)
        # Create button box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setGeometry(QtCore.QRect(160, 330, 341, 32))
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
        self.about_info.setGeometry(QtCore.QRect(20, 260, 726, 61))
        self.about_info_layout = QtWidgets.QFormLayout(self.about_info)
        # Create labels
        font = QtGui.QFont()
        font.setPointSize(13)
        label_1 = QtWidgets.QLabel(self.about_info)
        label_1.setText(_("Developed by:"))
        label_1.setFont(font)
        label_2 = QtWidgets.QLabel(self.about_info)
        label_2.setText(_("Measurement Engineering Group"))
        label_2.setFont(font)
        label_3 = QtWidgets.QLabel(self.about_info)
        label_3.setText(_("Homepage:"))
        label_3.setFont(font)
        label_4 = QtWidgets.QLabel(self.about_info)
        label_4.setText(_('<a href="https://ei.uni-paderborn.de/en/electrical-engineering/emt/electrical-engineering/home">EMT</a>'))
        label_4.setOpenExternalLinks(True)
        label_4.setFont(font)
        # Add labels

        self.about_info_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, label_1)
        self.about_info_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, label_2)
        self.about_info_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, label_3)
        self.about_info_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, label_4)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
