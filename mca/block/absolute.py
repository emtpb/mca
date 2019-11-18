from mca.datatypes import signal
import mca.base as base
from mca import validator, language


class Absolute(base.block_base.Block):
    name = language._("AbsoluteBlock")
    description = language._("Computes the absolute of the input signal.")

    def __init__(self, **kwargs):
        super().__init__()
        self._new_output(
            meta_data=signal.MetaData(
                language._("Test"), language._("Zeit"), "t", "s",
                language._("Spannung"), "U", "V"
            )
        )
        self._new_input()
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0])
        input_signal = self.inputs[0].data
        ordinate = abs(input_signal.ordinate)
        self.outputs[0].data = signal.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
