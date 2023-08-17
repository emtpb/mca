import numpy as np

from mca.framework import Block, data_types, parameters, util


class Quantization(Block):
    """Quantizes the input signal by a given amount of bits. Returns optionally
    the raw bit values.
    """
    name = "Quantization"
    description = ("Quantizes the input signal by a given amount of bits. "
                   "Returns optionally the raw bit values.")
    tags = ("Processing",)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["bits"] = parameters.IntParameter(
            name="Bits", min_=1, default=10
        )
        self.parameters["max_value"] = parameters.FloatParameter(
            name="Max value", min_=0, default=1
        )
        self.parameters["signed"] = parameters.BoolParameter(
            name="Signed", default=True
        )
        self.parameters["raw"] = parameters.BoolParameter(
            name="Raw bits", default=False
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        bits = self.parameters["bits"].value
        max_value = self.parameters["max_value"].value
        signed = self.parameters["signed"].value
        raw = self.parameters["raw"].value
        # Calculate the ordinate
        if not signed:
            ordinate = input_signal.ordinate * (2 ** bits) / max_value
        else:
            ordinate = (input_signal.ordinate + max_value) * (2 ** bits - 1) / (
                        2 * max_value)
        ordinate = np.rint(ordinate)
        # Apply clipping
        pos_clipping_mask = ordinate > 2 ** bits - 1
        neg_clipping_mask = ordinate < 0
        ordinate = ~(
                    pos_clipping_mask | neg_clipping_mask) * ordinate + pos_clipping_mask * (
                               2 ** bits - 1)
        # Convert int values back to actual values
        if not raw:
            ordinate = ordinate * (1 + signed) * max_value / (2 ** bits)
        # Subtract offset
        if signed and not raw:
            ordinate = ordinate - max_value
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Remove ordinate unit in raw mode
        if raw:
            metadata = data_types.MetaData(
                name="",
                unit_a=self.inputs[0].metadata.unit_a,
                unit_o="",
            )
        else:
            metadata = self.inputs[0].metadata
        # Apply the new metadata to the output
        self.outputs[0].process_metadata = metadata
