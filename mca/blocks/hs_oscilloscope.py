from copy import deepcopy

from handyscope import Oscilloscope

from mca.framework import Block, data_types, parameters


class HSOscilloscope(Block):
    """Measure and extract data from a Handyscope oscilloscope.
     Parameters allow basic setting of device options.

    Attributes:
        oscilloscope: HS oscilloscope device object.
    """
    name = "HSOscilloscope"
    description = "Measure and extract data from a Handyscope oscilloscope"
    tags = ("Generating",)

    def __init__(self, **kwargs):
        """Initializes HSOscilloscope."""
        super().__init__(**kwargs)
        self.oscilloscope = None

    def setup_io(self):
        self.new_output(name="Channel 1", user_metadata_required=True)
        self.new_output(name="Channel 2", user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["device"] = parameters.ChoiceParameter(
                name="Device", choices=(("HS3", "HS3"),
                                           ("HS5", "HS5")),
                default="HS3"
        )
        self.parameters["connect"] = parameters.ActionParameter(
                name="Connect", function=self.connect_oscilloscope
        )
        self.parameters["adc_resolution"] = parameters.ChoiceParameter(
            name="ADC Resolution", choices=((8, "8"), (10, "10"),
                                               (12, "12"), (14, "14")),
            default=8
        )
        self.parameters["sample_freq"] = parameters.FloatParameter(
            name="Sample Frequency", unit="Hz", default=1e8
        )
        self.parameters["record_length"] = parameters.IntParameter(
            name="Record Length", default=5000
        )
        self.parameters["measure"] = parameters.ActionParameter(
            name="Measure", function=self.measure
        )
        volt_range = parameters.ChoiceParameter("Range",
                                                choices=[(0.2, "0.2"),
                                                         (0.4, "0.4"),
                                                         (0.8, "0.8"),
                                                         (2, "2"),
                                                         (4, "4"),
                                                         (8, "8"),
                                                         (20, "20"),
                                                         (40, "40"),
                                                         (80, "80")],
                                                default=80)
        trig_lvl = parameters.FloatParameter("Trigger Level", min_=0,
                                             max_=1, default=0.5)
        trig_kind = parameters.ChoiceParameter("Trigger Kind",
                                               choices=[
                                                   ("rising", "Rising Edge"),
                                                   ("falling", "Falling Edge"),
                                                   ("in window", "In Window"),
                                                   (
                                                   "out window", "Out Window")],
                                               default="rising")
        trig_enabled_ch1 = parameters.BoolParameter("Enable Trigger",
                                                    default=True)
        ch1 = parameters.ParameterBlock(name="Channel 1",
                                        parameters={"range": volt_range,
                                                    "enable_trig": trig_enabled_ch1,
                                                    "trig_lvl": trig_lvl,
                                                    "trig_kind": trig_kind})
        trig_enabled_ch2 = parameters.BoolParameter("Enable Trigger",
                                                    default=False)
        ch2 = parameters.ParameterBlock(name="Channel 2",
                                        parameters={
                                            "range": deepcopy(volt_range),
                                            "enable_trig": trig_enabled_ch2,
                                            "trig_lvl": deepcopy(trig_lvl),
                                            "trig_kind": deepcopy(trig_kind)})
        self.parameters["ch1"] = ch1
        self.parameters["ch2"] = ch2

    def process(self):
        if self.oscilloscope:
            self.apply_parameters()

    def connect_oscilloscope(self):
        """Connects to an oscilloscope device by creating an instance of the
        handyscope oscilloscope class.
        """
        device = self.parameters["device"].value
        self.oscilloscope = Oscilloscope(device)
        self.apply_parameters()

    def measure(self):
        """Measures and extracts data from the oscilloscope. This triggers an
        update in the block structure.
        """
        # Check if an oscilloscope has been initialized
        if not self.oscilloscope:
            raise RuntimeError("No oscilloscope object initialized.")
        # Apply the parameters
        self.apply_parameters()
        # Start a measurement
        measurement = self.oscilloscope.measure()
        time_vector = self.oscilloscope.time_vector
        # Get the abscissa start
        abscissa_start = time_vector[0]
        # Calculate the increment
        increment = 1 / self.parameters["sample_freq"].value
        # Calculate the amount of values
        values = len(time_vector)
        # Apply the signals to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=measurement[0])
        self.outputs[1].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=measurement[1])
        # Trigger an update manually since this is not executed within the
        # process method
        self.trigger_update()

    def apply_parameters(self):
        """Applies the values of the parameters to the oscilloscope device."""
        self.oscilloscope.sample_freq = self.parameters["sample_freq"].value
        self.oscilloscope.resolution = self.parameters["adc_resolution"].value
        self.oscilloscope.record_length = self.parameters["record_length"].value
        for channel, index in zip(self.oscilloscope.channels, ("1", "2")):
            channel.range = self.parameters["ch{}".format(index)].parameters[
                "range"].value
            channel.is_trig_enabled = \
            self.parameters["ch{}".format(index)].parameters[
                "enable_trig"].value
            channel.trig_kind = \
            self.parameters["ch{}".format(index)].parameters[
                "trig_kind"].value
            channel.trig_lvl = (
            self.parameters["ch{}".format(index)].parameters[
                "trig_lvl"].value,)
