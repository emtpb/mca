import numpy as np

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class Limiter(Block):
    """Limits the values of the input signal. Values exceeding this limit get
    set to the threshold.
    """
    name = _("Limiter")
    description = _("Limits the values of the input signal. Values exceeding "
                    "this limit get set to the threshold.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output()
        self._new_input()

    def setup_parameters(self):
        self.parameters.update(
            {"mode": parameters.ChoiceParameter(
                _("Mode"),
                choices=[("unipolar", _("Unipolar")), ("bipolar", _("Bipolar"))], default="unipolar"),
             "threshold": parameters.FloatParameter(_("Threshold"), default=1)
             })

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        mode = self.parameters["mode"].value
        threshold = self.parameters["threshold"].value
        input_signal = self.inputs[0].data
        max_threshold = threshold
        min_threshold = None
        if mode == "bipolar":
            min_threshold = -threshold
        ordinate = np.clip(input_signal.ordinate, min_threshold, max_threshold)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )