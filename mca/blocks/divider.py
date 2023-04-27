from mca.framework import Block, data_types, util
from mca.language import _


class Divider(Block):
    """Divides the two input signals."""
    name = _("Divider")
    description = _("Divides the two input signals.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
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
        # Fill the signals with zeros so their lengths match
        matched_signals = util.fill_zeros(input_signals)
        # Calculate the ordinate
        ordinate = input_signals[0].ordinate / input_signals[1].ordinate
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=matched_signals[0].abscissa_start,
            values=matched_signals[0].values,
            increment=matched_signals[0].increment,
            ordinate=ordinate,
        )
        # Calculate units for abscissa and ordinate
        unit_a = self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o / self.inputs[1].metadata.unit_o
        # Apply new metadata to the output
        self.outputs[0].external_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )
