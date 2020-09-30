import json
from . import block_io, block_registry, data_types
from mca import exceptions
from . import parameters
from mca.language import _


class Block:
    """Basic Block class of the Multi Channel Analyzer.
    
    All specific Blocks must derive from this basic Block class.
    
    Attributes:
        inputs: List that contains all its :class:`.Input`.
        outputs: List that contains all its :class:`.Output`.
        parameters: List that contains all parameters.
    """
    icon_file = None
    tags = []

    def __init__(self):
        """Initializes the main Block class."""
        self.inputs = []
        self.outputs = []
        self.parameters = {
            "name": parameters.StrParameter(_("Name"), max_length=35,
                                            value=self.name)}
        self.gui_data = {"save_data": {}, "run_time_data": {}}

    def apply_parameter_changes(self):
        """Applies all changes to the parameters and triggers an update."""
        block_registry.Registry.invalidate_and_update(self)

    def read_kwargs(self, kwargs):
        """Writes keyword arguments into the parameters."""
        for key in kwargs:
            self.parameters[key].validate(kwargs[key])
            self.parameters[key].value = kwargs[key]

    def _process(self):
        """Processes data from the Inputs and the parameters and puts new
        data to the outputs.
        """
        raise NotImplementedError

    def update_my_block(self):
        """Updates the data and the flags of the Outputs if all
        Inputs have valid data."""
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

    def _new_output(self, meta_data, name=None):
        """Creates and adds an new output to the block. Used to create new
        Outputs in the initialization of a new block.

        .. see also::
            :class:`.DynamicBlock`
        """

        self.outputs.append(
            block_registry.Registry.add_node(
                block_io.Output(self, meta_data=meta_data, name=name)
            )
        )

    def _new_input(self, name=None):
        """Creates and adds an new Input to the block. Used to create new
        Inputs in the initialization of a new block.
        
        .. warning:: Never call this method after a block instance has been
            initialized.
        .. see also::
            :class:`.DynamicBlock`
        """
        self.inputs.append(
            block_registry.Registry.add_node(block_io.Input(self, name=name))
        )

    def check_empty_inputs(self):
        """Checks if Inputs have any data and if that is not the case
        the data of the Outputs will be set to None.

        Returns:
            bool: True if all Inputs contain no data.
        """
        no_data = all([input_.data is None for input_ in self.inputs])
        if no_data:
            for output in self.outputs:
                output.data = None
            return True

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
                                 output_index].data.meta_data.name,
                             "quantity_a": self.outputs[
                                 output_index].data.meta_data.quantity_a,
                             "symbol_a": self.outputs[
                                 output_index].data.meta_data.symbol_a,
                             "unit_a": repr(self.outputs[
                                 output_index].data.meta_data.unit_a),
                             "quantity_o": self.outputs[
                                 output_index].data.meta_data.quantity_o,
                             "symbol_o": self.outputs[
                                 output_index].data.meta_data.symbol_o,
                             "unit_o": repr(self.outputs[
                                 output_index].data.meta_data.unit_o),
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
    removing :class:`.Output` s and :class:`.Input` s. Further Blocks with
    dynamic amount of Inputs or dynamic amount of outputs need to inherit from
    this class. Furthermore it can be chosen between only the amount of Inputs
    being dynamic, only the amount of Outputs being dynamic or both. It is
    advised to overwrite the following methods in subclasses, if only specific
    classes of Inputs or outputs should be added to the block or if further
    validation is needed.

    Attributes:
        dynamic_output: (lower limit, upper limit) The upper limit and
            lower limit of the amount of outputs. The lower limit is an
            integer and for it applies: lower limit >= 0.
            The upper limit is an integer and
            for it applies: upper limit > lower limit. The upper limit can also
            be set to None meaning there is no finite upper limit.
            By default dynamic_output is set to None meaning the amount of
            Outputs are not dynamic and no Outputs can be added or removed
            after the initialization.

        dynamic_input: (lower limit, upper limit) The upper limit and
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

    def __init__(self):
        """Initialize DynamicBlock class."""
        super().__init__()
        self.dynamic_output = None
        self.dynamic_input = None

    def add_input(self, input_):
        """Adds an Input to the Block.

        Args:
            input_: Input instance added to the block.
        Raises:
            :class:`.InputOutputError`: If adding the Input was not successful
        """
        if input_ in block_registry.Registry._graph.nodes:
            raise exceptions.InputOutputError("Input already added")
        if not self.dynamic_input:
            raise exceptions.InputOutputError("No permission to create Input")

        if self.dynamic_input[1]:
            if self.dynamic_input[1] <= len(self.inputs):
                raise exceptions.InputOutputError("Maximum Inputs reached")
            self.inputs.append(block_registry.Registry.add_node(input_))
        else:
            self.inputs.append(block_registry.Registry.add_node(input_))

    def add_output(self, output):
        """Adds an Output to the Block.

        Args:
            output: Output instance added to the block.
        Raises:
            :class:`.InputOutputError`: If adding the Output was not successful
        """
        if output in block_registry.Registry._graph.nodes:
            raise exceptions.InputOutputError("Output already added")
        if not self.dynamic_output:
            raise exceptions.InputOutputError("No permission to create Output")
        if self.dynamic_output[1]:
            if self.dynamic_output[1] <= len(self.outputs):
                raise exceptions.InputOutputError("Maximum Outputs reached")
            self.outputs.append(block_registry.Registry.add_node(output))
        else:
            self.outputs.append(block_registry.Registry.add_node(output))
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
            raise exceptions.InputOutputError("No permission to delete Input")
        if self.dynamic_input[0] >= len(self.inputs):
            raise exceptions.InputOutputError("Minimum Inputs reached")
        block_registry.Registry.remove_input(self.inputs.pop(input_index))

    def delete_output(self, output_index):
        """Removes an Output from the Block.

        Args:
            output_index: Index of the Output in the list called outputs.
        Raises:
            :class:`.InputOutputError`: If the lower limit of the Outputs is
                reached or dynamic_output is set to None.
        """
        if not self.dynamic_output:
            raise exceptions.InputOutputError("No permission to delete Output")
        if self.dynamic_output[0] >= len(self.outputs):
            raise exceptions.InputOutputError("Minimum Outputs reached")
        block_registry.Registry.remove_output(self.outputs.pop(output_index))

    def _process(self):
        """Processes data from the Inputs and the parameters and put new
        data to the outputs.
        """
        raise NotImplementedError
