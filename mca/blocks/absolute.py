from mca.framework import validator, data_types, Block
from mca.language import _


class Absolute(Block):
    """Computes the absolute of the input signal."""
    name = _("Absolute")
    description = _("Computes the absolute of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        ordinate = abs(input_signal.ordinate)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
