import json
import logging

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets

from mca import exceptions
from mca.framework import block_io, io_registry, data_types, parameters
from mca.language import _


class Block:
    """Basic Block class of the Multi Channel Analyzer.
    
    All specific Blocks must derive from this basic Block class.
    
    Attributes:
        inputs: List that contains all its :class:`.Input`.
        outputs: List that contains all its :class:`.Output`.
        parameters: List that contains all parameters.
        gui_data (dict): Holds GUI data. Data is separated in the keys
                         'save_data' and 'run_time_data'. 'save_data' is dumped
                         into the save file when saving the block structure
                         and 'run_time_data' holds data is only used while the
                         program is running.
    """
    icon_file = None
    tags = []

    def __init__(self, **kwargs):
        """Initializes the main Block class."""
        super().__init__()
        logging.info(f"Initializing {self.name}")
        self.inputs = []
        self.outputs = []
        self.parameters = {
            "name": parameters.StrParameter(name=_("Name"), max_length=35,
                                            default=self.name)}
        self.plot_parameters = {}
        self.gui_data = {"save_data": {}, "run_time_data": {}}
        self.setup_io()
        self.setup_parameters()
        self.read_kwargs(kwargs)

    def trigger_update(self):
        """Triggers an update from the block."""
        io_registry.Registry.invalidate_and_update(self)

    def read_kwargs(self, kwargs):
        """Writes keyword arguments into the parameters."""
        for key in kwargs:
            if key not in self.parameters:
                continue
            if isinstance(kwargs[key], dict):
                for sub_key in kwargs[key]:
                    self.parameters[key].parameters[sub_key].value = kwargs[key][sub_key]
            else:
                self.parameters[key].value = kwargs[key]

    def _process(self):
        """Processes data from Inputs and parameters.

        This method describes the behaviour of the Block on what to do with
        data. This usually refers to applying new data on Outputs, plotting
        Input data or saving Input data.
        """
        raise NotImplementedError

    def setup_parameters(self):
        """Sets up the parameters for a block."""
        raise NotImplementedError

    def setup_io(self):
        """Sets up the inputs and outputs of the block."""
        raise NotImplementedError

    def update(self):
        """Updates the data and the flags of the Outputs if all
        Inputs have valid data.
        """
        if (not self.inputs) or all(
                elem == True
                for elem in [input_.up_to_date for input_ in self.inputs]
        ):
            self._process()
            for output in self.outputs:
                output.up_to_date = True

    def disconnect_all(self):
        """Disconnects all Inputs and Outputs."""
        for i in self.inputs:
            i.disconnect()
        for o in self.outputs:
            o.disconnect()

    def new_output(self, metadata=None, metadata_input_dependent=True,
                   abscissa_metadata=False, ordinate_metadata=False,
                   name=None):
        """Creates and adds an new Output to the block. Used to create new
        Outputs in the initialization of a new block.

        Args:
            name (str): Name of the Output.
            metadata(:class:`.MetaData`): Metadata of the data.
            metadata_input_dependent (bool): True, if the :class:`.MetaData` of
                                              the Output can be dependent on the
                                              MetaData of any Input.
            abscissa_metadata (bool): True, if the abscissa metadata
                                       should be used when data gets assigned
                                       to the Output.
            ordinate_metadata (bool): True, if the ordinate metadata
                                       should be used when data gets assigned
                                       to this Output.


        .. see also::
            :class:`.DynamicBlock`
        """

        self.outputs.append(
            io_registry.Registry.add_node(
                block_io.Output(
                    self,
                    initial_metadata=metadata,
                    metadata_input_dependent=metadata_input_dependent,
                    abscissa_metadata=abscissa_metadata,
                    ordinate_metadata=ordinate_metadata,
                    name=name)
            )
        )

    def delete(self):
        """Removes its inputs and outputs from the registry and cleans up all
        internal references to allow the garbage collector to remove the object
        once all explicit references are deleted.
        """
        for input_ in self.inputs:
            input_.delete()
        for output in self.outputs:
            output.delete()
        self.gui_data = None
        for parameter in self.parameters.values():
            if isinstance(parameter, parameters.ActionParameter):
                parameter.function = None
        logging.info(f"Deleting {self}")

    def new_input(self, name=None):
        """Creates and adds an new Input to the block. Used to create new
        Inputs in the initialization of a new block.

        .. see also::
            :class:`.DynamicBlock`
        """
        self.inputs.append(
            io_registry.Registry.add_node(block_io.Input(self, name=name))
        )

    def all_inputs_empty(self):
        """Checks if all Inputs have no data and if that is the case
        the data of the Outputs will be set to None.

        Returns:
            bool: True if all Inputs contain no data.
        """
        no_data = all([input_.data is None for input_ in self.inputs])
        if no_data:
            for output in self.outputs:
                output.data = None
            return True
        else:
            return False

    def any_inputs_empty(self):
        """Checks if any Inputs have no data and if that is the case
        the data of the Outputs will be set to None.

        Returns:
            bool: True if all Inputs contain no data.
        """
        no_data = any([input_.data is None for input_ in self.inputs])
        if no_data:
            for output in self.outputs:
                output.data = None
            return True
        else:
            return False

    def save_output_data(self, output_index, file_name):
        """Saves the data of the output in a json-file. Currently only supports
        saving the data type :class:`.Signal`.

        Args:
            output_index (int): Index of the output which data should be saved.
            file_name (str): Name of the file with the full path.
                             Requires .json as file type.
        """
        if not self.outputs[output_index].data:
            raise exceptions.DataSavingError("Output has no data to save.")
        with open(file_name, 'w') as save_file:
            if isinstance(self.outputs[output_index].data, data_types.Signal):
                save_data = {"data_type": "Signal",
                             "name": self.outputs[
                                 output_index].data.metadata.name,
                             "quantity_a": self.outputs[
                                 output_index].data.metadata.quantity_a,
                             "symbol_a": self.outputs[
                                 output_index].data.metadata.symbol_a,
                             "unit_a": repr(self.outputs[
                                                output_index].data.metadata.unit_a),
                             "quantity_o": self.outputs[
                                 output_index].data.metadata.quantity_o,
                             "symbol_o": self.outputs[
                                 output_index].data.metadata.symbol_o,
                             "unit_o": repr(self.outputs[
                                                output_index].data.metadata.unit_o),
                             "abscissa_start": self.outputs[
                                 output_index].data.abscissa_start,
                             "values": self.outputs[output_index].data.values,
                             "increment": self.outputs[
                                 output_index].data.increment,
                             "ordinate": str(
                                 self.outputs[output_index].data.ordinate)}
                json.dump(save_data, save_file)


