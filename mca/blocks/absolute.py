from mca.framework import validator, data_types, Block
from mca.language import _


class Absolute(Block):
    """Calculates the absolute of the input signal.

    This block has one input and one output.
    """
    name = _("AbsoluteBlock")
    description = _("Computes the absolute of the input signal.")
    tags = (_("Processing"),)

    def __init__(self, **kwargs):
        """Initialize the adder block.

        Args:
            **kwargs: Arbitrary keyword arguments which are used set parameters
                of the block if there are any.
        """

        super().__init__()
        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
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
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
