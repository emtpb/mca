import pytest
import os

from mca.blocks import signal_generator_arbitrary, signal_generator_periodic

dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def clean_up_jsons():
    yield
    file_list = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    for f in file_list:
        os.remove(os.path.join(dir_path, f))


def test_load_json(clean_up_jsons):
    clean_up_jsons
    a = signal_generator_periodic.SignalGeneratorPeriodic(values=100, function="sin")
    a.apply_parameter_changes()
    a.save_output_data(0, dir_path + "/sin.json")
    b = signal_generator_arbitrary.SignalGeneratorArbitrary()
    b.load_data(dir_path + "/sin.json")
    assert a.outputs[0].data == b.outputs[0].data
    a.parameters["function"].value = "rect"
    a.apply_parameter_changes()
    a.save_output_data(0, dir_path + "/rect.json")
    b.load_data(dir_path + "/rect.json")
    assert a.outputs[0].data == b.outputs[0].data
    with pytest.raises(FileNotFoundError):
        b.load_data("test")
