from . import block_registry


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
    """

    def __init__(self, block, name=None):
        """Initializes Output class.
        
        Args:
            name (str): Name of the Output.
            block: Block to which the Output belongs to.
        """
        self.name = name
        self.block = block
        self.up_to_date = True
        self.data = None

    def disconnect(self):
        """Disconnects itself from all Inputs."""
        block_registry.Registry.disconnect_output(self)
