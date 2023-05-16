import os.path

import dsch
from dsch import schema

from mca import exceptions
from mca.framework import Block, data_types, parameters


class SignalSaver(Block):
    """Saves the input signal in a .npz, .mat or .hdf5 file."""
    name = "SignalSaver"
    description = "Saves the input signal in a .npz, .mat, .hdf5 file."
    tags = ("Saving",)

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters["file_name"] = parameters.PathParameter(
            name="Filename", file_formats=(".npz", ".mat", ".hdf5")
        )
        self.parameters["save"] = parameters.ActionParameter(
            name="Save", function=self.save_data,
            display_options=("edit_window", "block_button")
        )

    def process(self):
        pass

    def save_data(self):
        """Saves the input data in .npz, .mat, or .hdf5 file."""
        # Raise error when the input has no data to save
        if self.all_inputs_empty():
            raise exceptions.DataSavingError("No data to save.")
        # Read the input data
        signal = self.inputs[0].data
        # Read the input metadata
        metadata = self.inputs[0].metadata
        # Read parameters values
        filename = self.parameters["file_name"].value
        # Remove file to create a new storage
        if os.path.exists(filename):
            os.remove(filename)
        # Create dsch storage to save the data
        storage = dsch.create(
            storage_path=filename,
            schema_node=data_types.signal_schema
        )
        # Write the signal parameters
        storage.data.signal.abscissa_start.value = signal.abscissa_start
        storage.data.signal.values.value = signal.values
        storage.data.signal.increment.value = signal.increment
        storage.data.signal.ordinate.value = signal.ordinate
        # Write the metadata parameters
        storage.data.metadata.name.value = metadata.name
        storage.data.metadata.abscissa_unit.value = repr(metadata.unit_a)
        storage.data.metadata.abscissa_symbol.value = metadata.symbol_a
        storage.data.metadata.abscissa_quantity.value = metadata.quantity_a
        storage.data.metadata.ordinate_unit.value = repr(metadata.unit_o)
        storage.data.metadata.ordinate_symbol.value = metadata.symbol_o
        storage.data.metadata.ordinate_quantity.value = metadata.quantity_o
        # Save the data
        storage.save()
