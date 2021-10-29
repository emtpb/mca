import pytest
import os
import json

from mca.blocks import signal_generator_arbitrary
from mca import exceptions

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_load_json(sin_signal):
    test_dict = {"data_type": "Signal",
                 "name": sin_signal.metadata.name,
                 "quantity_a": sin_signal.metadata.quantity_a,
                 "symbol_a": sin_signal.metadata.symbol_a,
                 "unit_a": repr(sin_signal.metadata.unit_a),
                 "quantity_o": sin_signal.metadata.quantity_o,
                 "symbol_o": sin_signal.metadata.symbol_o,
                 "unit_o": repr(sin_signal.metadata.unit_o),
                 "abscissa_start": sin_signal.abscissa_start,
                 "values": sin_signal.values,
                 "increment": sin_signal.increment,
                 "ordinate": sin_signal.ordinate.tolist()}
    file_name = dir_path+"/sin.json"
    with open(file_name, "w") as save_file:
        json.dump(test_dict, save_file)
    b = signal_generator_arbitrary.SignalGeneratorArbitrary()
    b.parameters["file_name"].value = file_name
    b.load_file()
    assert b.outputs[0].data == sin_signal
    assert b.outputs[0].data.metadata.unit_a == sin_signal.metadata.unit_a
    assert b.outputs[0].data.metadata.unit_o == sin_signal.metadata.unit_o
    assert b.outputs[0].data.metadata.quantity_a == sin_signal.metadata.quantity_a
    assert b.outputs[0].data.metadata.quantity_o == sin_signal.metadata.quantity_o
    with pytest.raises(exceptions.DataLoadingError):
        b.parameters["file_name"].value = "test.json"
        b.load_file()
    test_dict["data_type"] = "test"
    with open(file_name, "w") as save_file:
        json.dump(test_dict, save_file)
    with pytest.raises(exceptions.DataLoadingError):
        b.parameters["file_name"].value = file_name
        b.load_file()
    os.remove(file_name)
