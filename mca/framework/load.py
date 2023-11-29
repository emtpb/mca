import json
import logging

from mca import exceptions, blocks
from mca.framework import io_registry, block_io, data_types


def load_block_structure(file_path):
    """Loads a block structure into an empty structure.

    Args:
        file_path (str): Path of the .json file.

    Returns:
        list: List of blocks created by the save file.
    """
    logging.info(f"Loading block structure from {file_path}")
    if io_registry.Registry.get_all_blocks():
        raise exceptions.DataLoadingError("Cannot load block structure"
                                          "into an existing structure.")
    with open(file_path, "r") as load_file:
        json_string = load_file.read()
    block_structure = json_to_blocks(json_string)
    return block_structure


def json_to_blocks(json_string):
    # Load the json
    load_data = json.loads(json_string)
    # Create dict which maps strings to block classes
    str_to_block_types = {str(block_class): block_class
                          for block_class in blocks.block_classes}
    block_structure = []
    # Create all blocks in the save file
    for block_save in load_data["blocks"]:
        # Create a block instance
        try:
            block_instance = str_to_block_types[block_save["class"]]()
        except KeyError:
            logging.error(f"Could not find {block_save['class']}")
            continue
        except Exception as e:
            logging.error(f"Loading {block_save['class']} unsuccessful: {e}")
            continue

        block_structure.append(block_instance)
        # Pass the saved gui data
        block_instance.gui_data["save_data"] = block_save["gui_data"]
        # Set the values for the parameters and the plot_parameters
        for parameter_name, parameter in block_save["parameters"].items():
            if isinstance(parameter, dict):
                for sub_parameter_name, sub_parameter in parameter.items():
                    try:
                        block_instance.parameters[parameter_name].parameters[
                            sub_parameter_name].value = sub_parameter
                    except KeyError:
                        logging.error(
                            f"Could not find parameter {sub_parameter_name}"
                            f"for {block_save['class']}")
                        continue
                    except Exception as e:
                        logging.error(f"Writing parameter {sub_parameter_name} "
                                      f"unsuccessful: {e}")
                        continue
            else:
                try:
                    block_instance.parameters[parameter_name].value = parameter
                except KeyError:
                    logging.error(f"Could not find parameter {parameter_name}"
                                  f"for {block_save['class']}")
                    continue
                except Exception as e:
                    logging.error(f"Writing parameter {parameter_name} "
                                  f"unsuccessful: {e}")
                    continue
        for parameter_name, parameter in block_save["plot_parameters"].items():
            if isinstance(parameter, dict):
                for sub_parameter_name, sub_parameter in parameter.items():
                    try:
                        block_instance.plot_parameters[parameter_name].parameters[
                            sub_parameter_name].value = sub_parameter
                    except KeyError:
                        logging.error(
                            f"Could not find parameter {sub_parameter_name}"
                            f"for {block_save['class']}")
                        continue
                    except Exception as e:
                        logging.error(f"Writing parameter {sub_parameter_name} "
                                      f"unsuccessful: {e}")
                        continue
            else:
                try:
                    block_instance.plot_parameters[parameter_name].value = parameter
                except KeyError:
                    logging.error(f"Could not find parameter {parameter_name}"
                                  f"for {block_save['class']}")
                    continue
                except Exception as e:
                    logging.error(f"Writing parameter {parameter_name} "
                                  f"unsuccessful: {e}")
                    continue
        # Add additional outputs in case of a DynamicBlock
        for index, input_save in enumerate(block_save["inputs"]):
            if index + 1 > len(block_instance.inputs):
                try:
                    block_instance.add_input(block_io.Input(block_instance))
                except exceptions.DynamicIOError as e:
                    logging.error(f"Could not add input {index}: {e}")
                    continue
            block_instance.inputs[index].connected_output_id = input_save.get("connected_output")
        # Set the user metadata for the outputs
        for index, output_save in enumerate(block_save["outputs"]):
            try:
                metadata = data_types.MetaData(
                    output_save["metadata"]["signal_name"],
                    output_save["metadata"]["unit_a"],
                    output_save["metadata"]["unit_o"],
                    output_save["metadata"]["quantity_a"],
                    output_save["metadata"]["quantity_o"],
                    output_save["metadata"]["symbol_a"],
                    output_save["metadata"]["symbol_o"],
                )
            except Exception as e:
                logging.error(f"Could not load metadata for output {index}"
                              f"of {block_save['class']}: {e}")
            if index + 1 > len(block_instance.outputs):
                try:
                    block_instance.add_output(block_io.Output(block_instance))
                except exceptions.DynamicIOError as e:
                    logging.error(f"Could not add output {index}: {e}")
                    continue
            block_instance.outputs[index].id = output_save["id"]
            block_instance.outputs[index].user_metadata = metadata
            block_instance.outputs[index].use_process_abscissa_metadata = output_save[
                "use_process_abscissa_metadata"]
            block_instance.outputs[index].use_process_ordinate_metadata = output_save[
                "use_process_ordinate_metadata"]
            block_instance.trigger_update()
    # Connect inputs and outputs of the blocks
    for block_outer in block_structure:
        for input_ in block_outer.inputs:
            if input_.connected_output_id:
                found = False
                for block_inner in block_structure:
                    if found:
                        break
                    for output in block_inner.outputs:
                        if input_.connected_output_id == output.id:
                            try:
                                input_.connect(output)
                            except Exception as e:
                                logging.error(f"Could not connect {block_outer}"
                                              f"to {block_inner}: {e}")
                            else:
                                found = True
                                break
    return block_structure
