import json
import logging
import sys

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
        gui_data (dict): Holds GUI data. Data is separated in in the keys
                         'save_data' and 'run_time_data'. 'save_data' is dumped
                         into the save file when saving the block structure
                         and 'run_time_data' holds data is only used while the
                         program is running.
    """
    icon_file = None
    tags = []

    def __init__(self, **kwargs):
        """Initializes the main Block class."""
        logging.info(f"Initializing {self.name}")
        self.inputs = []
        self.outputs = []
        self.parameters = {
            "name": parameters.StrParameter(name=_("Name"), max_length=35,
                                            default=self.name)}
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
            if isinstance(kwargs[key], dict):
                for sub_key in kwargs[key]:
                    self.parameters[key].parameters[sub_key].value = \
                    kwargs[key][sub_key]
            else:
                self.parameters[key].value = kwargs[key]

    def _process(self):
        """Processes data from the Inputs and the parameters and puts new
        data to the outputs.
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
                    metadata=metadata,
                    metadata_input_dependent=metadata_input_dependent,
                    abscissa_metadata=abscissa_metadata,
                    ordinate_metadata=ordinate_metadata,
                    name=name)
            )
        )

    def delete(self):
        for input_ in self.inputs:
            input_.delete()
        for output in self.outputs:
            output.delete()
        self.gui_data = None
        for parameter in self.parameters.values():
            if isinstance(parameter, parameters.ActionParameter):
                parameter.function = None

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

    def __init__(self):
        """Initialize DynamicBlock class."""
        self.dynamic_output = None
        self.dynamic_input = None
        super().__init__()

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
        """Processes data from the Inputs and the parameters and put new
        data to the outputs.
        """
        raise NotImplementedError
