import os

from PySide2 import QtWidgets
from united import Unit

from mca import exceptions
from mca.config import Config
from mca.framework import parameters
from mca.language import _

config = Config()


class BaseParameterWidget:
    """Basic parameter widget for all specific parameter widgets.

    Attributes:
        parameter: Given :class:`.Parameter` to display.
        prev_value: Stores the last value of the parameter until changes get
                    finally applied.
        changed (bool): Indicates whether the current value in the widget
                        differs from the previous value.
    """

    def __init__(self, parameter):
        """Initializes BaseParameterWidget class.

        Args:
            parameter: Given :class:`.Parameter` to display.
        """
        self.parameter = parameter
        self.prev_value = self.parameter.value
        self.changed = False
        self.setFixedHeight(25)

    def write_parameter(self):
        """Takes the current value in the widget and sets
        it in the parameter.
        """
        raise NotImplementedError

    def read_parameter(self):
        """Reads the current value in the parameter
        and sets it in the widget.
        """
        raise NotImplementedError

    def check_changed(self):
        """Identifies if the value differs from the previous value and
        visually modifies the widget.
        """
        raise NotImplementedError

    def apply_changes(self):
        """Accepts changes to the parameter."""
        raise NotImplementedError

    def revert_changes(self):
        """Reverts changes made by the user and applies the
        previous parameter again."""
        raise NotImplementedError

    def modified(self):
        """Informs the :class:`.MainWindow` that there are unsaved changes."""
        pass
        self.window().block_item.modified()


class FloatParameterWidget(BaseParameterWidget, QtWidgets.QLineEdit):
    """Widget to display a :class:`.FloatParameter` ."""

    def __init__(self, parameter):
        """Initializes FloatParameterWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.textChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = float(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))

    def check_changed(self):
        try:
            value = float(self.text())
            self.parameter.validate(value)
        except (ValueError, exceptions.MCAError) as e:
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid red;")
            self.changed = True
            return
        if self.parameter.value != float(self.text()):
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = float(self.text())
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        if self.changed:
            self.setText(str(self.prev_value))
            self.setStyleSheet("")
            self.write_parameter()
            self.read_parameter()
            self.changed = False


class IntParameterWidget(BaseParameterWidget, QtWidgets.QLineEdit):
    """Widget to display an :class:`.IntParameter` ."""

    def __init__(self, parameter):
        """Initializes IntParameterWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.textChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = int(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))

    def check_changed(self):
        try:
            value = int(self.text())
            self.parameter.validate(value)
        except (ValueError, exceptions.MCAError) as e:
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid red;")
            self.changed = True
            return
        if self.parameter.value != int(self.text()):
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = int(self.text())
        self.setStyleSheet("")
        self.changed = False
        self.modified()

    def revert_changes(self):
        if self.changed:
            self.setText(str(self.prev_value))
            self.write_parameter()
            self.read_parameter()
            self.changed = False


