import numpy as np

from mca.framework import validator, data_types, parameters, Block
from mca.language import _


class Amplifier(Block):
    """Amplifies the input signal by the desired factor

    This block has one input and one output.
    """
    name = _("Amplifier")
    description = _("Amplifies the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(
            meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        factor = parameters.FloatParameter(name=_("Factor"), value=1)
        decibel = parameters.FloatParameter(name=_("Decibel"), value=0, unit="dB")

        def factor_to_decibel():
            decibel.value = 10*np.log10(factor.value)

        def decibel_to_factor():
            factor.value = 10 ** (decibel.value / 10)

        conversion = parameters.ParameterConversion(
            [factor], [decibel], factor_to_decibel
        )
        conversion_1 = parameters.ParameterConversion(
            [decibel], [factor], decibel_to_factor)
        multiplier = parameters.ParameterBlock(name=_("Amplification"),
                                               parameters={"factor": factor, "decibel": decibel},
                                               param_conversions=[conversion, conversion_1],
                                               default_conversion=0)

        self.parameters.update({"multiplier": multiplier})

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        ordinate = self.parameters["multiplier"].parameters["factor"].value * input_signal.ordinate
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