class DynamicBlock(Block):
    """Basic dynamic block class is the subclass of the
    :class:`.Block` class with the extension of adding and
    removing :class:`.Output`  and :class: `.Input` objects. Blocks with
    dynamic amount of Inputs or dynamic amount of Outputs need to inherit from
    this class. Furthermore it can be chosen between only the amount of Inputs
    being dynamic, only the amount of Outputs being dynamic or both. It is
    advised to overwrite the following methods in subclasses, if only specific
    classes of Inputs or Outputs should be added to the block or if further
    validation is needed.

    Attributes:
        dynamic_output: (lower_limit, upper_limit) The upper limit and
            lower limit of the amount of outputs. The lower limit is an
            integer and for it applies: lower limit >= 0.
            The upper limit is an integer and
            for it applies: upper limit > lower limit. The upper limit can also
            be set to None meaning there is no finite upper limit.
            By default dynamic_output is set to None meaning the amount of
            Outputs are not dynamic and no Outputs can be added or removed
            after the initialization.

        dynamic_input: (lower_limit, upper_limit) The upper limit and
            lower limit of the amount of Inputs. The lower limit is an
            integer and for it applies: lower limit >= 0. The upper limit
            is an integer and for it applies: upper limit > lower limit.
            The upper limit can also be set to None meaning there is no
            finite upper limit. By default dynamic_input is set to None
            meaning the amount of Inputs are not dynamic and no Inputs can
            be added or removed after the initialization.

            Examples:
                >>> self.dynamic_output = None
                No Outputs can be added or removed
                >>> self.dynamic_input = (0, 5)
                The amount of Inputs can vary between 0 and 5
                >>> self.dynamic_output = (3, None)
                There are at least 3 Outputs and any amount of Outputs
                can be added

    """

    def __init__(self, **kwargs):
        """Initialize DynamicBlock class."""
        self.dynamic_output = None
        self.dynamic_input = None
        super().__init__(**kwargs)

    def add_input(self, input_):
        """Adds an Input to the Block.

        Args:
            input_: Input instance added to the block.
        Raises:
            :class:`.InputOutputError`: If adding the Input was not successful.
        """
        if input_ in io_registry.Registry._graph.nodes:
            raise exceptions.DynamicIOError("Input already added")
        if not self.dynamic_input:
            raise exceptions.DynamicIOError("No permission to create Input")

        if self.dynamic_input[1]:
            if self.dynamic_input[1] <= len(self.inputs):
                raise exceptions.DynamicIOError("Maximum Inputs reached")
            self.inputs.append(io_registry.Registry.add_node(input_))
        else:
            self.inputs.append(io_registry.Registry.add_node(input_))

    def add_output(self, output):
        """Adds an Output to the Block.

        Args:
            output: Output instance added to the block.
        Raises:
            :class:`.InputOutputError`: If adding the Output was not successful.
        """
        if output in io_registry.Registry._graph.nodes:
            raise exceptions.DynamicIOError("Output already added")
        if not self.dynamic_output:
            raise exceptions.DynamicIOError("No permission to create Output")
        if self.dynamic_output[1]:
            if self.dynamic_output[1] <= len(self.outputs):
                raise exceptions.DynamicIOError("Maximum Outputs reached")
            self.outputs.append(io_registry.Registry.add_node(output))
        else:
            self.outputs.append(io_registry.Registry.add_node(output))
        self._process()

    def delete_input(self, input_index):
        """Removes an Input from the Block.

        Args:
            input_index: Index of the Input in the list called inputs.
        Raises:
            :class:`.InputOutputError`: If the lower limit of the Inputs is
                reached or dynamic_input is set to None.
        """
        if not self.dynamic_input:
            raise exceptions.DynamicIOError("No permission to delete Input")
        if self.dynamic_input[0] >= len(self.inputs):
            raise exceptions.DynamicIOError("Minimum Inputs reached")
        io_registry.Registry.remove_input(self.inputs.pop(input_index))

    def delete_output(self, output_index):
        """Removes an Output from the Block.

        Args:
            output_index: Index of the Output in the list called outputs.
        Raises:
            :class:`.InputOutputError`: If the lower limit of the Outputs is
                reached or dynamic_output is set to None.
        """
        if not self.dynamic_output:
            raise exceptions.DynamicIOError("No permission to delete Output")
        if self.dynamic_output[0] >= len(self.outputs):
            raise exceptions.DynamicIOError("Minimum Outputs reached")
        io_registry.Registry.remove_output(self.outputs.pop(output_index))

    def _process(self):
        raise NotImplementedError

    def setup_io(self):
        raise NotImplementedError

    def setup_parameters(self):
        raise NotImplementedError