class ChoiceParameterWidget(BaseParameterWidget, QtWidgets.QComboBox):
    """Widget to display a :class:`.ChoiceParameter` ."""

    def __init__(self, parameter):
        """Initializes ChoiceParameterWidget class."""
        QtWidgets.QComboBox.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.currentIndexChanged.connect(self.check_changed)
        # Prevents the last item to expand in dark mode
        delegate = QtWidgets.QStyledItemDelegate()
        self.setItemDelegate(delegate)

        for i in range(len(self.parameter.choices)):
            self.addItem(_(self.parameter.choices[i][1]),
                         userData=self.parameter.choices[i][0])

    def write_parameter(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        if self.changed:
            self.parameter.value = data

    def read_parameter(self):
        for i in range(len(self.parameter.choices)):
            if self.parameter.choices[i][0] == self.parameter.value:
                self.setCurrentText(self.parameter.choices[i][1])

    def check_changed(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        if self.parameter.value != data:
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        self.prev_value = data
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        if self.changed:
            index = self.findData(self.prev_value)
            self.setCurrentIndex(index)
            self.setStyleSheet("")
            self.write_parameter()
            self.read_parameter()
            self.changed = False


class StringParameterWidget(BaseParameterWidget, QtWidgets.QLineEdit):
    """Widget to display a :class:`.StringParameter` ."""

    def __init__(self, parameter):
        """Initializes StringParameterWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseParameterWidget.__init__(self, parameter)
        self.textChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = self.text()

    def read_parameter(self):
        self.setText(self.parameter.value)

    def check_changed(self):
        if self.parameter.value != self.text():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = self.text()
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        if self.changed:
            self.setText(self.prev_value)
            self.setStyleSheet("")
            self.write_parameter()
            self.read_parameter()
            self.changed = False


class BoolParameterWidget(BaseParameterWidget, QtWidgets.QCheckBox):
    """Widget to display a :class:`.BoolParameter` ."""

    def __init__(self, parameter):
        """Initializes BoolParameterWidget class."""
        QtWidgets.QCheckBox.__init__(self, parameter.name)
        BaseParameterWidget.__init__(self, parameter)
        self.stateChanged.connect(self.check_changed)

    def write_parameter(self):
        if self.changed:
            self.parameter.value = self.isChecked()

    def read_parameter(self):
        self.setChecked(self.parameter.value)

    def check_changed(self):
        if self.parameter.value != self.isChecked():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = self.isChecked()
        self.changed = False
        self.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        if self.changed:
            self.setChecked(self.prev_value)
            self.setStyleSheet("")
            self.write_parameter()
            self.read_parameter()
            self.changed = False


class ActionParameterWidget(BaseParameterWidget, QtWidgets.QPushButton):
    """Widget to display :class:`.ActionParameter`."""

    def __init__(self, parameter):
        self.parameter = parameter
        QtWidgets.QPushButton.__init__(self, _(self.parameter.name))
        BaseParameterWidget.__init__(self, parameter)
        self.pressed.connect(self.execute_function)

    def write_parameter(self):
        pass

    def read_parameter(self):
        pass

    def check_changed(self):
        pass

    def apply_changes(self):
        pass

    def revert_changes(self):
        pass

    def execute_function(self):
        """Executes the function of the parameter."""
        try:
            self.parameter.function()
        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self, _("MCA"), _("Could not apply action") + "\n" + repr(error),
                QtWidgets.QMessageBox.Ok)


class FileParameterWidget(BaseParameterWidget, QtWidgets.QWidget):
    """Combination of widgets to display :class:`PathParameter`. The file path
    can be entered manually with the line edit or can be chosen via a file
    dialog window.
    """

    def __init__(self, parameter):
        """Initializes FileParameterWidget class."""
        QtWidgets.QWidget.__init__(self)
        self.button = QtWidgets.QPushButton(text="...")
        self.file_edit = QtWidgets.QLineEdit()

        BaseParameterWidget.__init__(self, parameter)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self.file_edit)
        self.file_edit.setText(self.parameter.value)
        self.file_edit.textChanged.connect(self.check_changed)
        if self.parameter.file_formats:
            self.file_edit.setToolTip("File has to be " +
                                      " or ".join(self.parameter.file_formats))
        self.button.setMaximumWidth(30)
        self.layout().addWidget(self.button)
        dir_path = ""

        if self.parameter.value:
            dir_path = os.path.dirname(os.path.realpath(self.parameter.value))
        self.file_dialog = QtWidgets.QFileDialog()
        if self.parameter.file_formats:
            file_formats = "(*" + " *".join(self.parameter.file_formats) + ")"
            self.file_dialog.setNameFilter(file_formats)
        if self.parameter.loading:
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        else:
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        if dir_path:
            self.file_dialog.setDirectory(dir_path)
        self.button.clicked.connect(self.open_file_dialog)

    def write_parameter(self):
        self.parameter.value = self.file_edit.text()

    def read_parameter(self):
        self.file_edit.setText(self.parameter.value)

    def check_changed(self):
        try:
            self.parameter.validate(self.file_edit.text())
        except exceptions.ParameterTypeError:
            self.file_edit.setStyleSheet("border-radius: 3px;"
                                         "border: 2px solid red;")
            self.changed = True
            return
        if self.parameter.value != self.file_edit.text():
            self.changed = True
            self.file_edit.setStyleSheet("border-radius: 3px;"
                                         "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.file_edit.setStyleSheet("")

    def apply_changes(self):
        self.prev_value = self.file_edit.text()
        self.changed = False
        self.file_edit.setStyleSheet("")
        self.modified()

    def revert_changes(self):
        if self.changed:
            self.file_edit.setText(self.prev_value)
            self.file_edit.setStyleSheet("")
            self.write_parameter()
            self.read_parameter()
            self.changed = False

    def setFixedHeight(self, h):
        """Sets the button and the line edit at a fixed height."""
        self.button.setFixedHeight(h)
        self.file_edit.setFixedHeight(h)

    def open_file_dialog(self):
        """Opens the file dialog window and puts the chosen file into the
        line edit.
        """
        if self.file_dialog.exec_():
            self.file_edit.setText(self.file_dialog.selectedFiles()[0])


class MetaDataEditWidget(QtWidgets.QLineEdit):
    """Widget to display attributes of metadata objects.

    Attributes:
        metadata: Reference of the :class:`.MetaData` object.
        attr(str): Attribute name of the :class:`.MetaData` object.
        prev_value: Stores the last value of the attribute until changes get
                    finally applied.
        changed (bool): Indicates whether the current value in the widget
                        differs from the previous value.
    """

    def __init__(self, metadata, attr):
        """Initializes MetaDataEditWidget class.

        Args:
            metadata: Reference of the :class:`.MetaData` object.
            attr(str): Attribute name of the :class:`.MetaData` object.
        """
        QtWidgets.QLineEdit.__init__(self)
        self.metadata = metadata
        self.attr = attr
        self.changed = False
        self.prev_value = getattr(self.metadata, self.attr)
        self.textChanged.connect(self.check_changed)
        self.setFixedHeight(25)

    def write_attribute(self):
        """Writes the value from the widget to the attribute."""
        if self.changed:
            setattr(self.metadata, self.attr, self.text())

    def read_attribute(self):
        """Reads the value from the attribute and sets the widget text
        to it.
        """
        attr = getattr(self.metadata, self.attr)
        if isinstance(attr, Unit):
            attr = repr(attr)
        self.setText(attr)

    def check_changed(self):
        """Checks whether the value has been changed compared to the
        previous value.
        """
        attr = getattr(self.metadata, self.attr)
        if isinstance(attr, Unit):
            attr = repr(attr)
        if attr != self.text():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        """Accepts changes to the attribute."""
        self.changed = False
        self.prev_value = getattr(self.metadata, self.attr)
        self.setStyleSheet("")
        self.window().block_item.modified()

    def revert_changes(self):
        """Reverts changes made by the user and applies the
        previous attribute again.
        """
        if self.changed:
            attr = self.prev_value
            if isinstance(attr, Unit):
                attr = repr(attr)
            self.setText(attr)
            self.setStyleSheet("")
            self.write_attribute()
            self.read_attribute()
            self.changed = False


class MetaDataBoolWidget(QtWidgets.QCheckBox):
    """Widget to confirm whether predefined metadata from the output should
    be applied to the signal by manipulating bool values from the output.

    Attributes:
        text: Text to be displayed next to the checkbox.
        output: Reference of the :class:`.Output` object.
        attr(str): Attribute name of the :class:`.Output` object.
        prev_value: Stores the last value of the attribute until changes get
                    finally applied.
        changed (bool): Indicates whether the current value in the widget
                        differs from the previous value.
    """

    def __init__(self, text, output, attr):
        """Initializes MetaDataEditWidget class.

        Args:
            text: Text to be displayed next to the checkbox.
            output: Reference of the :class:`.MetaData` object.
            attr(str): Attribute name of the :class:`.MetaData` object.
        """
        QtWidgets.QCheckBox.__init__(self, text)
        self.output = output
        self.attr = attr
        self.changed = False
        self.prev_value = getattr(self.output, self.attr)
        self.stateChanged.connect(self.check_changed)
        self.setFixedHeight(25)

    def write_attribute(self):
        """Writes the value from the widget to the attribute."""
        if self.changed:
            setattr(self.output, self.attr, self.isChecked())

    def read_attribute(self):
        """Reads the value from the attribute and sets the widget value
        to it.
        """
        attr = getattr(self.output, self.attr)
        self.setChecked(attr)

    def check_changed(self):
        """Checks whether the value has been changed compared to the
        previous value.
        """
        attr = getattr(self.output, self.attr)
        if attr != self.isChecked():
            self.changed = True
            self.setStyleSheet("border-radius: 3px;"
                               "border: 2px solid lightblue;")
        else:
            self.changed = False
            self.setStyleSheet("")

    def apply_changes(self):
        """Accepts changes to the attribute."""
        self.changed = False
        self.prev_value = getattr(self.output, self.attr)
        self.setStyleSheet("")
        self.window().block_item.modified()

    def revert_changes(self):
        """Reverts changes made by the user and applies the
        previous attribute again.
        """
        if self.changed:
            attr = self.prev_value
            self.setChecked(attr)
            self.setStyleSheet("")
            self.write_attribute()
            self.read_attribute()
            self.changed = False


class ParameterBlockChoiceWidget(QtWidgets.QComboBox):
    """Widget to display the choices for the parameter conversions and
    applying them.

    Attributes:
        parameter_block: Reference of the ParameterBlock.
        parameters_to_widgets (dict): Mapping of the parameter to the
                                     corresponding widgets.
    """

    def __init__(self, parameter_block, parameters_to_widgets):
        """Initializes ParameterBlockChoiceWidget.

        Args:
            parameter_block: Reference of the ParameterBlock.
            parameters_to_widgets (dict): Mapping of the parameter to the
                                         corresponding widgets.
        """
        QtWidgets.QComboBox.__init__(self)
        self.parameter_block = parameter_block
        self.parameters_to_widgets = parameters_to_widgets
        # Prevents the last item to expand in dark mode
        delegate = QtWidgets.QStyledItemDelegate()
        self.setItemDelegate(delegate)
        # Add the conversions to the ComboBox
        for index, conversion in enumerate(
                self.parameter_block.param_conversions):
            names = [parameter.name for parameter in conversion.main_parameters]
            self.addItem("/".join(names), userData=index)
        self.enable_parameter_widgets()
        self.currentIndexChanged.connect(self.change_conversion)

    def enable_parameter_widgets(self):
        """Enables and disables the parameter widgets depending on the
        current activated conversion.
        """
        current_conversion = self.parameter_block.param_conversions[
            self.parameter_block.conversion_index]
        for parameter in current_conversion.main_parameters:
            widget = self.parameters_to_widgets[parameter]
            widget.setEnabled(True)
        for parameter in current_conversion.sub_parameters:
            widget = self.parameters_to_widgets[parameter]
            widget.setEnabled(False)

    def change_conversion(self):
        """Change the conversion of the parameter block to the current selected
        conversion in the widget.
        """
        conversion_index = self.currentData()
        self.parameter_block.conversion_index = conversion_index
        self.enable_parameter_widgets()


class ParameterBlockWidget(QtWidgets.QGroupBox):
    """Widget to display :class:`.ParameterBlock`. Creates and arranges the
    widgets of its parameters similar to EditWindow.

    Attributes:
        parameter_block: Reference of the ParameterBlock.
        main_layout: Layout for this widget.
        parameters_to_widgets (dict): Mapping of the parameter to the
                                      corresponding widgets.
    """

    def __init__(self, parameter_block):
        """Initializes the ParameterBlockWidget.

        Args:
            parameter_block: Reference of the ParameterBlock.
        """
        self.parameter_block = parameter_block
        QtWidgets.QGroupBox.__init__(self, title=parameter_block.name)
        self.main_layout = QtWidgets.QGridLayout(self)
        self.parameters_to_widgets = {}
        # Create and arrange the parameter widgets
        for index, parameter in enumerate(
                self.parameter_block.parameters.values(), 1):
            if not isinstance(parameter, parameters.BoolParameter) and \
                    not isinstance(parameter, parameters.ActionParameter):
                name_label = QtWidgets.QLabel(parameter.name + ":")
                name_label.setFixedHeight(25)
                self.main_layout.addWidget(name_label, index, 0, 1, 1)
            widget = widget_dict[type(parameter)](parameter)
            self.parameters_to_widgets[parameter] = widget
            widget.read_parameter()
            self.main_layout.addWidget(widget, index, 1, 1, 1)
            if parameter.unit:
                unit_label = QtWidgets.QLabel(parameter.unit)
                self.main_layout.addWidget(unit_label, index, 2, 1, 1)
        # Add the choice widget
        if self.parameter_block.param_conversions:
            conversion_choice = ParameterBlockChoiceWidget(self.parameter_block,
                                                           self.parameters_to_widgets)
            self.main_layout.addWidget(conversion_choice, 0, 0, 1, 1)

    def write_parameter(self):
        for parameter in self.parameters_to_widgets.values():
            if parameter.isEnabled():
                parameter.write_parameter()
        self.read_parameter()

    def read_parameter(self):
        for parameter in self.parameters_to_widgets.values():
            parameter.read_parameter()

    def check_changed(self):
        for parameter in self.parameters_to_widgets.values():
            if parameter.isEnabled():
                parameter.check_changed()

    def apply_changes(self):
        for parameter in self.parameters_to_widgets.values():
            parameter.apply_changes()
        self.window().block_item.modified()

    def revert_changes(self):
        for parameter in self.parameters_to_widgets.values():
            parameter.revert_changes()


# Map parameters to widgets
widget_dict = {parameters.BoolParameter: BoolParameterWidget,
               parameters.IntParameter: IntParameterWidget,
               parameters.FloatParameter: FloatParameterWidget,
               parameters.ChoiceParameter: ChoiceParameterWidget,
               parameters.StrParameter: StringParameterWidget,
               parameters.ActionParameter: ActionParameterWidget,
               parameters.PathParameter: FileParameterWidget,
               parameters.ParameterBlock: ParameterBlockWidget}
