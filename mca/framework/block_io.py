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
    def metadata(self):
        """Returns metadata retrieved from the connected Output."""
        if self.connected_output:
            return self.connected_output.metadata

    @property
    def connected_output(self):
        """Convenience method to get the current connected Output.

        Returns:
            output (Output): If the Input is connected, the output is returned.
        """
        return io_registry.Registry.get_output(self)

    def delete(self):
        """Removes itself from the registry and removes its reference of
        its block.
        """
        self.block = None
        io_registry.Registry.remove_input(self)
        logging.info(f"Deleting {self}")


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
        user_metadata_required (bool): True, if user_metadata is forced to be
                                       used to set the metadata for Output.
        use_process_abscissa_metadata (bool): Flag whether the process
                                              abscissa metadata or the user
                                              metadata should be used.
        use_process_ordinate_metadata (bool): Flag whether the process
                                              ordinate metadata or the user
                                              metadata should be used.
        initial_metadata: MetaData of the attribute data.
        id: Used to identify the Inputs which were connected to the Output
            after saving.
    """

    def __init__(self, block=None, initial_metadata=None, name=None,
                 user_metadata_required=False):
        """Initializes Output class.

        Args:
            block: Block to which the Output belongs to.
            name (str): Name of the Output.
            initial_metadata: Metadata of the data.
            user_metadata_required (bool): True, if user_metadata is forced to
                                           be used to set the metadata for
                                           Output.
        """
        self.name = name
        self.block = block
        self.up_to_date = True
        self.data = None
        self.user_metadata_required = user_metadata_required

        if user_metadata_required:
            self.use_process_abscissa_metadata = False
            self.use_process_ordinate_metadata = False
        else:
            self.use_process_abscissa_metadata = True
            self.use_process_ordinate_metadata = True

        if initial_metadata is None:
            self.user_metadata = data_types.default_metadata()
        else:
            self.user_metadata = initial_metadata

        self.process_metadata = None

        self.id = uuid.uuid4()

    @property
    def metadata(self):
        """Get the currently used metadata of the Output.

        An Output owns two types of metadata.

        1. user_metadata: Static metadata which is part of the Output and can be
                          modified by the user.
        2. process_metadata: Dynamic metadata which is calculated in the Block
                             process method.

        Depending on the use_process_abscissa_metadata and
        use_process_ordinate_metadata flags one of those two metadatas is
        returned.

        The name of the user_metadata is taken by default.
        """
        if self.use_process_abscissa_metadata and self.process_metadata is not None:
            unit_a = self.process_metadata.unit_a
            symbol_a = ""
            quantity_a = self.process_metadata.quantity_a
            fixed_unit_a = False
        else:
            unit_a = self.user_metadata.unit_a
            symbol_a = self.user_metadata.symbol_a
            quantity_a = self.user_metadata.quantity_a
            fixed_unit_a = True

        if self.use_process_ordinate_metadata and self.process_metadata is not None:
            unit_o = self.process_metadata.unit_o
            symbol_o = ""
            quantity_o = self.process_metadata.quantity_o
            fixed_unit_o = False
        else:
            unit_o = self.user_metadata.unit_o
            symbol_o = self.user_metadata.symbol_o
            quantity_o = self.user_metadata.quantity_o
            fixed_unit_o = True

        return data_types.MetaData(name=self.user_metadata.name,
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
        """Removes itself from the registry and removes its reference of
        its block.
        """
        self.block = None
        io_registry.Registry.remove_output(self)
        logging.info(f"Deleting {self}")
