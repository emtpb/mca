import numpy as np

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class Quantization(Block):
    """Quantizes the input signal by a given amount of bits. Returns optionally
    the raw bit values."""
    name = _("Quantization")
    description = _("Quantizes the input signal by a given amount of bits. "
                    "Returns optionally the raw bit values.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "bits": parameters.IntParameter(_("Bits"), min_=1, default=10),
            "max_value": parameters.FloatParameter(_("Max value"), min_=0,
                                                   default=1),
            "signed": parameters.BoolParameter(_("Signed"), default=True),
            "raw": parameters.BoolParameter(_("Raw bits"), default=False)
        })

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        bits = self.parameters["bits"].value
        max_value = self.parameters["max_value"].value
        signed = self.parameters["signed"].value
        raw = self.parameters["raw"].value

        if not signed:
            ordinate = input_signal.ordinate * (2 ** bits) / max_value
        else:
            ordinate = (input_signal.ordinate + max_value) * (2 ** bits - 1) / (
                        2 * max_value)
        ordinate = np.rint(ordinate)

        pos_clipping_mask = ordinate > 2 ** bits - 1
        neg_clipping_mask = ordinate < 0
        ordinate = ~(
                    pos_clipping_mask | neg_clipping_mask) * ordinate + pos_clipping_mask * (
                               2 ** bits - 1)

        if not raw:
            ordinate = ordinate * (1 + signed) * max_value / (2 ** bits)

        if signed and not raw:
            ordinate = ordinate - max_value
        if raw:
            metadata = data_types.MetaData(
                name="",
                unit_a=self.inputs[0].metadata.unit_a,
                unit_o="",
            )
        else:
            metadata = self.inputs[0].metadata

        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = metadata
