from scipy.signal import butter, cheby1, cheby2, ellip, lfilter, filtfilt

from mca import exceptions
from mca.framework import Block, data_types, parameters, util
from mca.language import _


class IRRFilter(Block):
    """Filters with common IIR filters the input signal. The upper cut-off
    frequency is ignored when 'lowpass' or 'highpass' are selected as the
    characteristic.
    """
    name = _("IIRFilter")
    description = _("Filters with common IIR filters the input signal. The "
                    "upper cut off frequency is ignored when 'lowpass' or "
                    "'highpass' are selected as the characteristic. For "
                    "specific 'Filter types' certain parameters are ignored "
                    "as well.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["filter_type"] = parameters.ChoiceParameter(
                name=_("Filter type"),
                choices=(("butter", _("Butter")), ("cheby1", _("Cheby1")),
                         ("cheby2", _("Cheby2")), ("ellip", _("Elliptic"))
                         ),
                default="butter"
        )
        self.parameters["characteristic"] = parameters.ChoiceParameter(
            name=_("Characteristic"), choices=(("low", _("Lowpass")),
                                               ("high", _("Highpass")),
                                               ("band", _("Bandpass")),
                                               ("stop", _("Bandstop"))
                                               ),
            default="low"
        )
        self.parameters["order"] = parameters.IntParameter(
            name=_("Order"), min_=1, default=1
        )
        self.parameters["cut_off"] = parameters.FloatParameter(
            name=_("Cut off frequency"), min_=0, default=1, unit="Hz"
        )
        self.parameters["upper_cut_off"] = parameters.FloatParameter(
                name=_("Upper cut off frequency"), min_=0, default=10,
                unit="Hz"
        )
        self.parameters["ripple"] = parameters.FloatParameter(
            name=_("Ripple"), min_=0, default=5, unit="dB"
        )
        self.parameters["attenuation"] = parameters.FloatParameter(
            name=_("Attenuation"), min_=0, default=5, unit="dB"
        )
        self.parameters["phase_corr"] = parameters.BoolParameter(
                name=_("Phase correction (filtfilt)"), default=False
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        filter_type = self.parameters["filter_type"].value
        order = self.parameters["order"].value
        characteristic = self.parameters["characteristic"].value
        cut_off = self.parameters["cut_off"].value
        upper_cut_off = self.parameters["upper_cut_off"].value
        ripple = self.parameters["ripple"].value
        attenuation = self.parameters["attenuation"].value
        phase_corr = self.parameters["phase_corr"].value
        # Validation for the cut_off frequencies
        if cut_off > (2 / input_signal.increment):
            raise exceptions.ParameterValueError("Cut off frequency can not "
                                                 "exceed the nyquist frequency "
                                                 "of the input signal.")
        if (characteristic == "band") or (characteristic == "stop"):
            if upper_cut_off > (2 / input_signal.increment):
                raise exceptions.ParameterValueError(
                    "Upper cut off frequency can not exceed the nyquist "
                    "frequency of the input signal.")
            f_norm = (cut_off / (2 / input_signal.increment),
                      upper_cut_off / (2 / input_signal.increment))
        else:
            f_norm = cut_off / (2 / input_signal.increment)
        # Get the according filter
        if filter_type == "butter":
            b, a = butter(N=order, Wn=f_norm, btype=characteristic)
        elif filter_type == "cheby1":
            b, a = cheby1(N=order, Wn=f_norm,
                          btype=characteristic, rp=ripple)
        elif filter_type == "cheby2":
            b, a = cheby2(N=order, Wn=f_norm,
                          btype=characteristic, rs=attenuation)
        elif filter_type == "ellip":
            b, a = ellip(N=order, Wn=f_norm,
                         btype=characteristic, rs=attenuation, rp=ripple)
        # Apply the phase correction
        if phase_corr:
            ordinate = filtfilt(b, a, input_signal.ordinate)
        else:
            ordinate = lfilter(b, a, input_signal.ordinate)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
