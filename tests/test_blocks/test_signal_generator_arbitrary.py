import pytest
import os
import json

from mca.blocks import signal_generator_arbitrary
from mca import exceptions

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_load_json(sin_signal):
    test_dict = {"data_type": "Signal",
                 "name": sin_signal.meta_data.name,
                 "quantity_a": sin_signal.meta_data.quantity_a,
                 "symbol_a": sin_signal.meta_data.symbol_a,
                 "unit_a": repr(sin_signal.meta_data.unit_a),
                 "quantity_o": sin_signal.meta_data.quantity_o,
                 "symbol_o": sin_signal.meta_data.symbol_o,
                 "unit_o": repr(sin_signal.meta_data.unit_o),
                 "abscissa_start": sin_signal.abscissa_start,
                 "values": sin_signal.values,
                 "increment": sin_signal.increment,
                 "ordinate": str(sin_signal.ordinate)}
    file_path = dir_path+"/sin.json"
    with open(file_path, "w") as save_file:
        json.dump(test_dict, save_file)
    b = signal_generator_arbitrary.SignalGeneratorArbitrary()
    b.parameters["file"].value = file_path
    b.trigger_update()
    assert b.outputs[0].data == sin_signal
    assert b.outputs[0].data.meta_data == sin_signal.meta_data
    with pytest.raises(FileNotFoundError):
        b.parameters["file"].value = "test"
        b.trigger_update()
    test_dict["data_type"] = "test"
    with open(file_path, "w") as save_file:
        json.dump(test_dict, save_file)
    with pytest.raises(exceptions.DataLoadingError):
        b.parameters["file"].value = file_path
        b.trigger_update()
    os.remove(file_path)
