from PySide2 import QtWidgets, QtCore, QtGui
from mca.framework import parameters
from mca.gui import parameter_widgets


class ParameterWindow(QtWidgets.QDialog):
    def __init__(self, block):
        QtWidgets.QDialog.__init__(self)
        self.block = block
        self.resize(500, 400)
        self.setWindowTitle("Edit")
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

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),
                               self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),
                               self.reject)

        self.display_parameters()
        QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), block.apply_parameter_changes)

    def display_parameters(self):
        block_parameters = self.block.parameters.values()
        if block_parameters:
            parameter_label = QtWidgets.QLabel("Parameters:", self.layout_widget)
            self.layout.addWidget(parameter_label, 0, 0, 1, 1)
            font = QtGui.QFont()
            font.setFamily("TeXGyreHeros")
            font.setPointSize(11)
            font.setWeight(75)
            font.setBold(True)
            parameter_label.setFont(font)
        for block_parameter, index in zip(block_parameters, range(1, len(block_parameters) + 1)):
            if isinstance(block_parameter, parameters.FloatParameter):
                name_label = QtWidgets.QLabel(self.layout_widget)
                self.layout.addWidget(name_label, index, 0, 1, 1)
                name_label.setText(block_parameter.name)
                line_edit = parameter_widgets.FloatWidget(block_parameter, self.layout_widget)
                QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), line_edit.set_parameter)
                line_edit.setText(str(block_parameter.value))
                self.layout.addWidget(line_edit, index, 1, 1, 1)
                if block_parameter.unit:
                    unit_label = QtWidgets.QLabel(self.layout_widget)
                    self.layout.addWidget(unit_label, index, 2, 1, 1)
                    unit_label.setText(block_parameter.unit)

            if isinstance(block_parameter, parameters.IntParameter):
                name_label = QtWidgets.QLabel(self.layout_widget)
                self.layout.addWidget(name_label, index, 0, 1, 1)
                name_label.setText(block_parameter.name)
                line_edit = parameter_widgets.IntWidget(block_parameter, self.layout_widget)
                QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), line_edit.set_parameter)
                line_edit.setText(str(block_parameter.value))
                self.layout.addWidget(line_edit, index, 1, 1, 1)
                if block_parameter.unit:
                    unit_label = QtWidgets.QLabel(self.layout_widget)
                    self.layout.addWidget(unit_label, index, 2, 1, 1)
                    unit_label.setText(block_parameter.unit)

            if isinstance(block_parameter, parameters.StrParameter):
                name_label = QtWidgets.QLabel(self.layout_widget)
                self.layout.addWidget(name_label, index, 0, 1, 1)
                name_label.setText(block_parameter.name)
                line_edit = parameter_widgets.StringWidget(block_parameter, self.layout_widget)
                QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), line_edit.set_parameter)
                line_edit.setText(block_parameter.value)
                self.layout.addWidget(line_edit, index, 1, 1, 1)

            if isinstance(block_parameter, parameters.ChoiceParameter):
                name_label = QtWidgets.QLabel(self.layout_widget)
                self.layout.addWidget(name_label, index, 0, 1, 1)
                name_label.setText(block_parameter.name)
                combo_box = parameter_widgets.ChoiceWidget(block_parameter, self.layout_widget)
                for i in range(len(block_parameter.choices)):
                    combo_box.addItem(block_parameter.choices[i][1], userData=block_parameter.choices[i][0])
                    if block_parameter.choices[i][0] == block_parameter.value:
                        combo_box.setCurrentText(block_parameter.choices[i][1])

                QtCore.QObject.connect(self, QtCore.SIGNAL("accepted()"), combo_box.set_parameter)
                self.layout.addWidget(combo_box, index, 1, 1, 1)
                if block_parameter.unit:
                    unit_label = QtWidgets.QLabel(self.layout_widget)
                    self.layout.addWidget(unit_label, index, 2, 1, 1)
                    unit_label.setText(block_parameter.unit)

            if isinstance(block_parameter, parameters.BoolParameter):
                check_box = QtWidgets.QComboBox(self.layout_widget)
                self.layout.addWidget(check_box, index, 1, 1, 1)