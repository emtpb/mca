from mca.framework import validator, data_types, parameters, Block
from mca.language import _

from scipy import signal


class Window(Block):
    """Applies a window function to the input signal."""
    name = _("Window")
    description = _("Applies a window function to the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({
            "window_func": parameters.ChoiceParameter(
                _("Window Function"),
                choices=[("tukey", _("Tukey")), ("hann", _("Hann")),
                         ("hamming", _("Hamming")),
                         ("exponential", _("Exponential")),
                         ("gaussian", _("Gaussian")),
                         ("triangle", _("Triangle"))],
                value="hann"
            ),
            "alpha": parameters.FloatParameter(_("Alpha (Tukey)"), min_=0,
                                               max_=1, value=0.5),
            "std": parameters.FloatParameter(_("Standard Deviation (Gaussian)"),
                                             min_=0, value=1)
        })

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        kwargs = {}
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
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
