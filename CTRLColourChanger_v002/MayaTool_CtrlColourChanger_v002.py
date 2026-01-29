# ------------------------------------------------------------------
# CTRL ColourChanger v002
# made with the help of Gemini
# ------------------------------------------------------------------

import sys
import json
import maya.cmds as cmds
from functools import partial

try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
class ColorUtils:
    @staticmethod
    def srgb_to_linear(rgb):
        def convert(c):
            if c <= 0.04045: return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
        return tuple(convert(c) for c in rgb)

    @staticmethod
    def hex_to_linear(hex_str):
        hex_str = hex_str.lstrip("#")
        if len(hex_str) != 6: return (0,0,0)
        srgb = tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return ColorUtils.srgb_to_linear(srgb)
    
    @staticmethod
    def get_ui_color_from_data(data):
        """Returns a QColor object from any supported data type."""
        if isinstance(data, str): return QtGui.QColor(data)
        elif isinstance(data, int):
            if data < 0: return QtGui.QColor(200, 200, 200)
            try:
                rgb = cmds.colorIndex(data, query=True)
                return QtGui.QColor.fromRgbF(*rgb)
            except: return QtGui.QColor(100, 100, 100)
        elif isinstance(data, (list, tuple)):
            if len(data) < 3: return QtGui.QColor(0,0,0)
            is_float = any(isinstance(x, float) for x in data)
            is_large = any(x > 1.0 for x in data)
            if is_large or not is_float: return QtGui.QColor(int(data[0]), int(data[1]), int(data[2]))
            else: return QtGui.QColor.fromRgbF(data[0], data[1], data[2])
        return QtGui.QColor(255, 0, 255)

class MayaLogic:
    @staticmethod
    def get_target_nodes(transform=True, shape=False):
        sel = cmds.ls(selection=True, long=True)
        if not sel: return []
        targets = []
        for node in sel:
            if cmds.nodeType(node) == "transform":
                if transform: targets.append(node)
                if shape:
                    shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
                    targets.extend(shapes)
            elif shape and "shape" in cmds.nodeType(node, inherited=True):
                 targets.append(node)
        return targets

    @staticmethod
    def apply_smart_override(nodes, color_data):
        for node in nodes:
            try:
                cmds.setAttr(f"{node}.overrideEnabled", 1)
                if isinstance(color_data, int):
                    cmds.setAttr(f"{node}.overrideRGBColors", 0)
                    cmds.setAttr(f"{node}.overrideColor", color_data)
                elif isinstance(color_data, str):
                    cmds.setAttr(f"{node}.overrideRGBColors", 1)
                    linear_rgb = ColorUtils.hex_to_linear(color_data)
                    cmds.setAttr(f"{node}.overrideColorRGB", *linear_rgb)
                elif isinstance(color_data, (list, tuple)):
                    cmds.setAttr(f"{node}.overrideRGBColors", 1)
                    raw_rgb = color_data
                    if any(x > 1.0 for x in raw_rgb): raw_rgb = [x / 255.0 for x in raw_rgb]
                    linear_rgb = ColorUtils.srgb_to_linear(raw_rgb)
                    cmds.setAttr(f"{node}.overrideColorRGB", *linear_rgb)
            except Exception as e: print(f"Error setting {node}: {e}")
    
    @staticmethod
    def copy_attributes():
        sel = cmds.ls(selection=True)
        if not sel: return None
        node = sel[0]
        return {
            "useRGB": cmds.getAttr(f"{node}.overrideRGBColors"),
            "colorIndex": cmds.getAttr(f"{node}.overrideColor"),
            "colorRGB": cmds.getAttr(f"{node}.overrideColorRGB")[0]
        }

    @staticmethod
    def paste_attributes(data, targets):
        for node in targets:
            cmds.setAttr(f"{node}.overrideEnabled", 1)
            cmds.setAttr(f"{node}.overrideRGBColors", data["useRGB"])
            if data["useRGB"]: cmds.setAttr(f"{node}.overrideColorRGB", *data["colorRGB"])
            else: cmds.setAttr(f"{node}.overrideColor", data["colorIndex"])

    @staticmethod
    def reset_override(targets):
        for node in targets:
            try:
                cmds.setAttr(f"{node}.overrideEnabled", 0)
                cmds.setAttr(f"{node}.overrideRGBColors", 0)
                cmds.setAttr(f"{node}.overrideColor", 0)
            except Exception: pass

