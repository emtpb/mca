from mca.framework import validator, data_types, parameters, Block
from mca.language import _


class Amplifier(Block):
    """Amplifies the input signal by the desired factor

    This block has one input and one output.
    """
    name = _("Amplifier")
    description = _("Amplifies the input signal by the desired factor")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(
            meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({"factor": parameters.FloatParameter(
            name=_("Factor"), value=1)})

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        ordinate = self.parameters["factor"].value * input_signal.ordinate
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
