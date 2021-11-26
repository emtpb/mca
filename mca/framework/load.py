import json

from mca import exceptions, blocks
from mca.framework import io_registry, block_io, data_types


def load_block_structure(file_path):
    """Loads a block structure into an empty structure.

    Args:
        file_path (str): Path of the .json file.

    Returns:
        list: Contains all saved blocks in no particular order.
    """
    if io_registry.Registry.get_all_blocks():
        raise exceptions.DataLoadingError("Cannot load block structure"
                                          "into an existing structure.")
    with open(file_path, "r") as load_file:
        load_data = json.load(load_file)
    str_to_block_types = {str(block_class): block_class
                          for block_class in blocks.block_classes}
    block_structure = []
    for block_save in load_data["blocks"]:
        block_instance = str_to_block_types[block_save["class"]]()
        block_structure.append(block_instance)
        block_instance.gui_data["save_data"] = block_save["gui_data"]
        for parameter_name, parameter in block_save["parameters"].items():
            if isinstance(parameter, dict):
                for sub_parameter_name, sub_parameter in parameter.items():
                    block_instance.parameters[parameter_name].parameters[
                        sub_parameter_name].value = sub_parameter
            else:
                block_instance.parameters[parameter_name].value = parameter
        for index, input_save in enumerate(block_save["inputs"]):
            if index + 1 > len(block_instance.inputs):
                block_instance.add_input(block_io.Input(block_instance))
        for index, output_save in enumerate(block_save["outputs"]):
            metadata = data_types.MetaData(
                output_save["metadata"]["signal_name"],
                output_save["metadata"]["unit_a"],
                output_save["metadata"]["unit_o"],
                output_save["metadata"]["quantity_a"],
                output_save["metadata"]["quantity_o"],
                output_save["metadata"]["symbol_a"],
                output_save["metadata"]["symbol_o"],
            )
            if index + 1 > len(block_instance.outputs):
                block_instance.add_output(block_io.Output(block_instance))
            block_instance.outputs[index].metadata = metadata
            block_instance.outputs[index].abscissa_metadata = output_save[
                "abscissa_metadata"]
            block_instance.outputs[index].ordinate_metadata = output_save[
                "ordinate_metadata"]
            block_instance.trigger_update()
    for block_index_outer, block_save_outer in enumerate(
            load_data["blocks"]):
        for input_index, input_save in enumerate(
                block_save_outer["inputs"]):
            if input_save.get("connected_output"):
                found = False
                for block_index_inner, block_save_inner in enumerate(
                        load_data["blocks"]):
                    if found:
                        break
                    for output_index, output_save in enumerate(
                            block_save_inner["outputs"]):
                        if input_save["connected_output"] == output_save["id"]:
                            block_structure[block_index_outer].inputs[
                                input_index].connect(
                                block_structure[block_index_inner].outputs[
                                    output_index])
                            found = True
    return block_structure
