from mca import exceptions
from mca.framework import Block, data_types, parameters, util
from mca.language import _


class Cutter(Block):
    """Cuts out a part of the input signal and puts the cut out signal to the
    output. Start and end values have to be in range of the abscissa values.
    Values within the abscissa range which do not match any sampling get
    rounded down.
    """
    name = _("Cutter")
    description = _("Cuts out a part of the input signal and puts the cut out "
                    "signal to the output. Start and end values have to be in "
                    "range of the abscissa values. Values within the abscissa "
                    "range which do not match any sampling get rounded down.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["start_value"] = parameters.FloatParameter(
                name=_("Start value"), default=0
        )
        self.parameters["end_value"] = parameters.FloatParameter(
                name=_("End value"), default=1
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        start_value = self.parameters["start_value"].value
        end_value = self.parameters["end_value"].value
        # Validate the start and end values depending on the input signal
        if start_value < input_signal.abscissa_start:
            raise exceptions.ParameterValueError("Cut start has to be even or "
                                                 "greater than the abscissa "
                                                 "start.")
        if end_value <= start_value:
            raise exceptions.ParameterValueError("Cut end has to be greater "
                                                 "than the cut start.")
        if input_signal.abscissa_start + input_signal.increment * (
                input_signal.values - 1) < end_value:
            raise exceptions.ParameterValueError(
                "Cut end must be even or less than the abscissa end.")
        # Calculate the new start and end index
        start_index = int(
            (
                        start_value - input_signal.abscissa_start) / input_signal.increment)
        end_index = int(
            (
                        end_value - input_signal.abscissa_start) / input_signal.increment) + 1
        # Calculate the abscissa start
        abscissa_start = input_signal.abscissa_start + input_signal.increment * start_index
        # Calculate the amount of values
        values = end_index - start_index
        # Calculate the ordinate
        ordinate = input_signal.ordinate[start_index:end_index]
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
