import os
import json

from mca.blocks import SignalSaver


def test_save_data(sin_block, sin_signal):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    a = SignalSaver(file_name=dir_path + "/sin.json")
    b = sin_block
    a.inputs[0].connect(b.outputs[0])
    a.save_data()
    metadata = a.inputs[0].metadata
    test_dict = {"data_type": "Signal",
                 "name": metadata.name,
                 "quantity_a": metadata.quantity_a,
                 "symbol_a": metadata.symbol_a,
                 "unit_a": repr(metadata.unit_a),
                 "quantity_o": metadata.quantity_o,
                 "symbol_o": metadata.symbol_o,
                 "unit_o": repr(metadata.unit_o),
                 "abscissa_start": sin_signal.abscissa_start,
                 "values": sin_signal.values,
                 "increment": sin_signal.increment,
                 "ordinate": sin_signal.ordinate.tolist()}
    with open(dir_path + "/sin.json", "r") as save_file:
        test_dict_saved = json.load(save_file)
    assert test_dict == test_dict_saved

    file_list = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    for f in file_list:
        os.remove(os.path.join(dir_path, f))
