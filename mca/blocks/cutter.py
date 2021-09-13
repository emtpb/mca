from mca import exceptions
from mca.framework import validator, data_types, Block, parameters
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
        self._new_output(meta_data=data_types.default_meta_data())
        self._new_input()

    def setup_parameters(self):
        self.parameters.update({
            "start_value": parameters.FloatParameter(_("Start value"), value=0),
            "end_value": parameters.FloatParameter(_("End value"), value=1)
        })

    def _process(self):
        if self.check_all_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        start_value = self.parameters["start_value"].value
        end_value = self.parameters["end_value"].value

        if start_value < input_signal.abscissa_start:
            raise exceptions.ParameterValueError("Cut start has to be even or "
                                                 "greater than the abscissa "
                                                 "start.")
        if end_value <= start_value:
            raise exceptions.ParameterValueError("Cut end has to be greater "
                                                 "than the cut start.")
        if input_signal.abscissa_start + input_signal.increment*(input_signal.values-1) < end_value:
            raise exceptions.ParameterValueError("Cut end must be even or less than the abscissa end.")

        start_index = int(
            (start_value-input_signal.abscissa_start)/input_signal.increment)
        end_index = int(
            (end_value-input_signal.abscissa_start)/input_signal.increment)+1

        abscissa_start = input_signal.abscissa_start + input_signal.increment*start_index
        values = end_index-start_index
        ordinate = input_signal.ordinate[start_index:end_index]

        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=abscissa_start,
            values=values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