class PlotBlock(Block):
    """Base class for plot class. All plot blocks should inherit from this
    class. It uses the QT5 backend of matplotlib and the plot figure will be
    embedded in the PySide2 GUI.

    Attributes:
        plot_window: Qt widget containing the figure.
        axes(:py:class:`numpy.ndarray` or :obj:`matplotlib.axis.Axis`):
            Depending on the number of rows and cols it is either a single
            axis or an array of axes.
        fig(:obj:`matplotlib.figure`): Matplotlib figure object.
    """
    def __init__(self, rows, cols, **kwargs):
        """Initialize PlotBlock.

        Args:
            rows (int): Number of cols in the figure.
            cols (int): Number of cols in the figure.
        """

        super().__init__(**kwargs)
        self.setup_plot_parameters()
        self.plot_window = PlotWindow(rows, cols)
        self.axes = self.plot_window.axes
        self.fig = self.plot_window.canvas.fig

    def show(self):
        self.plot_window.show()

    def _process(self):
        raise NotImplementedError

    def setup_io(self):
        raise NotImplementedError

    def setup_parameters(self):
        raise NotImplementedError

    def setup_plot_parameters(self):
        pass


class MplCanvas(FigureCanvasQTAgg):
    """MatplotlibCanvas holding the figure object.

    Attributes:
        fig(:obj:`matplotlib.figure`): Matplotlib figure object.
    """
    def __init__(self, width=5, height=4, dpi=100):
        """Initialize MplCanvas.

        Args:
            width: Width of the figure.
            height: Height of the figure.
            dpi: DPI of the figure.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)


class PlotWindow(QtWidgets.QWidget):
    """Qt widget containing the :obj:`matplotlib.figure`.

    Attributes:
        canvas: Matplotlib canvas containing the figure.
        axes: Axes within the figure.
    """
    def __init__(self, rows, cols, **kwargs):
        """Initialize PlotWindow.

        Args:
            rows (int): Number of cols in the figure.
            cols (int): Number of cols in the figure.
        """
        super(PlotWindow, self).__init__(**kwargs)

        self.canvas = MplCanvas(width=5, height=4, dpi=100)

        toolbar = NavigationToolbar(self.canvas, parent=self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(widget)
        self.axes = self.canvas.fig.subplots(nrows=rows, ncols=cols)

    def paintEvent(self, event):
        if self.style().objectName() == "qdarkstyle":
            fig_colour = "#60798B"
            ax_colour = "#9DA9B5"
            grid_colour = "white"
        else:
            fig_colour = "white"
            ax_colour = "white"
            grid_colour = "black"
        self.canvas.fig.set_facecolor(fig_colour)
        try:
            for ax in self.axes:
                ax.set_facecolor(ax_colour)
                ax.grid(color=grid_colour)
        except TypeError:
            self.axes.set_facecolor(ax_colour)
            self.axes.grid(color=grid_colour)
        super().paintEvent(event)
