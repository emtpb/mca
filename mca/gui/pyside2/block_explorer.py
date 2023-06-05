import os

from PySide2 import QtWidgets, QtCore, QtGui

import mca
from mca import blocks
from mca.language import _


class BlockExplorer(QtWidgets.QWidget):
    """Widget that holds and arranges the search bar,
     the button filter and the block list.

     Attributes:
         search_bar: Matches the strings the tags and block classes within
                     the block list.
         tag_check_box: Sets whether blocks should be grouped by tags or
                        just be listed.
         block_list: Contains blocks and tags al items.
     """

    def __init__(self, scene):
        """Initialize BlockExplorer widget.

        Args:
            scene: Reference of the block scene.
        """
        QtWidgets.QWidget.__init__(self)

        self.setMinimumSize(200, 0)
        self.setLayout(QtWidgets.QVBoxLayout())
        # Init the searchbar
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.setPlaceholderText(_("Search..."))
        # Init the check boy for tags
        self.tag_check_box = QtWidgets.QCheckBox(_("Show tags"))
        self.tag_check_box.setChecked(True)
        # Init the blocklist
        self.block_list = BlockList(scene)
        self.block_list.tag_check_box = self.tag_check_box

        self.tag_check_box.stateChanged.connect(self.block_list.show_blocks)

        self.block_list.search_bar = self.search_bar
        self.search_bar.textChanged.connect(self.block_list.show_items)

        self.layout().addWidget(self.search_bar)
        self.layout().addWidget(self.tag_check_box)
        self.layout().addWidget(self.block_list)

        self.block_list.show_blocks()


class BlockList(QtWidgets.QListWidget):
    """BlockList widget holding tags and drag-able blocks. Allows creating
    block items in the :class:`.BlockScene` with the drag-able block list
    items.
    """

    def __init__(self, scene):
        """Initialize BlockList widget.

        Args:
            scene: Reference of the :class:`.BlockScene` .
        """
        QtWidgets.QListWidget.__init__(self)

        self.scene = scene
        self.search_bar = None
        self.tag_check_box = None

        self.setDragEnabled(True)

        self.menu = QtWidgets.QMenu()
        self.new_block_action = QtWidgets.QAction(_("New block"))
        self.new_block_action.triggered.connect(
            lambda: self.scene.create_block_item(self.currentItem().data(3)(),
                                                 self.width(), 10)
        )
        self.menu.addAction(self.new_block_action)
        # Add all blocks to the block list
        for block_class in blocks.block_classes:
            self.add_block(block_class)
        # Add the tags to the lists
        for tag in blocks.tag_dict.keys():
            self.add_tag(tag)

    def mouseMoveEvent(self, event):
        """Method invoked when the mouse grabs an item from the list. Allows
        dragging the blocks into the :class:`.BlockScene`.
        """
        mime_data = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction,
                   QtCore.Qt.CopyAction)

    def mouseDoubleClickEvent(self, event):
        """Method invoked when an item in the list gets double-clicked. If a
        block gets clicked, it will get initialized in the :class:`.BlockScene`.
        If a tag gets clicked the string will appear in the search_bar.
        """
        item = self.currentItem()
        if item is None:
            return
        if item.data(4) == "block":
            selected_block_class = item.data(3)
            self.scene.create_block_item(selected_block_class(), 0, 0,
                                         open_edit_window=False,
                                         random_pos=True)
        elif item.data(4) == "tag":
            self.search_bar.setText(_(item.data(5)))

    def contextMenuEvent(self, event):
        """Method invoked when right-clicking with the mouse. Opens
        the menu.
        """
        item = self.itemAt(event.pos())
        if item.data(4) == "block":
            self.menu.exec_(event.globalPos())

    def show_items(self):
        """Wrapper method for show blocks to connect to the
        search_bar textChanged signal.
        """
        self.show_blocks(self.tag_check_box.checkState())

    def hide_all_items(self):
        """Hide all items in the BlockList."""
        all_items = self.findItems("", QtCore.Qt.MatchStartsWith)
        for item in all_items:
            self.setItemHidden(item, True)

    def show_blocks(self, tags=True):
        """Show all block items matching the search string in the search bar.

        Args:
            tags: If True, all blocks are grouped according to their tags. If a
                  block has multiple tags it is listed under all its tags.
        """
        # By default hide all items
        self.hide_all_items()
        # Get the matching items from the search_bar  string
        search_string = self.search_bar.text()
        matching_items = self.findItems(search_string, QtCore.Qt.MatchContains)
        if not tags:
            # Show the blocks without tags
            for item in matching_items:
                if item.data(4) == "block" and item.data(5) is False:
                    item.setHidden(False)
        else:
            # Get the matching tags
            matching_tags = filter(lambda x: x.data(4) == "tag", matching_items)
            related_blocks = []
            # Get the blocks which are related to the tags
            for tag in matching_tags:
                related_blocks += tag.related_blocks
            # Block classes which match due their tags matching with the search
            # string
            matching_blocks = list(map(lambda x: x.data(3), related_blocks))
            for item in matching_items:
                # Show blocks not associated with tags if they match with the
                # search string and are not associated with a matching tag
                # already
                if search_string and item.data(5) is False and matching_blocks.count(item.data(3)) == 0:
                    item.setHidden(False)
                # Show the tag and all its associated blocks
                elif item.data(4) == "tag":
                    item.setHidden(False)

    def add_block(self, block, related_block=False):
        """Adds a block to the list.

        Args:
            block: Class of the block to add.
            related_block: Flag whether the block is related to a tag.
        """
        item = QtWidgets.QListWidgetItem()
        # Set an icon file if exist
        if block.icon_file:
            item.setIcon(QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + block.icon_file))
        # Save the block class
        item.setData(3, block)
        # Set the list type
        item.setData(4, "block")
        # Set if it is related to a tag
        item.setData(5, related_block)
        # Set the text
        item.setText(_(block.name))

        self.addItem(item)
        return item

    def add_tag(self, tag_name):
        """Adds a tag and its related blocks to the list.

        Args:
            tag_name (str): Name of the tag.
        """
        tag_item = TagListItem(tag_name=tag_name)
        self.addItem(tag_item)
        for block_class in blocks.tag_dict[tag_name]:
            block_item = self.add_block(block_class, related_block=True)
            tag_item.related_blocks.append(block_item)
        return tag_item


class TagListItem(QtWidgets.QListWidgetItem):
    """Custom list widget item for tags. Setting the hidden status
    of the tag item also sets the status for the related blocks.

    Attributes:
        related_blocks(list): List of all block list items related to this tag.
    """

    def __init__(self, tag_name):
        """Initialize TagListItem.

        Args:
            tag_name: Name of the tag.
        """
        QtWidgets.QListWidgetItem.__init__(self)
        # Set the list type
        self.setData(4, "tag")
        # Set the name
        self.setData(5, tag_name)
        # Custom font
        font = self.font()
        font.setBold(True)
        font.setPointSize(13)
        self.setFont(font)
        self.setText(_(tag_name))

        self.related_blocks = []

    def setHidden(self, hide):
        """Sets the hidden status for itself and the related blocks.

        Args:
            hide: True to set the tag and the related blocks hidden.
        """
        for block in self.related_blocks:
            block.setHidden(hide)
        super().setHidden(hide)
