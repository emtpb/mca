import numpy as np

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class Amplifier(Block):
    """Amplifies the input signal by the desired factor."""
    name = _("Amplifier")
    description = _("Amplifies the input signal by the desired factor.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        # Create two equivalent parameters for amplification
        factor = parameters.FloatParameter(name=_("Factor"), default=1)
        decibel = parameters.FloatParameter(name=_("Decibel"), default=0,
                                            unit="dB")

        # Define the conversions between the parameters
        def factor_to_decibel():
            decibel.value = 10 * np.log10(factor.value)

        def decibel_to_factor():
            factor.value = 10 ** (decibel.value / 10)

        conversion = parameters.ParameterConversion(
            [factor], [decibel], factor_to_decibel
        )
        conversion_1 = parameters.ParameterConversion(
            [decibel], [factor], decibel_to_factor)
        # Create a parameter block of the amplification parameters
        multiplier = parameters.ParameterBlock(name=_("Amplification"),
                                               parameters={"factor": factor,
                                                           "decibel": decibel},
                                               param_conversions=[conversion,
                                                                  conversion_1],
                                               default_conversion=0)

        self.parameters["multiplier"] = multiplier

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        amplification = self.parameters["multiplier"].parameters["factor"].value
        # Calculate the ordinate
        ordinate = amplification * input_signal.ordinate
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
