from mca.framework import data_types, Block, util
from mca.language import _


class Divider(Block):
    """Divides the two input signals."""
    name = _("Divider")
    description = _("Divides the two input signals.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(
        )
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_any_inputs_empty
    @util.validate_type_signal
    @util.validate_units(abscissa=True)
    @util.validate_intervals
    def _process(self):
        input_signals = [self.inputs[0].data, self.inputs[1].data]

        unit_a = self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o / self.inputs[1].metadata.unit_o
        metadata = data_types.MetaData(None, unit_a, unit_o)

        matched_signals = util.fill_zeros(input_signals)
        ordinate = input_signals[0].ordinate / input_signals[1].ordinate
        values = matched_signals[0].values
        increment = matched_signals[0].increment
        abscissa_start = matched_signals[0].abscissa_start

        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )

        self.outputs[0].external_metadata = metadata
