import logging
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
        logging.info(f"Connecting {self.block}  to {output.block}")
        io_registry.Registry.connect(output, self)

    def disconnect(self):
        """Disconnects the Input from its Output if it is connected
        to any Output. Triggers an update.
        """
        if self.connected_output:
            logging.info(f"Disconnecting {self.block} from "
                         f"{self.connected_output.block}")
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

    def delete(self):
        self.block = None
        io_registry.Registry.remove_input(self)


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
        metadata_input_dependent (bool): True, if the MetaData of
                                          the Output can be dependent on the
                                          MetaData of any Input.
        abscissa_metadata (bool): True, if the abscissa
                                   should be used when data gets assigned
                                   to the Output.
        ordinate_metadata (bool): True, if the ordinate
                                   should be used when data gets assigned
                                   to this Output.
        metadata: MetaData of the attribute data.
        id: Used to identify the Inputs which were connected to the Output
            after saving.
    """

    def __init__(self, block=None, metadata=None, name=None,
                 metadata_input_dependent=True, abscissa_metadata=False,
                 ordinate_metadata=False):
        """Initializes Output class.

        Args:
            block: Block to which the Output belongs to.
            name (str): Name of the Output.
            metadata: Metadata of the data.
            metadata_input_dependent (bool): True, if the :class:`.MetaData` of
                                              the Output can be dependent on the
                                              MetaData of any Input.
            abscissa_metadata (bool): True, if the abscissa metadata
                                       should be used when data gets assigned
                                       to the Output.
            ordinate_metadata (bool): True, if the ordinate metadata
                                       should be used when data gets assigned
                                       to this Output.
        """
        self.name = name
        self.block = block
        self.up_to_date = True
        self.data = None
        self.metadata_input_dependent = metadata_input_dependent
        self.abscissa_metadata = abscissa_metadata
        self.ordinate_metadata = ordinate_metadata
        if metadata is None:
            self.metadata = data_types.default_metadata()
        else:
            self.metadata = metadata
        self.id = uuid.uuid4()

    def get_metadata(self, external_metadata):
        """Returns a MetaData object as a mix of given external meta
        data and internal metadata depending on the attributes
        abscissa_metadata and ordinate_metadata. Setting abscissa_metadata
        to True forces the use of the internal abscissa metadata. Same goes for
        ordinate_metadata. The metadata attribute "name" is always inherited
        by the internal metadata.

        Args:
            external_metadata: Given external metadata.
        """
        if self.abscissa_metadata:
            unit_a = self.metadata.unit_a
            symbol_a = self.metadata.symbol_a
            quantity_a = self.metadata.quantity_a
            fixed_unit_a = True
        else:
            unit_a = external_metadata.unit_a
            symbol_a = ""
            quantity_a = external_metadata.quantity_a
            fixed_unit_a = False

        if self.ordinate_metadata:
            unit_o = self.metadata.unit_o
            symbol_o = self.metadata.symbol_o
            quantity_o = self.metadata.quantity_o
            fixed_unit_o = True
        else:
            unit_o = external_metadata.unit_o
            symbol_o = ""
            quantity_o = external_metadata.quantity_o
            fixed_unit_o = False

        return data_types.MetaData(name=self.metadata.name,
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
        logging.info(f"Disconnecting {self.block} from all inputs.")
        io_registry.Registry.disconnect_output(self)

    def delete(self):
        self.block = None
        io_registry.Registry.remove_output(self)
