import uuid

from mca.framework import block_registry, data_types


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
        """Connects the Input to an Output and trigger an update.
        
        Args:
            output (Output): Output to which the Input gets connected.
        """
        block_registry.Registry.connect(output, self)

    def disconnect(self):
        """Disconnects the Input from its Output if it is connected
        to any Output. Triggers an update.
        """
        block_registry.Registry.disconnect_input(self)

    @property
    def data(self):
        """Returns data retrieved from the connected Output."""
        if self.connected_output:
            return self.connected_output.data

    @property
    def connected_output(self):
        """Convenience method to get the current connected Output.

        Returns:
            output (Output): If the Input is connected, the output is returned.
        """
        return block_registry.Registry.get_output(self)


class Output:
    """Basic Output class.

    Instances of Output are linked to Blocks which get connected
    to :class:`.Input` containing the data.

    Attributes:
        name (str): Name of the Output.
        block (:class:`.Block`): Block to which the Output belongs to.
        up_to_date (bool): Flag which indicates if the data of the Output is
            valid or needs to be updated.
        data: Data which the Output contains.
        abscissa_meta_data (bool): True, if the abscissa meta data
                                   should be used when data gets assigned
                                   to this output.
        ordinate_meta_data (bool): True, if the ordinate meta data
                                   should be used when data gets assigned
                                   to this output.
        meta_data: Metadata for data.
        id: Used to identify the inputs which were connected to the output
            after saving.
    """

    def __init__(self, block=None, meta_data=None, name=None,
                 meta_data_input_dependent=True, abscissa_meta_data=False,
                 ordinate_meta_data=False):
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
        self.abscissa_meta_data = abscissa_meta_data
        self.ordinate_meta_data = ordinate_meta_data
        self.meta_data_input_dependent = meta_data_input_dependent
        self.meta_data = meta_data
        self.id = uuid.uuid4()

    def get_meta_data(self, external_meta_data):
        """Returns a meta data object as a mix of given external meta data and
        internal meta data depending on the attributes abscissa_meta_data
        and ordinate_meta_data. Setting abscissa_meta_data to True forces the
        use of the internal abscissa meta data. Same goes for
        ordinate_meta_data. The meta data attribute "name" is always inherited
        by the internal meta data.

        Args:
            external_meta_data: Given external meta_data from the processing
                                method.
        """
        if self.abscissa_meta_data:
            unit_a = self.meta_data.unit_a
            symbol_a = self.meta_data.symbol_a
            quantity_a = self.meta_data.quantity_a
        else:
            unit_a = external_meta_data.unit_a
            symbol_a = external_meta_data.symbol_a
            quantity_a = external_meta_data.quantity_a

        if self.ordinate_meta_data:
            unit_o = self.meta_data.unit_o
            symbol_o = self.meta_data.symbol_o
            quantity_o = self.meta_data.quantity_o
        else:
            unit_o = external_meta_data.unit_o
            symbol_o = external_meta_data.symbol_o
            quantity_o = external_meta_data.quantity_o
        return data_types.MetaData(name=self.meta_data.name,
                                   unit_a=unit_a,
                                   unit_o=unit_o,
                                   symbol_a=symbol_a,
                                   symbol_o=symbol_o,
                                   quantity_a=quantity_a,
                                   quantity_o=quantity_o)

    def disconnect(self):
        """Disconnects itself from all Inputs."""
        block_registry.Registry.disconnect_output(self)
