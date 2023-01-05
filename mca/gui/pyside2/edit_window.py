import logging
import os

from PySide2 import QtWidgets, QtCore, QtGui

import mca
from mca.framework import parameters, DynamicBlock, PlotBlock
from mca.gui.pyside2 import edit_widgets
from mca.language import _


class EditWindow(QtWidgets.QDialog):
    """Window to display the parameter and metadata of a :class:`.Block`.

    Attributes:
        block: Reference of the :class:`.Block` instance.
        main_layout: Arranges the tab widget und the buttons.
        parameter_box_layout: Grid layout which arranges the parameter widgets.
        parameter_widgets (list): Contains references to all parameter widgets.
        metadata_layout: Vertical layout which arranges the metadata group
                          boxes.
        metadata_widgets (list): Contains references to all metadata widgets.
        tab_widget: Widget containing the tabs 'general' and 'metadata'.
        warning_message: Dialogue window which pops up when errors occur during
                         editing.
        button_box: "Apply|Cancel|Ok" button widgets.

    """

    def __init__(self, block_item, block):
        """Initialize EditWindow class.

        Args:
            block: Reference of the :class:`.Block` instance.
        """
        QtWidgets.QDialog.__init__(self)
        self.block = block
        self.block_item = block_item
        self.resize(600, 750)
        self.setMinimumSize((QtCore.QSize(500, 400)))
        self.setWindowTitle(
            _("Edit {}").format(self.block.parameters["name"].value))

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.parameter_widgets = []
        self.metadata_widgets = []

        self.tab_widget = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        # Initialize general tab
        general_tab = QtWidgets.QWidget()
        general_tab_layout = QtWidgets.QGridLayout(general_tab)
        general_tab_contents = QtWidgets.QWidget()
        general_tab_contents_layout = QtWidgets.QVBoxLayout(
            general_tab_contents)
        description_box = QtWidgets.QGroupBox(_("Description"))
        description_box_layout = QtWidgets.QVBoxLayout(description_box)
        description_label = QtWidgets.QLabel(self.block.description)
        description_label.setMaximumHeight(100)
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
        # Initialize metadata tab
        self.metadata_layout = None
        self.metadata_tab = None
        self.metadata_contents = None
        self.metadata_contents_layout = None
        # Add tab if block has outputs or is dynamic concerning outputs
        if self.block.outputs or (isinstance(self.block, DynamicBlock) and
                                  self.block.dynamic_output):
            self.metadata_contents = QtWidgets.QWidget()
            self.metadata_contents_layout = QtWidgets.QVBoxLayout(
                self.metadata_contents)
            self.metadata_tab = QtWidgets.QWidget()
            self.metadata_layout = QtWidgets.QVBoxLayout(self.metadata_tab)

            scroll = QtWidgets.QScrollArea()
            scroll.setWidget(self.metadata_contents)
            scroll.setWidgetResizable(True)

            self.metadata_layout.addWidget(scroll)
            self.tab_widget.addTab(self.metadata_tab, _("Metadata"))

            info_box = QtWidgets.QGroupBox(_("Info"))
            info_layout = QtWidgets.QVBoxLayout(info_box)
            info_label = QtWidgets.QLabel(
                _("Redefine the metadata for the "
                  "outgoing signals. By default metadata is computed "
                  "depending on the input metadata. In order to apply your "
                  "own defined metadata tick the corresponding boxes "
                  "'Use ordinate/abscissa metadata' below."))
            info_label.setMaximumHeight(100)
            info_label.setWordWrap(True)
            info_layout.addWidget(info_label)

            self.metadata_contents_layout.addWidget(info_box)
            self.add_metadata()
            self.metadata_contents_layout.addItem(QtWidgets.QSpacerItem(
                0, 0,
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Expanding))

        self.plot_parameter_layout = None
        self.plot_parameter_tab = None
        self.plot_parameter_contents = None
        self.plot_parameter_contents_layout = None
        self.plot_parameter_widgets = []

        if isinstance(self.block, PlotBlock):
            self.plot_parameter_contents = QtWidgets.QWidget()
            self.plot_parameter_contents_layout = QtWidgets.QVBoxLayout(
                self.plot_parameter_contents)
            self.plot_parameter_tab = QtWidgets.QWidget()
            self.plot_parameter_layout = QtWidgets.QVBoxLayout(self.plot_parameter_tab)

            scroll = QtWidgets.QScrollArea()
            scroll.setWidget(self.plot_parameter_contents)
            scroll.setWidgetResizable(True)

            self.plot_parameter_layout.addWidget(scroll)
            self.tab_widget.addTab(self.plot_parameter_tab, _("Plot options"))

            self.add_plot_parameters()
            self.plot_parameter_contents_layout.addItem(QtWidgets.QSpacerItem(
                0, 0,
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Expanding))
        # Set buttons
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setGeometry(QtCore.QRect(140, 360, 329, 23))
        self.button_box.setContentsMargins(0, 0, 10, 10)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok
                                           | QtWidgets.QDialogButtonBox.Cancel
                                           | QtWidgets.QDialogButtonBox.Apply)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText(_("Ok"))
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText(
            _("Cancel"))
        self.button_box.button(QtWidgets.QDialogButtonBox.Apply).setText(
            _("Apply"))
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.clicked.connect(self.apply)
        self.main_layout.addWidget(self.button_box)
        # Set custom window icon
        if self.block.icon_file:
            icon = QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + self.block.icon_file)
            self.setWindowIcon(icon)
        # Create warning message
        self.warning_message = QtWidgets.QMessageBox()
        self.warning_message.setWindowTitle(_("MCA"))
        self.warning_message.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_message.setText(
            _("Could not apply the changed parameters and metadata!"
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
        # Iterate over the parameters and add them row wise to the edit window
        for index, block_parameter in enumerate(block_parameters):
            # Skip if the parameter is not meant to be displayed here
            if hasattr(block_parameter, "display_options") and \
                    "edit_window" not in block_parameter.display_options:
                continue
            # Add name labels except for action and bool parameters and
            # parameter blocks
            if not isinstance(block_parameter, parameters.BoolParameter) and \
                    not isinstance(block_parameter,
                                   parameters.ActionParameter) and \
                    not isinstance(block_parameter, parameters.ParameterBlock):
                name_label = QtWidgets.QLabel(block_parameter.name + ":")
                name_label.setFixedHeight(25)
                self.parameter_box_layout.addWidget(name_label, index, 0, 1, 1)
            # Translate parameter to the corresponding widget
            widget = edit_widgets.widget_dict[type(block_parameter)](
                block_parameter)
            self.parameter_widgets.append(widget)
            widget.read_parameter()
            # Add widgets to the layout though parameters blocks
            # take two columns
            if isinstance(block_parameter, parameters.ParameterBlock):
                self.parameter_box_layout.addWidget(widget, index, 0, 1, 2)
            else:
                self.parameter_box_layout.addWidget(widget, index, 1, 1, 1)
            # Add the unit to the parameter
            if hasattr(block_parameter, "unit"):
                unit_label = QtWidgets.QLabel(block_parameter.unit)
                self.parameter_box_layout.addWidget(unit_label, index, 2, 1, 1)

    def add_metadata(self):
        """Arranges the metadata of the outputs of the block in the window."""
        for i in reversed(range(1, self.metadata_contents_layout.count())):
            self.metadata_layout.itemAt(i).widget().setParent(None)
        self.metadata_widgets = []
        for output_index, output in enumerate(self.block.outputs):
            if output.name:
                metadata_box = QtWidgets.QGroupBox(
                    _("Output '{}' metadata:").format(output.name))
            else:
                metadata_box = QtWidgets.QGroupBox(
                    _("Output {} metadata:").format(output_index))
            metadata_box_layout = QtWidgets.QFormLayout(metadata_box)
            label_attributes = ((_("Signal name:"), "name"),
                                (_("Abscissa quantity:"), "quantity_a"),
                                (_("Abscissa symbol:"), "symbol_a"),
                                (_("Abscissa unit:"), "unit_a"),
                                (_("Ordinate quantity:"), "quantity_o"),
                                (_("Ordinate symbol:"), "symbol_o"),
                                (_("Ordinate unit:"), "unit_o"))
            for label, attribute in label_attributes:
                entry_edit_line = edit_widgets.MetaDataEditWidget(
                    metadata=output.metadata, attr=attribute
                )
                entry_edit_line.read_attribute()
                entry_edit_line.setMaximumHeight(25)
                self.metadata_widgets.append(entry_edit_line)
                metadata_box_layout.addRow(label, entry_edit_line)
            abscissa_check_box = edit_widgets.MetaDataBoolWidget(
                _("Use abscissa metadata"), output, "abscissa_metadata")
            abscissa_check_box.read_attribute()
            if not output.metadata_input_dependent:
                abscissa_check_box.setEnabled(False)
            self.metadata_widgets.append(abscissa_check_box)
            metadata_box_layout.insertRow(4, "", abscissa_check_box)
            ordinate_check_box = edit_widgets.MetaDataBoolWidget(
                _("Use ordinate metadata"), output, "ordinate_metadata")
            ordinate_check_box.read_attribute()
            if not output.metadata_input_dependent:
                ordinate_check_box.setEnabled(False)
            self.metadata_widgets.append(ordinate_check_box)
            metadata_box_layout.insertRow(8, "", ordinate_check_box)
            self.metadata_contents_layout.addWidget(metadata_box)

    def add_plot_parameters(self):
        """Arranges plot parameters of a block in rows in the window underneath
        each other. One row includes the name of the parameter as a label, the
        desired widget and the unit if given.
        """
        plot_parameters = self.block.plot_parameters.values()
        plot_parameter_box = QtWidgets.QGroupBox(_("Plot options"))
        plot_parameter_box_layout = QtWidgets.QGridLayout(plot_parameter_box)
        # Iterate over the parameters and add them row wise to the edit window
        for index, plot_parameter in enumerate(plot_parameters):
            # Add name labels except for action and bool parameters and
            # parameter blocks
            if not isinstance(plot_parameter, parameters.BoolParameter) and \
                    not isinstance(plot_parameter,
                                   parameters.ActionParameter) and \
                    not isinstance(plot_parameter, parameters.ParameterBlock):
                name_label = QtWidgets.QLabel(plot_parameter.name + ":")
                name_label.setFixedHeight(25)
                plot_parameter_box_layout.addWidget(name_label, index, 0, 1, 1)
            # Translate parameter to the corresponding widget
            widget = edit_widgets.widget_dict[type(plot_parameter)](
                plot_parameter)
            self.plot_parameter_widgets.append(widget)
            widget.read_parameter()
            plot_parameter_box_layout.addWidget(widget, index, 1, 1, 1)
            self.plot_parameter_contents_layout.addWidget(plot_parameter_box)

    def accept(self):
        """Applies changes to all parameters and closes the window."""
        self.apply_changes()
        super(EditWindow, self).accept()

    def apply_changes(self, parameter_changes=True, metadata_changes=True,
                      plot_parameter_changes=True):
        """Tries to apply changes. In case of an error the user gets a
        notification and can choose between reverting his last changes or
        continue editing and potentially fix the error.

        Args:
            parameter_changes (bool): True, if changes to the parameters
                                      should be applied.
            metadata_changes (bool): True, if changes to the metadata should
                                      be applied
            plot_parameter_changes (bool): True, if changes to the
                                           plot_parameters should be applied.
        """
        try:
            if parameter_changes:
                for parameter_widget in self.parameter_widgets:
                    parameter_widget.write_parameter()
            if metadata_changes:
                for entry in self.metadata_widgets:
                    entry.write_attribute()
            if plot_parameter_changes:
                for plot_parameter in self.plot_parameter_widgets:
                    plot_parameter.write_parameter()
            self.block.trigger_update()
            self.block_item.update()
        except Exception as error:
            if error.args:
                logging.error(error.args)
                self.warning_message.setText(
                    _("Could not apply the changed parameters and metadata!"
                      "Continue editing or revert changes?") +
                    "\n" + _("Error message: ") + error.args[0])
            else:
                self.warning_message.setText(
                    _("Could not apply the changed parameters and metadata!"
                      "Continue editing or revert changes?"))
            self.warning_message.exec_()
            if self.warning_message.clickedButton() == self.warning_message.revert_button:
                self.revert_changes()
        else:
            if parameter_changes:
                for parameter_widget in self.parameter_widgets:
                    parameter_widget.apply_changes()
            if metadata_changes:
                for entry in self.metadata_widgets:
                    entry.apply_changes()

    def revert_changes(self):
        """Revert the last changes made."""
        for parameter_widget in self.parameter_widgets:
            parameter_widget.revert_changes()
        for entry in self.metadata_widgets:
            entry.revert_changes()
        self.block.trigger_update()

    def reject(self):
        """Reverts all not applied changes and closes the window."""
        self.revert_changes()
        super(EditWindow, self).reject()

    def closeEvent(self, e):
        """Event triggered when the window get closed."""
        self.apply_changes()
        super(EditWindow, self).closeEvent(e)

    def show(self):
        """Opens the window and reloads the metadata tab if the block is a
        dynamic block.
        """
        if isinstance(self.block, DynamicBlock) and self.block.dynamic_output:
            self.add_metadata()
        self.setWindowTitle(_("Edit {}").format(
            self.block.parameters["name"].value)
        )
        super(EditWindow, self).show()

    def apply(self, button):
        """Apply all changes made in the EditWindow. This is a helper function
        and effectively only calls apply_changes.
        """
        if self.button_box.buttonRole(
                button) == QtWidgets.QDialogButtonBox.ApplyRole:
            self.apply_changes()
