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


class EditWindow(QtWidgets.QDialog):
    """Window to display the parameter and meta data of a :class:`.Block`.

    Attributes:
        block: Reference of the :class:`.Block` instance.
        main_layout: Arranges the tab widget und the buttons.
        parameter_tab: Tab for holding the parameter widgets.
        parameter_layout: Grid layout which arranges the parameter widgets.
        meta_data_tab: Tab for holding the meta data widgets.
        meta_data_layout: Grid layout which arranges the meta data widgets.
        button_box: "Ok|Cancel" button widgets.
    """

    def __init__(self, block):
        """Initialize EditWindow class.

        Args:
            block: Reference of the :class:`.Block` instance.
        """
        QtWidgets.QDialog.__init__(self)
        self.block = block
        self.resize(500, 400)
        self.setMaximumSize(QtCore.QSize(500, 4000))
        self.setWindowTitle(_("Edit"))
        # Define font for headline labels in the edit window
        self.headline_font = QtGui.QFont()
        self.headline_font.setFamily("TeXGyreHeros")
        self.headline_font.setPointSize(11)
        self.headline_font.setWeight(75)
        self.headline_font.setBold(True)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.tab_widget = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        # Initialize parameter tab
        self.parameter_tab = QtWidgets.QWidget()
        self.parameter_layout = QtWidgets.QGridLayout(self.parameter_tab)
        parameters_tab_height = (len(block.parameters) + 1) * 30
        self.parameter_tab.setFixedHeight(parameters_tab_height)
        self.tab_widget.addTab(self.parameter_tab, "Parameters")
        self.display_parameters()
        # Initialize meta data tab
        if block.outputs:
            self.meta_data_tab = QtWidgets.QWidget()
            self.meta_data_layout = QtWidgets.QGridLayout(self.meta_data_tab)
            meta_data_tab_height = len(block.outputs)*210
            self.meta_data_tab.setFixedHeight(meta_data_tab_height)
            self.tab_widget.addTab(self.meta_data_tab, "Meta data")
            self.tab_widget.setCurrentIndex(0)
        self.display_meta_data()
        # Set buttons
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setGeometry(QtCore.QRect(140, 360, 329, 23))
        self.button_box.setContentsMargins(0, 0, 10, 10)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.main_layout.addWidget(self.button_box)
        # Set custom window icon
        if self.block.icon_file:
            icon = QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + self.block.icon_file)
            self.setWindowIcon(icon)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("accepted()"),
                               self.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("rejected()"),
                               self.reject)

        QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"),
                               block.apply_parameter_changes)

    def display_parameters(self):
        """Arranges parameters of a block in rows in the window underneath each
        other. One row includes the name of the parameter as a label, the
        desired widget and the unit optionally.
        """
        block_parameters = self.block.parameters.values()
        if block_parameters:
            parameter_label = QtWidgets.QLabel(_("Parameters:"),
                                               self.parameter_tab)
            self.parameter_layout.addWidget(parameter_label, 0, 0, 1, 1)
            parameter_label.setFont(self.headline_font)
        for block_parameter, index in zip(block_parameters,
                                          range(1, len(block_parameters) + 1)):
            if not isinstance(block_parameter, parameters.BoolParameter):
                name_label = QtWidgets.QLabel(block_parameter.name)
                self.parameter_layout.addWidget(name_label, index, 0, 1, 1)
            widget = widget_dict[type(block_parameter)](block_parameter)
            widget.read_parameter()
            QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"),
                                   widget.set_parameter)
            self.parameter_layout.addWidget(widget, index, 1, 1, 1)
            if block_parameter.unit:
                unit_label = QtWidgets.QLabel(block_parameter.unit)
                self.parameter_layout.addWidget(unit_label, index, 2, 1, 1)

    def display_meta_data(self):
        """Arranges the meta data of the outputs of the block in the window."""
        for index, output in enumerate(self.block.outputs):
            if output.name:
                output_label = QtWidgets.QLabel(
                    "Output '{}' meta data:".format(output.name))
            else:
                output_label = QtWidgets.QLabel("Output meta data:")
            output_label.setFont(self.headline_font)
            self.meta_data_layout.addWidget(output_label, index*8, 0, 1, 1)
            self.meta_data_layout.addWidget(QtWidgets.QLabel("Signal name:"),
                                            index*8+1, 0, 1, 1)
            name_edit = QtWidgets.QLineEdit(output.meta_data.name)
            self.meta_data_layout.addWidget(name_edit, index*8+1, 1, 1, 1)
            self.meta_data_layout.addWidget(
                QtWidgets.QLabel("Abscissa quantity:"), index*8+2, 0, 1, 1)
            quantity_a_edit = QtWidgets.QLineEdit(output.meta_data.quantity_a)
            self.meta_data_layout.addWidget(quantity_a_edit, index*8+2, 1, 1, 1)
            symbol_a_edit = QtWidgets.QLineEdit(output.meta_data.symbol_a)
            self.meta_data_layout.addWidget(
                QtWidgets.QLabel("Abscissa symbol:"), index*8+3, 0, 1, 1)
            self.meta_data_layout.addWidget(symbol_a_edit, index*8+3, 1, 1, 1)
            self.meta_data_layout.addWidget(QtWidgets.QLabel("Abscissa unit:"),
                                            index*8+4, 0, 1, 1)
            unit_a_edit = QtWidgets.QLineEdit(output.meta_data.unit_a)
            self.meta_data_layout.addWidget(unit_a_edit, index*8+4, 1, 1, 1)
            self.meta_data_layout.addWidget(QtWidgets.QLabel("Ordinate quantity:"),
                                            index*8+5, 0, 1, 1)
            quantity_o_edit = QtWidgets.QLineEdit(output.meta_data.quantity_o)
            self.meta_data_layout.addWidget(quantity_o_edit, index*8+5, 1, 1, 1)
            self.meta_data_layout.addWidget(QtWidgets.QLabel("Ordinate symbol:"),
                                            index*8+6, 0, 1, 1)
            symbol_o_edit = QtWidgets.QLineEdit(output.meta_data.symbol_o)
            self.meta_data_layout.addWidget(symbol_o_edit, index*8+6, 1, 1, 1)
            self.meta_data_layout.addWidget(QtWidgets.QLabel("Ordinate unit:"),
                                            index*8+7, 0, 1, 1)
            unit_o_edit = QtWidgets.QLineEdit(output.meta_data.unit_o)
            self.meta_data_layout.addWidget(unit_o_edit, index*8+7, 1, 1, 1)

            def set_meta_data():
                output.meta_data.name = name_edit.text()
                output.meta_data.quantity_a = quantity_a_edit.text()
                output.meta_data.symbol_a = symbol_a_edit.text()
                output.meta_data.unit_a = unit_a_edit.text()
                output.meta_data.quantity_o = quantity_o_edit.text()
                output.meta_data.symbol_o = symbol_o_edit.text()
                output.meta_data.unit_o = unit_o_edit.text()
            QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"),
                                   set_meta_data)
