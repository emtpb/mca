import logging

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets, QtGui

from mca import exceptions
from mca.framework import block_io, io_registry, parameters
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
        logging.info(f"Initializing {self}")
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

    def process(self):
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
        if (not self.inputs) or all(elem == True
                for elem in [input_.up_to_date for input_ in self.inputs]):
            self.process()
            for output in self.outputs:
                output.up_to_date = True

    def disconnect_all(self):
        """Disconnects all Inputs and Outputs."""
        for i in self.inputs:
            i.disconnect()
        for o in self.outputs:
            o.disconnect()

    def new_output(self, metadata=None, user_metadata_required=False,
                   name=None):
        """Creates and adds a new Output to the block. Used to create new
        Outputs when initializing a block.

        Args:
            name (str): Name of the Output.
            metadata(:class:`.MetaData`): Metadata of the data.
            user_metadata_required (bool): True, if user_metadata is forced to be
                                           used to set the metadata for Output.


        .. see also::
            :class:`.DynamicBlock`
        """

        self.outputs.append(
            io_registry.Registry.add_node(
                block_io.Output(
                    self,
                    initial_metadata=metadata,
                    user_metadata_required=user_metadata_required,
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
        """Checks if all Inputs have no data.

        Returns:
            bool: True if all Inputs contain no data.
        """
        no_data = all([input_.data is None for input_ in self.inputs])
        return no_data

    def any_inputs_empty(self):
        """Checks if any Input has no data and if that is the case
        the data of the Outputs will be set to None.

        Returns:
            bool: True if all Inputs contain no data.
        """
        no_data = any([input_.data is None for input_ in self.inputs])
        return no_data


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
        logging.info(f"Adding input to {self}")
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
        logging.info(f"Adding output to {self}")
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
        self.process()

    def delete_input(self, input_index):
        """Removes an Input from the Block.

        Args:
            input_index: Index of the Input in the list called inputs.
        Raises:
            :class:`.InputOutputError`: If the lower limit of the Inputs is
                reached or dynamic_input is set to None.
        """
        logging.info(f"Deleting input from {self}")
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
        logging.info(f"Deleting output from {self}")
        if not self.dynamic_output:
            raise exceptions.DynamicIOError("No permission to delete Output")
        if self.dynamic_output[0] >= len(self.outputs):
            raise exceptions.DynamicIOError("Minimum Outputs reached")
        io_registry.Registry.remove_output(self.outputs.pop(output_index))

    def process(self):
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

    @property
    def label_color(self):
        """Get color the labels of the plot should have.

        Returns:
            str: Color of the label as hexadecimal.
        """
        return self.plot_window.palette().color(
            QtGui.QPalette.Text).name()

    def set_ylabel(self, axis, unit, quantity=None, symbol=None, **kwargs):
        """Wrapper method for calling axis.set_ylabel. The label is not set
        directly, but rather get constructed based on the symbol, quantity
        and the unit of the metadata. This wrapper also sets the color
        depending on the theme.

        Args:
            axis: Axis to set the y-label of.
            unit: Unit for the y-label.
            symbol: Symbol for the y-label.
            quantity: Quantity for the y-label.
        """
        if symbol and quantity:
            label = "{} {} / {}".format(quantity, symbol, unit)
        elif symbol:
            label = "{} / {}".format(symbol, unit)
        elif quantity:
            label = "{} in {}".format(quantity, unit)
        else:
            label = repr(unit)
        axis.set_ylabel(label, color=self.label_color, **kwargs)

    def set_xlabel(self, axis, unit, quantity=None, symbol=None, **kwargs):
        """Wrapper method for calling axis.set_xlabel. The label is not set
        directly, but rather get constructed based on the symbol, quantity
        and the unit of the metadata. This wrapper also sets the color
        depending on the theme.

        Args:
            axis: Axis to set the y-label of.
            unit: Unit for the y-label.
            symbol: Symbol for the y-label.
            quantity: Quantity for the y-label.
        """
        if symbol and quantity:
            label = "{} {} / {}".format(quantity, symbol, unit)
        elif symbol:
            label = "{} / {}".format(symbol, unit)
        elif quantity:
            label = "{} in {}".format(quantity, unit)
        else:
            label = repr(unit)
        axis.set_xlabel(label, color=self.label_color, **kwargs)

    def show(self):
        self.plot_window.show()

    def process(self):
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
        # Get colors depending on the style
        fig_colour = self.palette().color(QtGui.QPalette.Base).name()
        ax_colour = self.palette().color(QtGui.QPalette.Window).name()
        grid_colour = self.palette().color(QtGui.QPalette.Text).name()
        # Apply the colors to the figure and the axes
        self.canvas.fig.set_facecolor(fig_colour)

        try:
            for ax in self.axes:
                ax.set_facecolor(ax_colour)
                ax.grid(color=grid_colour)
                ax.tick_params(colors=grid_colour)
                ax.xaxis.label.set_color(grid_colour)
                ax.yaxis.label.set_color(grid_colour)
        except TypeError:
            self.axes.tick_params(colors=grid_colour)
            self.axes.xaxis.label.set_color(grid_colour)
            self.axes.yaxis.label.set_color(grid_colour)
            self.axes.set_facecolor(ax_colour)
            self.axes.grid(color=grid_colour)

        super().paintEvent(event)
