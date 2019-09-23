from . import block_registry
from . import output_base
from . import input_base


class Block:
    """Basic Block class of the Multi Channel Analyzer.
    
    All specific Blocks must derive from this basic Block class.
    
    Attributes:
        name (str): Name of the Block.
        inputs: List that contains all its :class:`.Input`.
        outputs: List that conatins all its :class:`.Output`.
        parameters: List that contains all parameters.
    """

    def __init__(self):
        """Initialize the main Block class."""

        self.inputs = []
        self.outputs = []
        self.parameters = {}

    def apply_parameter_changes(self):
        """Applies all changes to the parameters and triggers an update."""
        block_registry.Registry.invalidate_and_update(self)

    def read_kwargs(self, kwargs):
        """Writes keyword arguments into the parameters."""
        for key in kwargs:
            self.parameters[key].validate(kwargs[key])
            self.parameters[key].value = kwargs[key]

    def _process(self):
        """Processes data from the inputs and the parameters and puts new
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

    def _new_output(self, meta_data):
        """Creates and adds an new output to the block. Used to create new
        outputs in the initialization of a new block. 
        
        .. warning:: Never call this method after a block instance has been
            initialized.
        .. see also::
            :class:`.DynamicBlock`
        """

        self.outputs.append(
            block_registry.Registry.add_node(
                output_base.Output(self, meta_data=meta_data)
            )
        )

    def _new_input(self):
        """Creates and adds an new input to the block. Used to create new
        inputs in the initialization of a new block.
        
        .. warning:: Never call this method after a block instance has been
            initialized.
        .. see also::
            :class:`.DynamicBlock`
        """
        self.inputs.append(
            block_registry.Registry.add_node(input_base.Input(self))
        )
