from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.language import _
from mca import blocks


class BlockList(QtWidgets.QListWidget):
    """List widget which holds all block classes and tags. Shows and hides the
    classes and tag depending on the string in the search bar. Items are listed
    in groups: Default block group and tag groups. The block group is made of
    all block items. It is visible when searching normally or with a "@"
    in front or at least partly visible if an individual block matches with the
    search string. The tag group is made of the tag item and all block items
    with the according tag. It is visible when searching normally or with a "#"
    in front and search string matches with the tag.

    Attributes:
        search_bar: Widget for searching tags and blocks in the list.
        scene: Reference of the scene where blocks get initialized.
        block_amount (int): Amount of existing block classes.
        menu: Menu opened when right clicking an item.
    """

    def __init__(self, parent, scene, search_bar):
        """Initializes BlockList class.

        Args:
            parent: Parent of this widget.
            scene: Reference of the scene where blocks get initialized.
            search_bar: Widget for searching tags and blocks in the list.
        """
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.setDragEnabled(True)

        self.scene = scene
        self.search_bar = search_bar
        self.search_bar.textChanged.connect(self.show_items)

        self.menu = QtWidgets.QMenu()
        self.new_block_action = QtWidgets.QAction(_("Create new block"))
        self.new_block_action.triggered.connect(
            lambda: self.scene.create_block_item(self.currentItem().data(3)(),
                                                 self.width(), 10)
        )
        self.menu.addAction(self.new_block_action)

        self.block_amount = len(blocks.block_classes)
        for block_class in blocks.block_classes:
            self.add_block(block_class)
        for tag, block_classes in blocks.tag_dict.items():
            self.add_tag(tag)
            for block_class in block_classes:
                self.add_block(block_class)
        for tag in blocks.tags:
            self.set_tag_status(tag, hidden=True)

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
        """Method invoked when an item in the list gets double clicked.
        If a block gets clicked, it will get initialized in the
        :class:`.BlockScene`. If a tag gets clicked the string will appear in
        in the search_bar.
        """
        item = self.currentItem()
        if item is None:
            return
        if item.data(4) == "block":
            selected_block_class = item.data(3)
            self.scene.create_block_item(selected_block_class(), 0, 0)
        elif item.data(4) == "tag":
            self.search_bar.setText("#{}".format(item.data(5)))

    def contextMenuEvent(self, event):
        """Method invoked when right clicking with the mouse. Opens
        the menu.
        """
        self.menu.exec_(event.globalPos())

    def show_items(self):
        """Shows and hides certain list items depending on the
        search_bar string.
        """
        # Hide all items
        all_items = self.findItems("", QtCore.Qt.MatchStartsWith)
        for item in all_items:
            self.setItemHidden(item, True)
        input_string = self.search_bar.text()
        # Show only tags
        if input_string and input_string[0] == "#":
            input_string = input_string.replace("#", "")
            matching_items = self.findItems(input_string, QtCore.Qt.MatchContains)
            for item in matching_items:
                if item.data(4) == "tag":
                    self.set_tag_status(item.data(5), hidden=False)
        # Show only blocks
        elif input_string and input_string[0] == "@":
            input_string = input_string.replace("@", "")
            matching_items = self.findItems(input_string, QtCore.Qt.MatchContains)
            for item in matching_items:
                if self.indexFromItem(item).row() >= self.block_amount:
                    break
                item.setHidden(False)
        # Show everything that matches
        else:
            matching_items = self.findItems(input_string, QtCore.Qt.MatchContains)
            for item in matching_items:
                if self.indexFromItem(item).row() >= self.block_amount:
                    break
                item.setHidden(False)
            if input_string == "":
                for tag in blocks.tags:
                    self.set_tag_status(tag, hidden=True)
            else:
                for item in matching_items:
                    if item.data(4) == "tag":
                        self.set_tag_status(item.data(5), hidden=False)

    def add_block(self, block):
        """Adds a block class to the list.

        Args:
            block: Class of the block to add.
        """
        item = QtWidgets.QListWidgetItem()
        if block.icon_file:
            item.setIcon(QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + block.icon_file))
        item.setData(3, block)
        item.setData(4, "block")
        item.setText(block.name)
        item.setBackgroundColor(QtGui.QColor(255, 255, 255))
        self.addItem(item)

    def add_tag(self, tag_name):
        """Adds a tag to the list.

        Args:
            tag_name (str): Name of the tag.
        """
        item = QtWidgets.QListWidgetItem()
        item.setData(4, "tag")
        item.setData(5, tag_name)
        font = item.font()
        font.setBold(True)
        font.setPointSize(13)
        item.setFont(font)
        item.setText("#{}".format(tag_name))
        self.addItem(item)

    def set_tag_status(self, tag_name, hidden):
        """Set the status of the tags to hidden or shown. All the blocks
        listed with the tag receive the same status.

        Args:
            tag_name (str): Name of the tag.
            hidden (bool): True to set the tag hidden. False to make the tag
                           visible.
        """
        tag_item = self.findItems("#{}".format(tag_name), QtCore.Qt.MatchExactly)[0]
        tag_item.setHidden(hidden)
        index = self.indexFromItem(tag_item).row() + 1
        next_item = self.item(index)
        while next_item and next_item.data(4) == "block":
            next_item.setHidden(hidden)
            index += 1
            next_item = self.item(index)

    def set_block_status(self, hidden):
        """Sets the status of the blocks which are not listed with any tag.

        Args:
            hidden (bool): True to set the blocks all hidden. False to set
                           them visible.
        """
        for index in range(self.block_amount):
            item = self.item(index)
            item.setHidden(hidden)