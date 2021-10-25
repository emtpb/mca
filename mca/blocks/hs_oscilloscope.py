from tiepie import Oscilloscope
from copy import deepcopy

from mca.framework import data_types, parameters, Block
from mca.language import _


class HSOscilloscope(Block):
    """Extract data from a Handyscope oscilloscope. Parameters allow basic
    setting of device options.

    Attributes:
        oscilloscope: HS oscilloscope device object.
    """
    name = _("HSOscilloscope")
    description = _("Extract data from a Handyscope oscilloscope")
    tags = (_("Generating"),)

    def __init__(self, **kwargs):
        """Initializes HSOscilloscope."""
        super().__init__(**kwargs)
        self.oscilloscope = None

    def setup_io(self):
        self._new_output(
            name=_("Channel 1"),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )
        self._new_output(
            name=_("Channel 2"),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )

    def setup_parameters(self):
        volt_range = parameters.ChoiceParameter(_("Range"),
                                                choices=[(0.2, "0.2"),
                                                         (0.4, "0.4"),
                                                         (0.8, "0.8"),
                                                         (2, "2"),
                                                         (4, "4"),
                                                         (8, "8"),
                                                         (20, "20"),
                                                         (40, "40"),
                                                         (80, "80")],
                                                value=80)
        trig_lvl = parameters.FloatParameter(_("Trigger Level"), min_=0,
                                             max_=1, value=0.5)
        trig_kind = parameters.ChoiceParameter(_("Trigger Kind"),
                                               choices=[("rising", "Rising Edge"),
                                                        ("falling", "Falling Edge"),
                                                        ("in window", "In Window"),
                                                        ("out window", "Out Window")],
                                               value="rising")
        trig_enabled_ch1 = parameters.BoolParameter(_("Enable Trigger"), value=True)
        ch1 = parameters.ParameterBlock(name=_("Channel 1"),
                                        parameters={"range": volt_range,
                                                    "enable_trig": trig_enabled_ch1,
                                                    "trig_lvl": trig_lvl,
                                                    "trig_kind": trig_kind})
        trig_enabled_ch2 = parameters.BoolParameter(_("Enable Trigger"),
                                                    value=False)
        ch2 = parameters.ParameterBlock(name=_("Channel 2"),
                                        parameters={"range": deepcopy(volt_range),
                                                    "enable_trig": trig_enabled_ch2,
                                                    "trig_lvl": deepcopy(trig_lvl),
                                                    "trig_kind": deepcopy(trig_kind)})
        self.parameters.update({
            "device": parameters.ChoiceParameter(
                name=_("Device"),
                choices=[("HS3", "HS3"), ("HS5", "HS5")],
                value="HS3"),
            "connect": parameters.ActionParameter(
                _("Connect"),
                function=self.connect_oscilloscope),
            "adc_resolution": parameters.ChoiceParameter(_("ADC Resolution"),
                                                        choices=[(8, "8"), (10, "10"), (12, "12"), (14, "14")],
                                                        value=8),
            "sample_freq": parameters.FloatParameter(_("Sample Frequency"), unit="Hz", value=1e8),
            "record_length": parameters.IntParameter(_("Record Length"), value=5000),
            "measure": parameters.ActionParameter(_("Measure"), function=self.measure),
            "ch1": ch1,
            "ch2": ch2
             })

    def _process(self):
        if self.oscilloscope:
            self.apply_parameters()

    def connect_oscilloscope(self):
        """Connects to an oscilloscope by creating an instance of the
        tiepie oscilloscope class.
        """
        device = self.parameters["device"].value
        self.oscilloscope = Oscilloscope(device)
        self.apply_parameters()

    def measure(self):
        """Measures and extracts data from the oscilloscope. This triggers an
        update in the block structure.
        """
        if not self.oscilloscope:
            raise RuntimeError("No oscilloscope object initialized.")
        self.apply_parameters()
        measurement = self.oscilloscope.measure()
        time_vector = self.oscilloscope.time_vector
        increment = 1/self.parameters["sample_freq"].value
        values = len(time_vector)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(None),
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=measurement[0])
        self.outputs[1].data = data_types.Signal(
            meta_data=self.outputs[1].get_meta_data(None),
            abscissa_start=0,
            values=values,
            increment=increment,
            ordinate=measurement[1])
        self.trigger_update()

    def apply_parameters(self):
        """Applies the values of the parameters to the oscilloscope device
        options.
        """
        self.oscilloscope.sample_freq = self.parameters["sample_freq"].value
        self.oscilloscope.resolution = self.parameters["adc_resolution"].value
        self.oscilloscope.record_length = self.parameters["record_length"].value
        for channel, index in zip(self.oscilloscope.channels, ("1", "2")):
            channel.range = self.parameters["ch{}".format(index)].parameters["range"].value
            channel.is_trig_enabled = self.parameters["ch{}".format(index)].parameters["enable_trig"].value
            channel.trig_kind = self.parameters["ch{}".format(index)].parameters[
                "trig_kind"].value
            channel.trig_lvl = (self.parameters["ch{}".format(index)].parameters[
                "trig_lvl"].value,)
