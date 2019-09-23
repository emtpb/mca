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
        meta_data: Metadata for data.
    """

    def __init__(self, block, name=None, meta_data=None):
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
