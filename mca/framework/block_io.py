import uuid

from mca.framework import io_registry, data_types


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
        """Connects the Input to an Output and triggers an update.
        
        Args:
            output (Output): Output to which the Input gets connected.
        """
        io_registry.Registry.connect(output, self)

    def disconnect(self):
        """Disconnects the Input from its Output if it is connected
        to any Output. Triggers an update.
        """
        io_registry.Registry.disconnect_input(self)

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
        return io_registry.Registry.get_output(self)


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
        meta_data_input_dependent (bool): True, if the MetaData of
                                          the Output can be dependent on the
                                          MetaData of any Input.
        abscissa_meta_data (bool): True, if the abscissa meta data
                                   should be used when data gets assigned
                                   to the Output.
        ordinate_meta_data (bool): True, if the ordinate meta data
                                   should be used when data gets assigned
                                   to this Output.
        meta_data: MetaData of the attribute data.
        id: Used to identify the Inputs which were connected to the Output
            after saving.
    """

    def __init__(self, block=None, meta_data=None, name=None,
                 meta_data_input_dependent=True, abscissa_meta_data=False,
                 ordinate_meta_data=False):
        """Initializes Output class.

        Args:
            block: Block to which the Output belongs to.
            name (str): Name of the Output.
            meta_data: Meta data of the data.
            meta_data_input_dependent (bool): True, if the :class:`.MetaData` of
                                              the Output can be dependent on the
                                              MetaData of any Input.
            abscissa_meta_data (bool): True, if the abscissa meta data
                                       should be used when data gets assigned
                                       to the Output.
            ordinate_meta_data (bool): True, if the ordinate meta data
                                       should be used when data gets assigned
                                       to this Output.
        """
        self.name = name
        self.block = block
        self.up_to_date = True
        self.data = None
        self.meta_data_input_dependent = meta_data_input_dependent
        self.abscissa_meta_data = abscissa_meta_data
        self.ordinate_meta_data = ordinate_meta_data
        if meta_data is None:
            self.meta_data = data_types.default_meta_data()
        else:
            self.meta_data = meta_data
        self.id = uuid.uuid4()

    def get_meta_data(self, external_meta_data):
        """Returns a MetaData object as a mix of given external meta
        data and internal meta data depending on the attributes
        abscissa_meta_data and ordinate_meta_data. Setting abscissa_meta_data
        to True forces the use of the internal abscissa meta data. Same goes for
        ordinate_meta_data. The meta data attribute "name" is always inherited
        by the internal meta data.

        Args:
            external_meta_data: Given external meta data.
        """
        if self.abscissa_meta_data:
            unit_a = self.meta_data.unit_a
            symbol_a = self.meta_data.symbol_a
            quantity_a = self.meta_data.quantity_a
            fixed_unit_a = True
        else:
            unit_a = external_meta_data.unit_a
            symbol_a = ""
            quantity_a = external_meta_data.quantity_a
            fixed_unit_a = False

        if self.ordinate_meta_data:
            unit_o = self.meta_data.unit_o
            symbol_o = self.meta_data.symbol_o
            quantity_o = self.meta_data.quantity_o
            fixed_unit_o = True
        else:
            unit_o = external_meta_data.unit_o
            symbol_o = ""
            quantity_o = external_meta_data.quantity_o
            fixed_unit_o = False

        return data_types.MetaData(name=self.meta_data.name,
                                   unit_a=unit_a,
                                   unit_o=unit_o,
                                   symbol_a=symbol_a,
                                   symbol_o=symbol_o,
                                   quantity_a=quantity_a,
                                   quantity_o=quantity_o,
                                   fixed_unit_a=fixed_unit_a,
                                   fixed_unit_o=fixed_unit_o)

    def disconnect(self):
        """Disconnects itself from all Inputs."""
        io_registry.Registry.disconnect_output(self)
