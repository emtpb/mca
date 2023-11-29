import dsch

from mca.framework import Block, data_types, parameters


class SignalLoader(Block):
    """Loads a signal from a file (previously saved by the SignalSaver)."""
    name = "Signal Loader"
    description = "Loads a signal from a file " \
                  "(previously saved by the SignalSaver)."
    tags = ("Generating", "Loading")

    def setup_io(self):
        self.new_output()

    def setup_parameters(self):
        self.parameters["file_name"] = parameters.PathParameter(
                name="Filename",
                loading=True,
                file_formats=[".npz", ".mat", ".hdf5"]
        )
        self.parameters["load_file"] = parameters.ActionParameter(
                name="Load file",
                function=self.load_file
        )

    def process(self):
        pass

    def load_file(self):
        """Loads a signal from a file (previously saved by the SignalSaver)."""
        # Read parameters values
        file_name = self.parameters["file_name"].value

        storage = dsch.load(
            storage_path=file_name,
            required_schema=data_types.signal_schema
        )
        # Apply loaded signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=storage.data.signal.abscissa_start.value,
            values=storage.data.signal.values.value,
            increment=storage.data.signal.increment.value,
            ordinate=storage.data.signal.ordinate.value
        )

        # Apply metadata from the loaded signal
        self.outputs[0].process_metadata = data_types.MetaData(
                    name=storage.data.metadata.name.value,
                    unit_a=storage.data.metadata.abscissa_unit.value,
                    unit_o=storage.data.metadata.ordinate_unit.value,
                    quantity_a=storage.data.metadata.abscissa_quantity.value,
                    quantity_o=storage.data.metadata.ordinate_quantity.value,
                    symbol_a=storage.data.metadata.abscissa_symbol.value,
                    symbol_o=storage.data.metadata.ordinate_symbol.value,
        )

        # Trigger an update manually since this is not executed within process
        self.trigger_update()
