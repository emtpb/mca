from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.framework import parameters
from mca.gui import parameter_widgets
from mca.language import _

widget_dict = {parameters.BoolParameter: parameter_widgets.BoolWidget,
               parameters.IntParameter: parameter_widgets.IntWidget,
               parameters.FloatParameter: parameter_widgets.FloatWidget,
               parameters.ChoiceParameter: parameter_widgets.ChoiceWidget,
               parameters.StrParameter: parameter_widgets.StringWidget}


class ParameterWindow(QtWidgets.QDialog):
    """Window to display the parameter of a :class:`.Block`.

    Attributes:
        block: Reference of the :class:`.Block` instance.
        layout_widget: Widget holding the layout.
        layout: Layout which arranges the :mod:`.parameter_widgets`
                underneath each other.
    """

    def __init__(self, block):
        """Initialize ParameterWindow class.

        Args:
            block: Reference of the :class:`.Block` instance.
        """
        QtWidgets.QDialog.__init__(self)
        self.block = block
        self.resize(500, 400)
        self.setWindowTitle(_("Edit"))
        self.setMaximumSize(QtCore.QSize(500, 400))
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(140, 360, 329, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        self.layout_widget = QtWidgets.QWidget(self)
        grid_y_size = (len(block.parameters) + 1) * 25
        self.layout_widget.setGeometry(QtCore.QRect(9, 9, 480, grid_y_size))
        self.layout_widget.setObjectName("layout_widget")
        self.layout = QtWidgets.QGridLayout(self.layout_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        if self.block.icon_file:
            icon = QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + self.block.icon_file)
            self.setWindowIcon(icon)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),
                               self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),
                               self.reject)

        self.display_parameters()
        QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"),
                               block.apply_parameter_changes)

    def display_parameters(self):
        """Arranges the given parameters in rows in the window underneath each
        other. One row includes the name of the parameter as a label, the
        desired widget and the unit optionally.
        """
        block_parameters = self.block.parameters.values()
        if block_parameters:
            parameter_label = QtWidgets.QLabel(_("Parameters:"),
                                               self.layout_widget)
            self.layout.addWidget(parameter_label, 0, 0, 1, 1)
            font = QtGui.QFont()
            font.setFamily("TeXGyreHeros")
            font.setPointSize(11)
            font.setWeight(75)
            font.setBold(True)
            parameter_label.setFont(font)
        for block_parameter, index in zip(block_parameters,
                                          range(1, len(block_parameters) + 1)):
            if not isinstance(block_parameter, parameters.BoolParameter):
                name_label = QtWidgets.QLabel(self.layout_widget)
                name_label.setText(block_parameter.name)
                self.layout.addWidget(name_label, index, 0, 1, 1)
            widget = widget_dict[type(block_parameter)](block_parameter,
                                                        self.layout_widget)
            widget.read_parameter()
            QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"),
                                   widget.set_parameter)
            self.layout.addWidget(widget, index, 1, 1, 1)
            if block_parameter.unit:
                unit_label = QtWidgets.QLabel(self.layout_widget)
                self.layout.addWidget(unit_label, index, 2, 1, 1)
                unit_label.setText(block_parameter.unit)