# ------------------------------------------------------------------
# CUSTOM WIDGETS
# ------------------------------------------------------------------
class ColorListWidget(QtWidgets.QListWidget):
    """
    The grid of icons.
    """
    def __init__(self, parent=None):
        super(ColorListWidget, self).__init__(parent)
        self.setViewMode(QtWidgets.QListWidget.IconMode)
        self.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        
        # Inside ColorListWidget __init__
        self.setIconSize(QtCore.QSize(30, 30))
        # WIDTH: 55 | HEIGHT: 75 (Increased height gives the text room to breathe)
        self.setGridSize(QtCore.QSize(40, 75))
        self.setSpacing(2)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # FIXED: Added 'outline: 0' to remove dotted focus lines
        # Update your stylesheet in ColorListWidget __init__
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border-radius: 4px;
                outline: 0;
            }
            QListWidget::item {
                /* This pushes the text down away from the icon */
                padding-top: 5px; 
                padding-bottom: 8px; 
                outline: 0;
            }
            QListWidget::item:selected {
                background-color: #5285a6;
            }
        """)

        self.drop_indicator_rect = None 

    def dragMoveEvent(self, event):
        if event.source() == self:
            pos = event.pos()
            item = self.itemAt(pos)
            if item:
                rect = self.visualItemRect(item)
                if pos.x() < rect.center().x():
                    self.drop_indicator_rect = QtCore.QRect(rect.left() - 3, rect.top(), 3, rect.height())
                else:
                    self.drop_indicator_rect = QtCore.QRect(rect.right(), rect.top(), 3, rect.height())
            else:
                if self.count() > 0:
                    last_item = self.item(self.count() - 1)
                    rect = self.visualItemRect(last_item)
                    self.drop_indicator_rect = QtCore.QRect(rect.right(), rect.top(), 3, rect.height())
                else:
                    self.drop_indicator_rect = QtCore.QRect(2, 2, 3, 45) 
            self.viewport().update()
            event.accept()
        else:
            super(ColorListWidget, self).dragMoveEvent(event)

    def dragLeaveEvent(self, event):
        self.drop_indicator_rect = None
        self.viewport().update()
        super(ColorListWidget, self).dragLeaveEvent(event)

    def paintEvent(self, event):
        super(ColorListWidget, self).paintEvent(event)
        if self.drop_indicator_rect:
            painter = QtGui.QPainter(self.viewport())
            painter.fillRect(self.drop_indicator_rect, QtGui.QColor("#00FFFF"))

    def dropEvent(self, event):
        self.drop_indicator_rect = None
        self.viewport().update()

        if event.source() == self:
            target_item = self.itemAt(event.pos())
            current_item = self.currentItem()
            if not current_item: return
            
            self.takeItem(self.row(current_item))
            if target_item:
                rect = self.visualItemRect(target_item)
                target_row = self.row(target_item)
                if event.pos().x() > rect.center().x(): target_row += 1
                self.insertItem(target_row, current_item)
            else:
                self.addItem(current_item)
            event.accept()
        else:
            super(ColorListWidget, self).dropEvent(event)

class GroupHeader(QtWidgets.QWidget):
    toggled = QtCore.Signal(bool)
    def __init__(self, title, parent=None):
        super(GroupHeader, self).__init__(parent)
        self._expanded = True
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10) 

        self.grip = QtWidgets.QLabel("::")
        self.grip.setToolTip("Drag to Reorder Group")
        self.grip.setStyleSheet("color: #666; font-weight: bold; cursor: size_all_cursor;")
        self.grip.setCursor(QtCore.Qt.SizeAllCursor)
        layout.addWidget(self.grip)

        self.arrow = QtWidgets.QLabel("▼")
        self.arrow.setStyleSheet("color: #bbb; font-weight: bold;")
        self.arrow.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.arrow)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("color: #ddd; font-weight: bold;")
        self.title_label.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.title_label)

        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.line.setStyleSheet("background-color: #555;")
        layout.addWidget(self.line)

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if child == self.grip:
            event.ignore() 
            return

        if event.button() == QtCore.Qt.LeftButton:
            self._expanded = not self._expanded
            self.arrow.setText("▼" if self._expanded else "▶")
            self.toggled.emit(self._expanded)
            event.accept()

class ResizeHandle(QtWidgets.QWidget):
    resized = QtCore.Signal(int)
    def __init__(self, parent=None):
        super(ResizeHandle, self).__init__(parent)
        self.setFixedHeight(8)
        self.setCursor(QtCore.Qt.SizeVerCursor)
        self.start_y = 0
        self.bg_color = QtGui.QColor("#2b2b2b")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.bg_color)
        painter.drawRect(self.rect())
        painter.setPen(QtGui.QColor(80, 80, 80))
        mid_y = 4
        cx = self.width() / 2
        painter.drawLine(cx - 20, mid_y, cx + 20, mid_y)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_y = event.globalPos().y()
            event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            current_y = event.globalPos().y()
            dy = current_y - self.start_y
            self.start_y = current_y
            self.resized.emit(dy)
            event.accept()

class CollapsibleGroup(QtWidgets.QWidget):
    sizeChanged = QtCore.Signal() 

    def __init__(self, title, parent=None):
        super(CollapsibleGroup, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.header = GroupHeader(title)
        self.header.toggled.connect(self.on_toggle)
        self.layout.addWidget(self.header)

        self.list_widget = ColorListWidget()
        
        # Group Window Height
        self.list_widget.setFixedHeight(60) 
        self.layout.addWidget(self.list_widget)

        self.handle = ResizeHandle()
        self.handle.resized.connect(self.on_resize)
        self.layout.addWidget(self.handle)

        self.last_height = 60

    def on_toggle(self, expanded):
        if expanded:
            self.list_widget.setVisible(True)
            self.handle.setVisible(True)
            self.list_widget.setFixedHeight(self.last_height)
        else:
            self.last_height = self.list_widget.height()
            self.list_widget.setVisible(False)
            self.handle.setVisible(False)
        self.sizeChanged.emit()

    def on_resize(self, dy):
        new_height = self.list_widget.height() + dy
        if new_height < 20: new_height = 20
        self.list_widget.setFixedHeight(new_height)
        self.last_height = new_height
        self.sizeChanged.emit()

# ------------------------------------------------------------------
# MAIN GROUP LIST
# ------------------------------------------------------------------
class GroupListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(GroupListWidget, self).__init__(parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAcceptDrops(True)
        # FIXED: Added outline:0 to remove dotted lines on the group container itself
        self.setStyleSheet("QListWidget { border: none; background: transparent; outline: 0; } QListWidget::item { border: none; outline: 0; }")
        self.setResizeMode(QtWidgets.QListWidget.Adjust)

# ------------------------------------------------------------------
# JSON EDITOR
# ------------------------------------------------------------------
class JsonEditorDialog(QtWidgets.QDialog):
    def __init__(self, current_data, parent=None):
        super(JsonEditorDialog, self).__init__(parent)
        self.setWindowTitle("Edit Presets (JSON)")
        self.resize(600, 700)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        layout = QtWidgets.QVBoxLayout(self)
        info = QtWidgets.QLabel("Format: [ { \"group\": \"Name\", \"colors\": [...] } ]")
        info.setStyleSheet("color: #bbb; font-family: monospace;")
        layout.addWidget(info)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setFont(QtGui.QFont("Courier New", 10))
        self.text_edit.setText(json.dumps(current_data, indent=4))
        layout.addWidget(self.text_edit)

        btn_box = QtWidgets.QHBoxLayout()
        btn_save = QtWidgets.QPushButton("Save && Apply")
        btn_save.clicked.connect(self.validate_and_save)
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_save); btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)
        self.result_data = None

    def validate_and_save(self):
        try:
            raw = self.text_edit.toPlainText()
            data = json.loads(raw)
            if not isinstance(data, list): raise ValueError("Root must be a list.")
            for grp in data:
                if "group" not in grp or "colors" not in grp: raise ValueError("Invalid Group structure.")
            self.result_data = data
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "JSON Error", str(e))

# ------------------------------------------------------------------
# MAIN TOOL
# ------------------------------------------------------------------
class CTRLColourChanger(QtWidgets.QDialog):
    
    WINDOW_TITLE = "CTRLcColour Changer"
    
    def __init__(self, parent=None):
        super(CTRLColourChanger, self).__init__(parent) # Pass parent here
        
        self.grouped_presets = [
            {
                "group": "Standard Colors",
                "colors": [
                    ["#003399", "Dark Blue"], ["#004dca", "Blue"], ["#0099cc", "Cyan"],
                    ["#ff080d", "Red"], ["#ffcc00", "Yellow"], ["#ffffff", "White"], ["#000000", "Black"]
                ]
            },
            {
                "group": "Legacy Index",
                "colors": [
                    [13, "Wireframe Red"], [6, "Wireframe Blue"], [17, "Wireframe Yellow"]
                ]
            },
            {
                "group": "Custom",
                "colors": [
                    ["#bf80ff", "Purple"], ["#ff99ff", "Pink"], ["#99ffcc", "Mint"]
                ]
            }
        ]

        self.setup_ui()
        self.rebuild_groups_ui()
        self.center_on_maya() 

    def setup_ui(self):
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(380, 700)
        self.setWindowFlags(QtCore.Qt.Tool)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Targets
        target_grp = QtWidgets.QGroupBox("Targets")
        h_layout = QtWidgets.QHBoxLayout()
        self.chk_trans = QtWidgets.QCheckBox("Transforms")
        self.chk_trans.setChecked(True)
        self.chk_shape = QtWidgets.QCheckBox("Shapes")
        h_layout.addWidget(self.chk_trans); h_layout.addWidget(self.chk_shape)
        target_grp.setLayout(h_layout)
        self.main_layout.addWidget(target_grp)

        # Group List
        self.group_list_widget = GroupListWidget()
        self.main_layout.addWidget(self.group_list_widget)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_add = QtWidgets.QPushButton("Add New Group")
        btn_add.clicked.connect(self.add_new_group)
        btn_json = QtWidgets.QPushButton("Edit JSON...")
        btn_json.clicked.connect(self.edit_json)
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_json)
        self.main_layout.addLayout(btn_layout)

        # Actions
        act_grp = QtWidgets.QGroupBox("Actions")
        v_layout = QtWidgets.QVBoxLayout()
        r1 = QtWidgets.QHBoxLayout()
        b_c = QtWidgets.QPushButton("Copy"); b_c.clicked.connect(self.copy_attr)
        b_p = QtWidgets.QPushButton("Paste"); b_p.clicked.connect(self.paste_attr)
        r1.addWidget(b_c); r1.addWidget(b_p)
        r2 = QtWidgets.QHBoxLayout()
        b_en = QtWidgets.QPushButton("Enable"); b_en.setStyleSheet("background-color: #446644;")
        b_en.clicked.connect(lambda: self.set_enable(True))
        b_dis = QtWidgets.QPushButton("Disable"); b_dis.setStyleSheet("background-color: #664444;")
        b_dis.clicked.connect(lambda: self.set_enable(False))
        r2.addWidget(b_en); r2.addWidget(b_dis)
        b_rst = QtWidgets.QPushButton("RESET"); b_rst.setStyleSheet("background-color: #333;")
        b_rst.clicked.connect(self.reset_all)
        v_layout.addLayout(r1); v_layout.addLayout(r2); v_layout.addWidget(b_rst)
        act_grp.setLayout(v_layout)
        self.main_layout.addWidget(act_grp)
    
    # ------------------------------------------------------------------
    # GROUP MANAGEMENT
    # ------------------------------------------------------------------
    def rebuild_groups_ui(self):
        self.group_list_widget.clear()
        for grp_data in self.grouped_presets:
            self.create_group_item(grp_data)

    def create_group_item(self, grp_data):
        title = grp_data.get("group", "Untitled")
        colors = grp_data.get("colors", [])
        
        group_wid = CollapsibleGroup(title)
        
        list_w = group_wid.list_widget
        for color_val, name in colors:
            self.add_item_to_list(list_w, color_val, name)
            
        list_w.itemClicked.connect(self.on_item_clicked)
        list_w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        list_w.customContextMenuRequested.connect(partial(self.open_context_menu, list_w))

        item = QtWidgets.QListWidgetItem(self.group_list_widget)
        item.setSizeHint(group_wid.sizeHint())
        
        group_wid.sizeChanged.connect(lambda: self.update_item_size(item, group_wid))
        self.group_list_widget.setItemWidget(item, group_wid)

    def update_item_size(self, item, widget):
        item.setSizeHint(widget.sizeHint())
        # FIXED: Removed scrollToItem to prevent jumping
        # self.group_list_widget.scrollToItem(item) 

    def add_item_to_list(self, list_widget, color_val, name):
        item = QtWidgets.QListWidgetItem(name)
        item.setData(QtCore.Qt.UserRole, color_val)
        ui_color = ColorUtils.get_ui_color_from_data(color_val)
        pix = QtGui.QPixmap(45, 45)
        pix.fill(ui_color)
        item.setIcon(QtGui.QIcon(pix))
        list_widget.addItem(item)

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def on_item_clicked(self, item):
        raw_data = item.data(QtCore.Qt.UserRole)
        targets = MayaLogic.get_target_nodes(self.chk_trans.isChecked(), self.chk_shape.isChecked())
        MayaLogic.apply_smart_override(targets, raw_data)
        if targets: cmds.inViewMessage(amg=f"Applied {item.text()}", pos="topCenter", fade=True)

    def add_new_group(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "New Group", "Group Name:")
        if ok and text:
            new_data = {"group": text, "colors": []}
            self.grouped_presets.append(new_data)
            self.rebuild_groups_ui()
            self.group_list_widget.scrollToBottom()

    def edit_json(self):
        self.sync_order_from_ui()
        dlg = JsonEditorDialog(self.grouped_presets, self)
        if dlg.exec_():
            self.grouped_presets = dlg.result_data
            self.rebuild_groups_ui()
            cmds.inViewMessage(amg="Layout Updated", pos="topCenter", fade=True)

    def sync_order_from_ui(self):
        new_presets = []
        for i in range(self.group_list_widget.count()):
            item = self.group_list_widget.item(i)
            widget = self.group_list_widget.itemWidget(item)
            group_title = widget.header.title_label.text()
            colors = []
            inner_list = widget.list_widget
            for r in range(inner_list.count()):
                c_item = inner_list.item(r)
                c_val = c_item.data(QtCore.Qt.UserRole)
                c_name = c_item.text()
                colors.append([c_val, c_name])
            new_presets.append({"group": group_title, "colors": colors})
        self.grouped_presets = new_presets

    def open_context_menu(self, list_widget, pos):
        item = list_widget.itemAt(pos)
        menu = QtWidgets.QMenu()
        
        if item:
            # COPY ACTIONS
            raw_data = item.data(QtCore.Qt.UserRole)
            
            # Helper to get strings
            c = ColorUtils.get_ui_color_from_data(raw_data)
            hex_s = c.name().upper()
            rgb_s = f"{c.redF():.3f}, {c.greenF():.3f}, {c.blueF():.3f}"
            
            menu.addAction(f"Copy Hex ({hex_s})").triggered.connect(lambda: self.copy_to_clip(hex_s))
            menu.addAction(f"Copy RGB ({rgb_s})").triggered.connect(lambda: self.copy_to_clip(rgb_s))
            menu.addSeparator()
            
            menu.addAction("Delete Item").triggered.connect(lambda: list_widget.takeItem(list_widget.row(item)))
        else:
            menu.addAction("Add Color Here").triggered.connect(lambda: self.add_color_to_list(list_widget))
        
        menu.exec_(list_widget.mapToGlobal(pos))

    def copy_to_clip(self, text):
        cb = QtGui.QGuiApplication.clipboard()
        cb.setText(text)
        cmds.inViewMessage(amg=f"Copied: {text}", pos="topCenter", fade=True)

    def add_color_to_list(self, list_widget):
        col = QtWidgets.QColorDialog.getColor()
        if col.isValid():
            name, ok = QtWidgets.QInputDialog.getText(self, "Name", "Color Name:")
            if ok: self.add_item_to_list(list_widget, col.name(), name or "Custom")

    # ------------------------------------------------------------------
    # WRAPPERS
    # ------------------------------------------------------------------
    def center_on_maya(self):
        maya_win = None
        for w in QtWidgets.QApplication.topLevelWidgets():
            if w.objectName() == "MayaWindow": maya_win = w; break
        if maya_win:
            geo = self.frameGeometry()
            geo.moveCenter(maya_win.frameGeometry().center())
            self.move(geo.topLeft())

    def copy_attr(self):
        self.clipboard_data = MayaLogic.copy_attributes()
        cmds.inViewMessage(amg="Copied", pos="topCenter", fade=True)

    def paste_attr(self):
        if hasattr(self, 'clipboard_data') and self.clipboard_data:
            t = MayaLogic.get_target_nodes(self.chk_trans.isChecked(), self.chk_shape.isChecked())
            MayaLogic.paste_attributes(self.clipboard_data, t)
            cmds.inViewMessage(amg="Pasted", pos="topCenter", fade=True)

    def set_enable(self, val):
        t = MayaLogic.get_target_nodes(self.chk_trans.isChecked(), self.chk_shape.isChecked())
        for n in t: cmds.setAttr(f"{n}.overrideEnabled", val)
        cmds.inViewMessage(amg=f"{'Enabled' if val else 'Disabled'}", pos="topCenter", fade=True)

    def reset_all(self):
        t = MayaLogic.get_target_nodes(self.chk_trans.isChecked(), self.chk_shape.isChecked())
        MayaLogic.reset_override(t)
        cmds.inViewMessage(amg="Reset", pos="topCenter", fade=True)

def show():
    # 1. Find the Maya Main Window to use as a parent
    maya_win = None
    for w in QtWidgets.QApplication.topLevelWidgets():
        if w.objectName() == "MayaWindow":
            maya_win = w
            break

    global my_drawing_tool
    try:
        my_drawing_tool.close()
        my_drawing_tool.deleteLater()
    except:
        pass
    
    # 2. Pass maya_win as the parent
    my_drawing_tool = CTRLColourChanger(parent=maya_win)
    my_drawing_tool.show()

show()

# -----------------------------------------------------------------------------
# AUTO-ICON UPDATER (Paste this at the bottom of any script)
# -----------------------------------------------------------------------------
def update_shelf_icon():
    """
    Automatically updates the Maya shelf button that launched this script.
    Checks if the button uses the default icon, and if so, swaps it for the custom one.
    """
    import maya.cmds as cmds
    import maya.mel as mel

    # --- CONFIGURATION (Edit these two lines) ---
    SCRIPT_NAME = "CTRLColourChanger"       # A unique word in your script's class or function name
    ICON_FILE   = "CTRLColourChanger_icon.png"   # The icon file name (must be in Maya's icon folder)
    # --------------------------------------------

    try:
        # 1. Get the currently active shelf tab (e.g., "Custom", "Rigging")
        current_shelf = mel.eval("tabLayout -q -selectTab $gShelfTopLevel")
        
        # 2. Get all buttons on that shelf
        buttons = cmds.shelfLayout(current_shelf, q=True, childArray=True) or []
        
        for btn in buttons:
            # 3. Read the Python command stored inside the button
            cmd = cmds.shelfButton(btn, q=True, command=True) or ""
            
            # 4. Check if this button runs THIS script
            if SCRIPT_NAME in cmd:
                # 5. Check if it's still using a default generic icon
                current_img = cmds.shelfButton(btn, q=True, image=True)
                if "pythonFamily" in current_img or "commandButton" in current_img:
                    # 6. Swap it!
                    cmds.shelfButton(btn, e=True, image=ICON_FILE)
                    print(f"Icon updated for {SCRIPT_NAME}")
    except Exception as e:
        print(f"Could not auto-update icon: {e}")

# Run it immediately
update_shelf_icon()