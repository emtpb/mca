import networkx as nx
import json

from . import block_io
from mca import exceptions
from mca import blocks
from mca.framework import data_types


class IORegistry:
    """Class which registers all :class:`.Input` s and :class:`.Output` s 
    created and also handles connections  between Outputs and Inputs and the 
    consistency of the data through updates.
    
    Attributes:
        _graph: :ref:`Networkx Graph <networkx:DiGraph>` which is base of 
            IORegistry.
    """

    def __init__(self):
        """Initializes the IORegistry."""
        self._graph = nx.DiGraph()

    def _invalidate_descendants(self, output):
        """Sets a flag of the output itself and all descendants to indicate
        their data may be invalid.
        
        Args:
            output: Output from which the invalidation starts.
        """
        output.up_to_date = False
        for descendant in nx.descendants(self._graph, output):
            descendant.up_to_date = False

    def _update_descendants(self, output):
        """Goes threw all descendants and updates the flags and tries to update
        the block of the descendants. For example if an output is updated
        all connected inputs will be updated and the outputs of the same Block 
        as the inputs and so on.
        
        Note:
            A block will only update itself if all inputs are up to date.
        Args:
            output: Output from which the update process starts.
        """
        for edge in nx.bfs_edges(self._graph, output):
            if isinstance(edge[0], block_io.Output) and isinstance(
                    edge[1], block_io.Input
            ):
                edge[1].up_to_date = edge[0].up_to_date
                edge[1].block.update_my_block()

    def invalidate_and_update(self, block):
        """Method which is called when a change (connect, disconnect,
        delete etc.) in the IO structure occurs
        which may cause data inconsistency. This method flags and updates
        blocks with an algorithm that ensures every Block updates itself
        only once in the process.
        
        Args:
            block (:class:`.Block`): Block in which the change occured.
        """
        for output in block.outputs:
            self._invalidate_descendants(output)
        block.update_my_block()
        for output in block.outputs:
            self._update_descendants(output)

    def add_node(self, node):
        """Adds an Input or Output to the registry.
        
        Args:
            node: Input or Output which should be added to the registry.
        
        Returns:
            The node which has been added to the structure.
        """
        self._graph.add_node(node)
        if isinstance(node, block_io.Output):
            for input_ in node.block.inputs:
                self._graph.add_edge(input_, node)
            return node
        if isinstance(node, block_io.Input):
            for output in node.block.outputs:
                self._graph.add_edge(node, output)
            return node

    def remove_input(self, input_):
        """Disconnects and removes an Input from the registry.
        
        Args:
            input_: Input which gets removed.
        """
        self.disconnect_input(input_)
        self._graph.remove_node(input_)

    def remove_output(self, output):
        """Disconnects and removes an Output from the registry.
        
        Args:
            output: Output which gets removed.
        """
        self.disconnect_output(output)
        self._graph.remove_node(output)

    def connect(self, output, input_):
        """Connects an Output to an Input.
        
        Args:
            output: Output which gets connected to the Input.
            input_: Input which gets connected to Output.
        
        Raises:
            exceptions.BlockCircleError: When connecting two nodes leads to
                a circle in the structure.
        """
        if not isinstance(output, block_io.Output) or not isinstance(
                input_, block_io.Input
        ):
            message = "{} is not instance of {} or {} is not instance of {}".format(
                output, block_io.Output, input_, block_io.Input
            )
            raise exceptions.ConnectionsError(message)
        if list(self._graph.predecessors(input_)):
            raise exceptions.ConnectionsError("Input already connected")
        self._graph.add_edge(output, input_)
        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(output, input_)
            raise exceptions.BlockCircleError(input_.block)
        self.invalidate_and_update(input_.block)

    def disconnect_input(self, input_):
        """Disconnects an Input from an Output if connected.
        
        Args:
            input_: Input which gets disconnected.
        """
        output = list(self._graph.predecessors(input_))
        if output:
            self._graph.remove_edge(output[0], input_)
            self.invalidate_and_update(input_.block)

    def disconnect_output(self, output):
        """Disconnects an Output from all its Inputs.
        
        Args:
            output: Output which gets disconnected.
        """
        inputs = [x for x in self._graph.neighbors(output)]
        for input_ in inputs:
            self._graph.remove_edge(output, input_)
        for input_ in inputs:
            for output in input_.block.outputs:
                self._invalidate_descendants(output)
        for block in set([x.block for x in inputs]):
            block.update_my_block()
        for input_ in inputs:
            for output in input_.block.outputs:
                self._update_descendants(output)

    def get_output(self, input_):
        """Returns the connected Output from an Input.
        
        Args:
            input_: Input to which the Output is connected to.
        """
        if list(self._graph.predecessors(input_)):
            return list(self._graph.predecessors(input_))[0]

    def clear(self):
        """Removes all Inputs and Outputs (thus all blocks)
        from the IORegistry.
        """
        self._graph.clear()

    def get_all_blocks(self):
        """Returns all blocks currently in the IORegistry."""
        all_blocks = []
        for node in self._graph.nodes:
            if node.block not in all_blocks:
                all_blocks.append(node.block)
        return all_blocks

    def remove_block(self, block):
        """Removes inputs and outputs of a block (thus removing the block)
        from the IORegistry.

        Removing a block means that all other blocks get disconnected from its
        inputs and outputs and can not be reconnected.

        Args:
            block: Block object which inputs and outputs should be removed.
        """
        for input_ in block.inputs:
            self.remove_input(input_)
        for output in block.outputs:
            self.remove_output(output)

    def save_block_structure(self, file_path):
        """Saves the current block structure to the given file_path as
        a .json.

        Args:
            file_path (str): Path of the .json file.
        """
        save_data = {"blocks": []}
        for block in self.get_all_blocks():
            save_block = {"class": str(type(block)),
                          "parameters": {parameter_name: parameter.value for
                                         parameter_name, parameter in
                                         block.parameters.items()},
                          "inputs": [],
                          "outputs": [{
                              "id": output.id.int,
                              "meta_data": {"signal_name": output.meta_data.name,
                                            "quantity_a": output.meta_data.quantity_a,
                                            "symbol_a": output.meta_data.symbol_a,
                                            "unit_a": repr(output.meta_data.unit_a),
                                            "quantity_o": output.meta_data.quantity_o,
                                            "symbol_o": output.meta_data.symbol_o,
                                            "unit_o": repr(output.meta_data.unit_o)},
                              "abscissa_meta_data": output.abscissa_meta_data,
                              "ordinate_meta_data": output.ordinate_meta_data
                              }
                              for output in block.outputs],
                          "gui_data": block.gui_data["save_data"]}
            for input_ in block.inputs:
                input_save = {}
                if input_.connected_output:
                    input_save[
                        "connected_output"] = input_.connected_output.id.int
                save_block["inputs"].append(input_save)
            save_data["blocks"].append(save_block)
        with open(file_path, "w") as save_file:
            json.dump(save_data, save_file)

    def load_block_structure(self, file_path):
        """Loads a block structure into an empty structure.

        Args:
            file_path (str): Path of the .json file.

        Returns:
            list: All saved blocks in no particular order.
        """
        if self.get_all_blocks():
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
            for parameter_name, parameter_value in block_save["parameters"].items():
                block_instance.parameters[parameter_name].value = parameter_value
            for index, input_save in enumerate(block_save["inputs"]):
                if index + 1 > len(block_instance.inputs):
                    block_instance.add_input(block_io.Input(block_instance))
            for index, output_save in enumerate(block_save["outputs"]):
                meta_data = data_types.MetaData(
                    output_save["meta_data"]["signal_name"],
                    output_save["meta_data"]["unit_a"],
                    output_save["meta_data"]["unit_o"],
                    output_save["meta_data"]["quantity_o"],
                    output_save["meta_data"]["quantity_a"],
                    output_save["meta_data"]["symbol_a"],
                    output_save["meta_data"]["symbol_o"],
                )
                if index + 1 > len(block_instance.outputs):
                    block_instance.add_output(block_io.Output(block_instance))
                block_instance.outputs[index].meta_data = meta_data
                block_instance.outputs[index].abscissa_meta_data = output_save["abscissa_meta_data"]
                block_instance.outputs[index].ordinate_meta_data = output_save["ordinate_meta_data"]
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
                                block_structure[block_index_outer].inputs[input_index].connect(
                                    block_structure[block_index_inner].outputs[output_index])
                                found = True
        return block_structure


Registry = IORegistry()
