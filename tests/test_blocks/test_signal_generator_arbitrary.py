import pytest
import os
import json
import test_data

from mca.blocks import signal_generator_arbitrary
from mca import exceptions

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_load_json():
    test_dict = {"data_type": "Signal",
                 "name": test_data.sin_signal.meta_data.name,
                 "quantity_a": test_data.sin_signal.meta_data.quantity_a,
                 "symbol_a": test_data.sin_signal.meta_data.symbol_a,
                 "unit_a": test_data.sin_signal.meta_data.unit_a,
                 "quantity_o": test_data.sin_signal.meta_data.quantity_o,
                 "symbol_o": test_data.sin_signal.meta_data.symbol_o,
                 "unit_o": test_data.sin_signal.meta_data.unit_o,
                 "abscissa_start": test_data.sin_signal.abscissa_start,
                 "values": test_data.sin_signal.values,
                 "increment": test_data.sin_signal.increment,
                 "ordinate": str(test_data.sin_signal.ordinate)}

    with open(dir_path+"/sin.json", "w") as save_file:
        json.dump(test_dict, save_file)
    b = signal_generator_arbitrary.SignalGeneratorArbitrary()
    b.load_data(dir_path+"/sin.json")
    assert b.outputs[0].data == test_data.sin_signal
    assert b.outputs[0].data.meta_data == test_data.sin_signal.meta_data
    with pytest.raises(FileNotFoundError):
        b.load_data("test")
    test_dict["data_type"] = "test"
    with open(dir_path + "/sin.json", "w") as save_file:
        json.dump(test_dict, save_file)
    with pytest.raises(exceptions.DataLoadingError):
        b.load_data(dir_path+"/sin.json")
    file_list = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    for f in file_list:
        os.remove(os.path.join(dir_path, f))
