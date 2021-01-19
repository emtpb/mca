import os
import json

from mca.blocks import SignalSaver


def test_save_data(sin_block, sin_signal):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    a = SignalSaver(filename=dir_path + "/sin.json")
    b = sin_block
    a.inputs[0].connect(b.outputs[0])
    a.save_data()
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
    with open(dir_path + "/sin.json", "r") as save_file:
        test_dict_saved = json.load(save_file)
    assert test_dict == test_dict_saved

    file_list = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    for f in file_list:
        os.remove(os.path.join(dir_path, f))
