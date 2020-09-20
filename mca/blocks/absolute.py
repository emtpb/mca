from united import Unit

import mca.framework
from mca.framework import validator
from mca.language import _


class Absolute(mca.framework.Block):
    """Block class which calculates the absolute of the input signal.

    This block has one input and one output.
    """
    name = _("AbsoluteBlock")
    description = _("Computes the absolute of the input signal.")

    def __init__(self, **kwargs):
        """Initialize the adder block.

        Args:
            **kwargs: Arbitrary keyword arguments which are used set parameters
                of the block if there are any.
        """

        super().__init__()
        self._new_output(
            meta_data=mca.framework.data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V"
            )
        )
        self._new_input()
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data
        ordinate = abs(input_signal.ordinate)
        self.outputs[0].data = mca.framework.data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
