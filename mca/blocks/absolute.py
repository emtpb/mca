from mca.framework import data_types, util, Block
from mca.language import _


class Absolute(Block):
    """Computes the absolute of the input signal."""
    name = _("Absolute")
    description = _("Computes the absolute of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        input_signal = self.inputs[0].data
        ordinate = abs(input_signal.ordinate)
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        self.outputs[0].external_metadata = self.inputs[0].metadata
