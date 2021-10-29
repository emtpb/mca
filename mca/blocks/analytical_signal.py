from scipy.signal import hilbert


from mca.framework import validator, data_types, Block
from mca.language import _


class AnalyticalSignal(Block):
    """Computes the analytical signal of the input signal."""
    name = _("AnalyticalSignal")
    description = _("Computes the analytical signal of the input signal.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        analytical_signal = hilbert(input_signal.ordinate)
        meta_data = data_types.MetaData(None, input_signal.meta_data.unit_a,
                                        input_signal.meta_data.unit_o)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=analytical_signal,
        )
