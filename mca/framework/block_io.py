from . import block_registry


class Input:
    """Basic Input class.
    
    Instances of Input are linked to Blocks which can be connected 
    to an :class:`.Output` containing the data.
    
    Attributes:
        name (str): Name of the Input.
        block (:class:`.Block`): Block to which the Input belongs to.
        up_to_date (bool): Flag which indicates if the data of the Input is
            valid or needs to be updated.
    """

    def __init__(self, block=None, name=None):
        """Initializes the Input class.
        
        Args:
            name (str): Name of the Input.
            block (:class:`.Block`): Block to which the Input belongs to.
        """
        self.name = name
        self.up_to_date = True
        self.block = block

    def connect(self, output):
        """Connects the Input to an Output and updates the data.
        
        Args:
            output (Output): Output to which the Input wants to connect to.
        """
        block_registry.Registry.connect(output, self)

    def disconnect(self):
        """Disconnects the Input from its Output, if it is connected 
        to any Output and updates the data.
        """
        block_registry.Registry.disconnect_input(self)

    @property
    def data(self):
        """Data retrieved from the connected Output."""
        if block_registry.Registry.get_output(self):
            return block_registry.Registry.get_output(self).data


class Output:
    """Basic Output class.

    Instances of Output are linked to Blocks which get connected
    to :class:`.Input` containing the data.

    Attributes:
        name (str): Name of the Output.
        block (:class:`.Block`): Block to which the Output belongs to.
        up_to_date (bool): Flag which indicates if the data of the Output is
            valid or needs to be updated.
        data: Data which the Output may contain.
        meta_data: Metadata for data.
    """

    def __init__(self, block, meta_data, name=None):
        """Initializes Output class.

        Args:
            name (str): Name of the Output.
            block: Block to which the Output belongs to.
            meta_data: Metadata for data.
        """
        self.name = name
        self.block = block
        self.up_to_date = True
        self.data = None
        self.meta_data = meta_data

    def disconnect(self):
        """Disconnects itself from all Inputs."""
        block_registry.Registry.disconnect_output(self)