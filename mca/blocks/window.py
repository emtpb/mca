from scipy import signal

from mca.framework import data_types, parameters, util, Block
from mca.language import _


class Window(Block):
    """Applies a window function to the input signal."""
    name = _("Window")
    description = _("Applies a window function to the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "window_func": parameters.ChoiceParameter(
                _("Window Function"),
                choices=[("tukey", _("Tukey")), ("hann", _("Hann")),
                         ("hamming", _("Hamming")),
                         ("exponential", _("Exponential")),
                         ("gaussian", _("Gaussian")),
                         ("triangle", _("Triangle"))],
                default="hann"
            ),
            "alpha": parameters.FloatParameter(_("Alpha (Tukey)"), min_=0,
                                               max_=1, default=0.5),
            "std": parameters.FloatParameter(_("Standard Deviation (Gaussian)"),
                                             min_=0, default=1)
        })

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        input_signal = self.inputs[0].data
        window_name = self.parameters["window_func"].value

        if window_name == "gaussian":
            args = (window_name, self.parameters["std"].value)
        elif window_name == "tukey":
            args = (window_name, self.parameters["alpha"].value)
        else:
            args = window_name
        window = signal.get_window(args, input_signal.values)
        ordinate = input_signal.ordinate * window
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = self.inputs[0].metadata
