import numpy as np

from mca.framework import Block, data_types, parameters, util
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
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters.update(
            {"mode": parameters.ChoiceParameter(
                _("Mode"),
                choices=[("unipolar", _("Unipolar")),
                         ("bipolar", _("Bipolar"))], default="unipolar"),
                "threshold": parameters.FloatParameter(_("Threshold"),
                                                       default=1)
            })

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        mode = self.parameters["mode"].value
        threshold = self.parameters["threshold"].value
        # Set the thresholds
        max_threshold = threshold
        min_threshold = None
        if mode == "bipolar":
            min_threshold = -threshold
        # Calculate the ordinate
        ordinate = np.clip(input_signal.ordinate, min_threshold, max_threshold)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].external_metadata = self.inputs[0].metadata
