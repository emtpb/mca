from scipy.signal import butter, cheby1, cheby2, ellip, lfilter, filtfilt

from mca.framework import validator, data_types, Block, parameters
from mca.language import _
from mca import exceptions


class IRRFilter(Block):
    """Filters with common IIR filters the input signal. The upper cut off
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
        self.parameters.update({
            "filter_type": parameters.ChoiceParameter(
                name=_("Filter type"),
                choices=[("butter", _("Butter")), ("cheby1", _("Cheby1")),
                         ("cheby2", _("Cheby2")), ("ellip", _("Elliptic"))
                         ],
                default="butter"),
            "order": parameters.IntParameter(name=_("Order"), min_=1, default=1),
            "characteristic": parameters.ChoiceParameter(
                name=_("Characteristic"), choices=[("low", _("Lowpass")),
                                                   ("high", _("Highpass")),
                                                   ("band", _("Bandpass")),
                                                   ("stop", _("Bandstop"))]),
            "cut_off": parameters.FloatParameter(name=_("Cut off frequency"),
                                                 min_=0, default=1, unit="Hz"),
            "upper_cut_off": parameters.FloatParameter(
                name=_("Upper cut off frequency"), min_=0, default=10, unit="Hz"),
            "ripple": parameters.FloatParameter(name=_("Ripple"), min_=0,
                                                default=5, unit="dB"),
            "attenuation": parameters.FloatParameter(name=_("Attenuation"),
                                                     min_=0, default=5,
                                                     unit="dB"),
            "phase_corr": parameters.BoolParameter(
                name=_("Phase correction (filtfilt)"), default=False)
        })

    def _process(self):
        if self.all_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)

        input_signal = self.inputs[0].data
        filter_type = self.parameters["filter_type"].value
        order = self.parameters["order"].value
        characteristic = self.parameters["characteristic"].value
        cut_off = self.parameters["cut_off"].value
        upper_cut_off = self.parameters["upper_cut_off"].value
        ripple = self.parameters["ripple"].value
        attenuation = self.parameters["attenuation"].value
        phase_corr = self.parameters["phase_corr"].value

        if cut_off > (2/input_signal.increment):
            raise exceptions.ParameterValueError("Cut off frequency can not "
                                                 "exceed the nyquist frequency "
                                                 "of the input signal.")
        if (characteristic == "band") or (characteristic == "stop"):
            if upper_cut_off > (2/input_signal.increment):
                raise exceptions.ParameterValueError(
                    "Upper cut off frequency can not exceed the nyquist "
                    "frequency of the input signal.")
            f_norm = (cut_off/(2/input_signal.increment),
                      upper_cut_off/(2/input_signal.increment))
        else:
            f_norm = cut_off/(2/input_signal.increment)
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
        if phase_corr:
            ordinate = filtfilt(b, a, input_signal.ordinate)
        else:
            ordinate = lfilter(b, a, input_signal.ordinate)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(input_signal.meta_data),
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
