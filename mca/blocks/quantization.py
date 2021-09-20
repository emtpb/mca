from mca.framework import validator, data_types, Block, parameters
from mca.language import _

import numpy as np


class Quantization(Block):
    """Quantizes the input signal by a given amount of bits. Returns optionally
    the raw bit values."""
    name = _("Quantization")
    description = _("Quantizes the input signal by a given amount of bits. "
                    "Returns optionally the raw bit values.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({
            "bits": parameters.IntParameter(_("Bits"), min_=1, value=10),
            "max_value": parameters.FloatParameter(_("Max value"), min_=0,
                                                   value=1),
            "signed": parameters.BoolParameter(_("Signed"), value=True),
            "raw": parameters.BoolParameter(_("Raw bits"), value=False)
        })

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        bits = self.parameters["bits"].value
        max_value = self.parameters["max_value"].value
        signed = self.parameters["signed"].value
        raw = self.parameters["raw"].value
        if not signed:
            ordinate = input_signal.ordinate * (2**bits) / max_value
        else:
            ordinate = (input_signal.ordinate+max_value) * (2**bits-1) / (2*max_value)
        ordinate = np.rint(ordinate)

        pos_clipping_mask = ordinate > 2**bits-1
        neg_clipping_mask = ordinate < 0
        ordinate = ~(pos_clipping_mask | neg_clipping_mask) * ordinate + pos_clipping_mask*(2**bits-1)

        if not raw:
            ordinate = ordinate * (1 + signed) * max_value / (2 ** bits)

        if signed and not raw:
            ordinate = ordinate - max_value
        if raw:
            meta_data = data_types.MetaData(
                name="",
                unit_a=input_signal.meta_data.unit_a,
                unit_o="",
            )
        else:
            meta_data = input_signal.meta_data

        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )