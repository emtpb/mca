from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.framework import parameters, DynamicBlock
from mca.gui.pyside2 import edit_widgets
from mca.language import _

widget_dict = {parameters.BoolParameter: edit_widgets.BoolParameterWidget,
               parameters.IntParameter: edit_widgets.IntParameterWidget,
               parameters.FloatParameter: edit_widgets.FloatParameterWidget,
               parameters.ChoiceParameter: edit_widgets.ChoiceParameterWidget,
               parameters.StrParameter: edit_widgets.StringParameterWidget,
               parameters.ActionParameter: edit_widgets.ActionParameterWidget,
               parameters.PathParameter: edit_widgets.FileParameterWidget}


class EditWindow(QtWidgets.QDialog):
    """Window to display the parameter and meta data of a :class:`.Block`.

    Attributes:
        block: Reference of the :class:`.Block` instance.
        main_layout: Arranges the tab widget und the buttons.
        parameter_box_layout: Grid layout which arranges the parameter widgets.
        parameter_widgets (list): Contains references to all parameter widgets.
        meta_data_layout: Vertical layout which arranges the meta data group
                          boxes.
        meta_data_widgets (list): Contains references to all meta data widgets.
        tab_widget: Widget containing the tabs 'general' and 'meta data'.
        warning_message: Dialogue window which pops up when errors occur during
                         editing.
        button_box: "Ok|Cancel" button widgets.

    """
    def __init__(self, parent, block):
        """Initialize EditWindow class.

        Args:
            block: Reference of the :class:`.Block` instance.
        """
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.block = block
        self.resize(500, 550)
        self.setMinimumSize((QtCore.QSize(500, 400)))
        self.setWindowTitle(_("Edit {}").format(self.block.parameters["name"].value))

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.parameter_widgets = []
        self.meta_data_widgets = []

        self.tab_widget = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        # Initialize general tab
        general_tab = QtWidgets.QWidget()
        general_tab_layout = QtWidgets.QGridLayout(general_tab)
        general_tab_contents = QtWidgets.QWidget()
        general_tab_contents_layout = QtWidgets.QVBoxLayout(general_tab_contents)
        description_box = QtWidgets.QGroupBox(_("Description"))
        description_box_layout = QtWidgets.QVBoxLayout(description_box)
        description_label = QtWidgets.QLabel(self.block.description)
        description_label.setMaximumHeight(60)
        description_label.setWordWrap(True)
        description_box_layout.addWidget(description_label)
        general_tab_contents_layout.addWidget(description_box)

        self.parameter_box = QtWidgets.QGroupBox(_("Parameters"))
        self.parameter_box_layout = QtWidgets.QGridLayout(self.parameter_box)
        general_tab_contents_layout.addWidget(self.parameter_box)
        general_tab_contents_layout.addItem(QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding))

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(general_tab_contents)
        scroll.setWidgetResizable(True)
        general_tab_layout.addWidget(scroll, 0, 0, 1, 1)
        self.tab_widget.addTab(general_tab, _("General"))
        self.add_parameters()
        # Initialize meta data tab
        self.meta_data_layout = None
        if self.block.outputs or (isinstance(self.block, DynamicBlock) and
                                  self.block.dynamic_output):
            self.meta_data_layout = QtWidgets.QVBoxLayout()
            scroll = QtWidgets.QScrollArea()
            scroll.setLayout(self.meta_data_layout)
            scroll.setWidgetResizable(True)
            self.tab_widget.addTab(scroll, _("Meta data"))
            self.add_meta_data()
        # Set buttons
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setGeometry(QtCore.QRect(140, 360, 329, 23))
        self.button_box.setContentsMargins(0, 0, 10, 10)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok
                                           | QtWidgets.QDialogButtonBox.Cancel
                                           | QtWidgets.QDialogButtonBox.Apply)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText(_("Ok"))
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText(_("Cancel"))
        self.button_box.button(QtWidgets.QDialogButtonBox.Apply).setText(_("Apply"))
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.clicked.connect(self.test)
        self.main_layout.addWidget(self.button_box)
        # Set custom window icon
        if self.block.icon_file:
            icon = QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + self.block.icon_file)
            self.setWindowIcon(icon)
        # Create warning message
        self.warning_message = QtWidgets.QMessageBox()
        self.warning_message.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_message.setText(
            _("Could not apply the changed parameters and meta data!"
              "Continue editing or revert changes?"))
        self.warning_message.continue_button = self.warning_message.addButton(
            _("Continue"),
            QtWidgets.QMessageBox.YesRole)
        self.warning_message.revert_button = self.warning_message.addButton(
            _("Revert"),
            QtWidgets.QMessageBox.NoRole)

    def add_parameters(self):
        """Arranges parameters of a block in rows in the window underneath each
        other. One row includes the name of the parameter as a label, the
        desired widget and the unit if given.
        """
        block_parameters = self.block.parameters.values()

        for block_parameter, index in zip(block_parameters,
                                          range(0, len(block_parameters))):
            if not isinstance(block_parameter, parameters.BoolParameter) and \
               not isinstance(block_parameter, parameters.ActionParameter):
                name_label = QtWidgets.QLabel(block_parameter.name + ":")
                name_label.setFixedHeight(25)
                self.parameter_box_layout.addWidget(name_label, index, 0, 1, 1)
            widget = widget_dict[type(block_parameter)](block_parameter, self)
            widget.setFixedHeight(25)
            self.parameter_widgets.append(widget)
            widget.read_parameter()
            self.parameter_box_layout.addWidget(widget, index, 1, 1, 1)
            if block_parameter.unit:
                unit_label = QtWidgets.QLabel(block_parameter.unit)
                self.parameter_box_layout.addWidget(unit_label, index, 2, 1, 1)

    def add_meta_data(self):
        """Arranges the meta data of the outputs of the block in the window."""
        for i in reversed(range(self.meta_data_layout.count())):
            self.meta_data_layout.itemAt(i).widget().setParent(None)
        self.meta_data_widgets = []
        for output_index, output in enumerate(self.block.outputs):
            if output.name:
                meta_data_box = QtWidgets.QGroupBox(
                    _("Output '{}' meta data:").format(output.name))
            else:
                meta_data_box = QtWidgets.QGroupBox(
                    _("Output {} meta data:").format(output_index))
            meta_data_box_layout = QtWidgets.QFormLayout(meta_data_box)
            label_attributes = ((_("Signal name:"), "name"),
                                (_("Abscissa quantity:"), "quantity_a"),
                                (_("Abscissa symbol:"), "symbol_a"),
                                (_("Abscissa unit:"), "unit_a"),
                                (_("Ordinate quantity:"), "quantity_o"),
                                (_("Ordinate symbol:"), "symbol_o"),
                                (_("Ordinate unit:"), "unit_o"))
            for label, attribute in label_attributes:
                entry_edit_line = edit_widgets.MetaDataEditWidget(
                    meta_data=output.meta_data, attr=attribute
                )
                entry_edit_line.read_attribute()
                entry_edit_line.setMaximumHeight(25)
                self.meta_data_widgets.append(entry_edit_line)
                meta_data_box_layout.addRow(label, entry_edit_line)

            abscissa_check_box = edit_widgets.MetaDataBoolWidget(
                _("Use abscissa meta data"), output, "abscissa_meta_data")
            abscissa_check_box.read_attribute()
            if not output.meta_data_input_dependent:
                abscissa_check_box.setEnabled(False)
            self.meta_data_widgets.append(abscissa_check_box)
            meta_data_box_layout.insertRow(4, "", abscissa_check_box)
            
            ordinate_check_box = edit_widgets.MetaDataBoolWidget(
                _("Use ordinate meta data"), output, "ordinate_meta_data")
            ordinate_check_box.read_attribute()
            if not output.meta_data_input_dependent:
                ordinate_check_box.setEnabled(False)
            self.meta_data_widgets.append(ordinate_check_box)
            meta_data_box_layout.insertRow(8, "", ordinate_check_box)
            self.meta_data_layout.addWidget(meta_data_box)

    def accept(self):
        """Applies changes to all parameters and closes the window."""
        self.apply_changes()
        super(EditWindow, self).accept()

    def apply_changes(self, parameter_changes=True, meta_data_changes=True):
        """Tries to apply changes. In case of an error the user gets a
        notification and can choose between reverting his last changes or
        continue editing and potentially fix the error.

        Args:
            parameter_changes (bool): True, if changes to the parameter
                                      should be applied.
            meta_data_changes (bool): True, if changes to the meta_data should
                                      be applied
        """
        try:
            if parameter_changes:
                for parameter_widget in self.parameter_widgets:
                    parameter_widget.write_parameter()
            if meta_data_changes:
                for entry in self.meta_data_widgets:
                    entry.write_attribute()
            self.block.trigger_update()
        except Exception as error:
            if error.args:
                self.warning_message.setText(
                    _("Could not apply the changed parameters and meta data!"
                      "Continue editing or revert changes?") +
                    "\n" + _("Error message:") + error.args[0])
            else:
                self.warning_message.setText(
                    _("Could not apply the changed parameters and meta data!"
                      "Continue editing or revert changes?"))
            self.warning_message.exec_()
            if self.warning_message.clickedButton() == self.warning_message.revert_button:
                self.revert_changes()
        else:
            if parameter_changes:
                for parameter_widget in self.parameter_widgets:
                    parameter_widget.apply_changes()
            if meta_data_changes:
                for entry in self.meta_data_widgets:
                    entry.apply_changes()

    def revert_changes(self):
        """Revert the last changes made."""
        for parameter_widget in self.parameter_widgets:
            parameter_widget.revert_changes()
        for entry in self.meta_data_widgets:
            entry.revert_changes()
        self.block.trigger_update()

    def reject(self):
        """Reverts all not applied changes and closes the the window."""
        self.revert_changes()
        super(EditWindow, self).reject()

    def closeEvent(self, e):
        """Event triggered when the window get closed."""
        self.apply_changes()
        super(EditWindow, self).closeEvent(e)

    def show(self):
        """Opens the window and reloads the meta data tab if the block is a
        dynamic block.
        """
        if isinstance(self.block, DynamicBlock) and self.block.dynamic_output:
            self.add_meta_data()
        self.setWindowTitle(_("Edit {}").format(
            self.block.parameters["name"].value)
        )
        super(EditWindow, self).show()

    def test(self, button):
        if self.button_box.buttonRole(button) == QtWidgets.QDialogButtonBox.ApplyRole:
            self.apply_changes()
