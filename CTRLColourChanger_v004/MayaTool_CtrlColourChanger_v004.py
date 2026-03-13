# ------------------------------------------------------------------
# CTRL ColourChanger v004
# ------------------------------------------------------------------
# Change Log:
# v004 — Unified UI theme matching the toolset stylesheet
# ------------------------------------------------------------------

import os
import json
import maya.cmds as cmds
from functools import partial

try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore

# ------------------------------------------------------------------
# STYLESHEET
# Same palette as the rest of the toolset:
#   Blue   #66b3ff  — focus rings, active indicators, Apply Side
#   Purple #bf80ff  — section titles (presets area)
#   Pink   #ff99ff  — section titles (side assignments)
#   Mint   #99ffcc  — section titles (actions)
#   Base dark       — #1e1e24 / #26262e
# ------------------------------------------------------------------
STYLESHEET = """
QWidget {
    background-color: #1e1e24;
    color: #d0d0d8;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
}

QDialog {
    background-color: #18181e;
    border: 1px solid #111116;
}

/* === SECTION FRAMES === */
QFrame#sectionFrame {
    background-color: #26262e;
    border: 1px solid #32323c;
    border-radius: 6px;
}

/* === LABELS === */
QLabel {
    color: #88889a;
    font-size: 11px;
    background: transparent;
}
QLabel#sectionTitle {
    color: #66b3ff;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
    background: transparent;
}
QLabel#sectionTitlePurple {
    color: #bf80ff;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
    background: transparent;
}
QLabel#sectionTitlePink {
    color: #ff99ff;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
    background: transparent;
}
QLabel#sectionTitleMint {
    color: #99ffcc;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
    background: transparent;
}

/* === LINE EDITS === */
QLineEdit {
    background-color: #14141a;
    border: 1px solid #36363f;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0ea;
    font-weight: bold;
    selection-background-color: #66b3ff;
    selection-color: #0a0a12;
}
QLineEdit:focus {
    border: 1px solid #66b3ff;
    background-color: #1a1a22;
}
QLineEdit:hover {
    border: 1px solid #505060;
}

/* === BUTTONS — Default === */
QPushButton {
    background-color: #2e2e38;
    border: 1px solid #3e3e4a;
    border-radius: 4px;
    padding: 4px 10px;
    color: #b0b0c0;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #38384a;
    border: 1px solid #58587a;
    color: #e0e0f0;
}
QPushButton:pressed {
    background-color: #1e1e28;
}

/* === ACCENT BUTTON — Blue === */
QPushButton#accentButton {
    background-color: #1e2a3a;
    border: 1px solid #3a6080;
    border-radius: 4px;
    color: #76acce;
    font-weight: bold;
    min-height: 22px;
    padding: 4px 10px;
}
QPushButton#accentButton:hover {
    background-color: #243650;
    border: 1px solid #66b3ff;
    color: #a0c8e8;
}
QPushButton#accentButton:pressed {
    background-color: #141e28;
}

/* === ENABLE BUTTON — Green === */
QPushButton#enableButton {
    background-color: #1e2e24;
    border: 1px solid #508060;
    border-radius: 4px;
    color: #7baf8a;
    font-weight: bold;
    min-height: 22px;
    padding: 4px 10px;
}
QPushButton#enableButton:hover {
    background-color: #263c2e;
    border: 1px solid #7baf8a;
    color: #a0c8aa;
}
QPushButton#enableButton:pressed {
    background-color: #141e18;
}

/* === DISABLE BUTTON — Red === */
QPushButton#disableButton {
    background-color: #2a1e1e;
    border: 1px solid #5a3030;
    border-radius: 4px;
    color: #a06060;
    font-weight: bold;
    min-height: 22px;
    padding: 4px 10px;
}
QPushButton#disableButton:hover {
    background-color: #382424;
    border: 1px solid #804040;
    color: #c07878;
}
QPushButton#disableButton:pressed {
    background-color: #1a1010;
}

/* === RESET BUTTON — Dim neutral === */
QPushButton#resetButton {
    background-color: #242430;
    border: 1px solid #3e3e50;
    border-radius: 4px;
    color: #606080;
    font-weight: bold;
    min-height: 22px;
    padding: 4px 10px;
}
QPushButton#resetButton:hover {
    background-color: #2e2e3e;
    border: 1px solid #505070;
    color: #9090b0;
}
QPushButton#resetButton:pressed {
    background-color: #1a1a24;
}

/* === CHECKBOXES === */
QCheckBox {
    color: #9090a8;
    spacing: 5px;
    background: transparent;
}
QCheckBox::indicator {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    border: 1px solid #484860;
    background-color: #14141a;
}
QCheckBox::indicator:checked {
    background-color: #66b3ff;
    border: 1px solid #99ccff;
}
QCheckBox::indicator:hover {
    border: 1px solid #66b3ff;
}
QCheckBox:checked {
    color: #99ccff;
}

/* === GROUP BOX === */
QGroupBox {
    border: 1px solid #32323c;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 6px;
    color: #66b3ff;
    font-size: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    letter-spacing: 1.5px;
}

/* === LIST WIDGETS === */
QListWidget {
    background-color: #1e1e24;
    border: 1px solid #32323c;
    border-radius: 4px;
    outline: 0;
}
QListWidget::item {
    padding-top: 5px;
    padding-bottom: 8px;
    outline: 0;
}
QListWidget::item:selected {
    background-color: #2a3650;
    border: 1px solid #66b3ff;
    border-radius: 3px;
}

/* === TEXT EDIT (JSON editor) === */
QTextEdit {
    background-color: #14141a;
    border: 1px solid #36363f;
    border-radius: 4px;
    color: #e0e0ea;
    font-family: "Courier New", monospace;
}

/* === SCROLL AREA === */
QScrollArea {
    border: none;
    background-color: #1e1e24;
}
QScrollBar:vertical {
    background: #1e1e24;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #38383f;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #66b3ff;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* === MENU === */
QMenu {
    background-color: #26262e;
    border: 1px solid #3a3a48;
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    padding: 5px 20px 5px 10px;
    border-radius: 3px;
    color: #d0d0d8;
}
QMenu::item:selected {
    background-color: #2e2e3e;
    color: #66b3ff;
}
QMenu::separator {
    height: 1px;
    background: #3a3a48;
    margin: 3px 6px;
}
"""

# ------------------------------------------------------------------
# SECTION FRAME HELPER  (mirrors the rest of the toolset)
# ------------------------------------------------------------------
def make_section(title, parent_layout, title_color="blue"):
    frame = QtWidgets.QFrame()
    frame.setObjectName("sectionFrame")
    frame.setFrameShape(QtWidgets.QFrame.StyledPanel)

    outer = QtWidgets.QVBoxLayout(frame)
    outer.setContentsMargins(10, 8, 10, 10)
    outer.setSpacing(6)

    lbl = QtWidgets.QLabel(title.upper())
    name_map = {
        "blue":   "sectionTitle",
        "purple": "sectionTitlePurple",
        "pink":   "sectionTitlePink",
        "mint":   "sectionTitleMint",
    }
    lbl.setObjectName(name_map.get(title_color, "sectionTitle"))
    outer.addWidget(lbl)

    inner = QtWidgets.QVBoxLayout()
    inner.setSpacing(6)
    outer.addLayout(inner)

    parent_layout.addWidget(frame)
    return inner


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
        if len(hex_str) != 6: return (0, 0, 0)
        srgb = tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return ColorUtils.srgb_to_linear(srgb)

    @staticmethod
    def get_ui_color_from_data(data):
        if isinstance(data, str): return QtGui.QColor(data)
        elif isinstance(data, int):
            if data < 0: return QtGui.QColor(200, 200, 200)
            try:
                rgb = cmds.colorIndex(data, query=True)
                return QtGui.QColor.fromRgbF(*rgb)
            except: return QtGui.QColor(100, 100, 100)
        elif isinstance(data, (list, tuple)):
            if len(data) < 3: return QtGui.QColor(0, 0, 0)
            is_float = any(isinstance(x, float) for x in data)
            is_large = any(x > 1.0 for x in data)
            if is_large or not is_float:
                return QtGui.QColor(int(data[0]), int(data[1]), int(data[2]))
            else:
                return QtGui.QColor.fromRgbF(data[0], data[1], data[2])
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
            except Exception as e:
                print(f"Error setting {node}: {e}")

    @staticmethod
    def copy_attributes():
        sel = cmds.ls(selection=True)
        if not sel: return None
        node = sel[0]
        return {
            "useRGB":     cmds.getAttr(f"{node}.overrideRGBColors"),
            "colorIndex": cmds.getAttr(f"{node}.overrideColor"),
            "colorRGB":   cmds.getAttr(f"{node}.overrideColorRGB")[0]
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
    dropped = QtCore.Signal()

    def __init__(self, parent=None):
        super(ColorListWidget, self).__init__(parent)
        self.setViewMode(QtWidgets.QListWidget.IconMode)
        self.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setIconSize(QtCore.QSize(30, 30))
        self.setGridSize(QtCore.QSize(40, 75))
        self.setSpacing(2)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e24;
                border: 1px solid #32323c;
                border-radius: 4px;
                outline: 0;
            }
            QListWidget::item {
                padding-top: 5px;
                padding-bottom: 8px;
                outline: 0;
            }
            QListWidget::item:selected {
                background-color: #2a3650;
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
            painter.fillRect(self.drop_indicator_rect, QtGui.QColor("#66b3ff"))

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
            self.dropped.emit()
        else:
            super(ColorListWidget, self).dropEvent(event)


class GroupHeader(QtWidgets.QWidget):
    toggled = QtCore.Signal(bool)

    def __init__(self, title, parent=None):
        super(GroupHeader, self).__init__(parent)
        self._expanded = True
        self.setStyleSheet("background-color: #26262e; border-radius: 4px;")

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(8)

        self.grip = QtWidgets.QLabel("::")
        self.grip.setToolTip("Drag to Reorder Group")
        self.grip.setStyleSheet("color: #484860; font-weight: bold;")
        self.grip.setCursor(QtCore.Qt.SizeAllCursor)
        layout.addWidget(self.grip)

        self.arrow = QtWidgets.QLabel(u"\u25BC")
        self.arrow.setStyleSheet("color: #66b3ff; font-weight: bold; background: transparent;")
        self.arrow.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.arrow)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("color: #d0d0d8; font-weight: bold; font-size: 12px; background: transparent;")
        self.title_label.setCursor(QtCore.Qt.PointingHandCursor)
        layout.addWidget(self.title_label)

        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.line.setStyleSheet("background-color: #32323c; max-height: 1px; border: none;")
        layout.addWidget(self.line)

    def mousePressEvent(self, event):
        if self.childAt(event.pos()) == self.grip:
            event.ignore()
            return
        if event.button() == QtCore.Qt.LeftButton:
            self._expanded = not self._expanded
            self.arrow.setText(u"\u25BC" if self._expanded else u"\u25B6")
            self.toggled.emit(self._expanded)
            event.accept()


class ResizeHandle(QtWidgets.QWidget):
    resized = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(ResizeHandle, self).__init__(parent)
        self.setFixedHeight(8)
        self.setCursor(QtCore.Qt.SizeVerCursor)
        self.start_y = 0

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor("#1e1e24"))
        painter.drawRect(self.rect())
        painter.setPen(QtGui.QColor("#484860"))
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

    def __init__(self, title, content_widget=None, parent=None, start_collapsed=False):
        super(CollapsibleGroup, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 4)
        self.layout.setSpacing(2)

        self.header = GroupHeader(title)
        self.header.toggled.connect(self.on_toggle)
        self.layout.addWidget(self.header)

        self.list_widget = content_widget if content_widget else ColorListWidget()
        if content_widget is None:
            self.list_widget.setFixedHeight(60)
        self.layout.addWidget(self.list_widget)

        self.handle = ResizeHandle()
        self.handle.resized.connect(self.on_resize)
        self.layout.addWidget(self.handle)

        self.last_height = self.list_widget.height()

        if start_collapsed:
            self.header._expanded = False
            self.header.arrow.setText(u"\u25B6")
            self.list_widget.setVisible(False)
            self.handle.setVisible(False)

    def on_toggle(self, expanded):
        self.list_widget.setVisible(expanded)
        self.handle.setVisible(expanded)
        if expanded:
            self.list_widget.setFixedHeight(self.last_height)
        else:
            self.last_height = self.list_widget.height()
        self.sizeChanged.emit()

    def on_resize(self, dy):
        new_h = max(20, self.list_widget.height() + dy)
        self.list_widget.setFixedHeight(new_h)
        self.last_height = new_h
        self.sizeChanged.emit()


class GroupListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(GroupListWidget, self).__init__(parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                outline: 0;
            }
            QListWidget::item {
                border: none;
                outline: 0;
            }
        """)
        self.setResizeMode(QtWidgets.QListWidget.Adjust)


# ------------------------------------------------------------------
# JSON EDITOR DIALOG
# ------------------------------------------------------------------
class JsonEditorDialog(QtWidgets.QDialog):
    def __init__(self, current_data, parent=None):
        super(JsonEditorDialog, self).__init__(parent)
        self.setWindowTitle("Edit Presets (JSON)")
        self.resize(600, 700)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(STYLESHEET)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        info = QtWidgets.QLabel('Format:  [ { "group": "Name", "colors": [...] } ]')
        info.setObjectName("sectionTitle")
        layout.addWidget(info)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setFont(QtGui.QFont("Courier New", 10))
        self.text_edit.setText(json.dumps(current_data, indent=4))
        layout.addWidget(self.text_edit)

        btn_row = QtWidgets.QHBoxLayout()
        btn_save = QtWidgets.QPushButton("Save && Apply")
        btn_save.setObjectName("accentButton")
        btn_save.clicked.connect(self.validate_and_save)
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        self.result_data = None

    def validate_and_save(self):
        try:
            data = json.loads(self.text_edit.toPlainText())
            if not isinstance(data, list): raise ValueError("Root must be a list.")
            for grp in data:
                if "group" not in grp or "colors" not in grp:
                    raise ValueError("Invalid group structure.")
            self.result_data = data
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "JSON Error", str(e))


# ------------------------------------------------------------------
# MAIN TOOL
# ------------------------------------------------------------------
class CTRLColourChanger(QtWidgets.QDialog):

    WINDOW_TITLE = "CTRL Colour Changer"

    def __init__(self, parent=None):
        super(CTRLColourChanger, self).__init__(parent)

        self.side_colors  = {"Left": None, "Center": None, "Right": None}
        self.side_previews = {}
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

        self.load_settings()
        self.setup_ui()
        self.rebuild_groups_ui()
        self.center_on_maya()

    # ------------------------------------------------------------------
    def setup_ui(self):
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(400, 780)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setStyleSheet(STYLESHEET)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ── SIDE ASSIGNMENTS ───────────────────────────
        self._build_side_section(root)

        # ── TARGETS ────────────────────────────────────
        targets_inner = make_section("Targets", root, "blue")
        targets_row = QtWidgets.QHBoxLayout()
        self.chk_trans = QtWidgets.QCheckBox("Transforms")
        self.chk_trans.setChecked(True)
        self.chk_shape = QtWidgets.QCheckBox("Shapes")
        targets_row.addWidget(self.chk_trans)
        targets_row.addWidget(self.chk_shape)
        targets_row.addStretch()
        targets_inner.addLayout(targets_row)

        # ── PRESETS ────────────────────────────────────
        presets_inner = make_section("Colour Presets", root, "purple")

        self.group_list_widget = GroupListWidget()
        presets_inner.addWidget(self.group_list_widget)

        btn_row = QtWidgets.QHBoxLayout()
        btn_add = QtWidgets.QPushButton("Add New Group")
        btn_add.clicked.connect(self.add_new_group)

        self.btn_json = QtWidgets.QPushButton("Edit JSON...")
        self.btn_json.clicked.connect(self.edit_json)
        self.btn_json.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.btn_json.customContextMenuRequested.connect(self.open_json_folder_menu)

        btn_row.addWidget(btn_add)
        btn_row.addWidget(self.btn_json)
        presets_inner.addLayout(btn_row)

        # ── ACTIONS ────────────────────────────────────
        actions_inner = make_section("Actions", root, "mint")

        copy_paste_row = QtWidgets.QHBoxLayout()
        b_copy = QtWidgets.QPushButton("Copy")
        b_copy.clicked.connect(self.copy_attr)
        b_paste = QtWidgets.QPushButton("Paste")
        b_paste.clicked.connect(self.paste_attr)
        copy_paste_row.addWidget(b_copy)
        copy_paste_row.addWidget(b_paste)
        actions_inner.addLayout(copy_paste_row)

        en_dis_row = QtWidgets.QHBoxLayout()
        b_en = QtWidgets.QPushButton("Enable")
        b_en.setObjectName("enableButton")
        b_en.clicked.connect(lambda: self.set_enable(True))
        b_dis = QtWidgets.QPushButton("Disable")
        b_dis.setObjectName("disableButton")
        b_dis.clicked.connect(lambda: self.set_enable(False))
        en_dis_row.addWidget(b_en)
        en_dis_row.addWidget(b_dis)
        actions_inner.addLayout(en_dis_row)

        b_rst = QtWidgets.QPushButton("RESET ALL OVERRIDES")
        b_rst.setObjectName("resetButton")
        b_rst.clicked.connect(self.reset_all)
        actions_inner.addWidget(b_rst)

    # ------------------------------------------------------------------
    def _build_side_section(self, parent_layout):
        """Builds the collapsible Side Assignments section."""
        self.side_content = QtWidgets.QWidget()
        self.side_content.setStyleSheet("background-color: #26262e; border-radius: 4px;")
        self.side_content.setFixedHeight(90)

        lay = QtWidgets.QVBoxLayout(self.side_content)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(6)

        boxes_row = QtWidgets.QHBoxLayout()
        for side in ["Left", "Center", "Right"]:
            col = QtWidgets.QVBoxLayout()
            col.setSpacing(3)

            lbl = QtWidgets.QLabel(side)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 10px; color: #88889a; background: transparent;")

            box = QtWidgets.QFrame()
            box.setFixedSize(64, 26)
            box.setStyleSheet("background-color: #14141a; border: 1px solid #484860; border-radius: 4px;")

            self.side_previews[side] = box
            col.addWidget(lbl)
            col.addWidget(box)
            boxes_row.addLayout(col)

        lay.addLayout(boxes_row)

        apply_btn = QtWidgets.QPushButton("Apply Side Colours")
        apply_btn.setObjectName("accentButton")
        apply_btn.setFixedHeight(24)
        apply_btn.clicked.connect(self.apply_side_logic)
        lay.addWidget(apply_btn)

        self.side_group = CollapsibleGroup(
            "Side Assignments",
            content_widget=self.side_content,
            start_collapsed=True
        )
        parent_layout.addWidget(self.side_group)

    # ------------------------------------------------------------------
    def set_side_color(self, side, color_data):
        self.side_colors[side] = color_data
        c = ColorUtils.get_ui_color_from_data(color_data)
        self.side_previews[side].setStyleSheet(
            f"background-color: {c.name()}; border: 1px solid #66b3ff; border-radius: 4px;"
        )

    def apply_side_logic(self):
        targets = MayaLogic.get_target_nodes(self.chk_trans.isChecked(), self.chk_shape.isChecked())
        for node in targets:
            x = cmds.xform(node, q=True, ws=True, t=True)[0]
            col = self.side_colors["Left"] if x > 0.1 else \
                  self.side_colors["Right"] if x < -0.1 else \
                  self.side_colors["Center"]
            if col: MayaLogic.apply_smart_override([node], col)
        cmds.inViewMessage(amg="Side Colors Applied", pos="topCenter", fade=True)

    # ------------------------------------------------------------------
    def get_settings_path(self):
        user_app_dir = cmds.internalVar(userAppDir=True)
        return os.path.join(user_app_dir, "scripts", "ctrl_colour_presets.json")

    def save_settings(self):
        self.sync_order_from_ui()
        path = self.get_settings_path()
        try:
            with open(path, 'w') as f:
                json.dump(self.grouped_presets, f, indent=4)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def load_settings(self):
        path = self.get_settings_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    self.grouped_presets = json.loads(f.read())
            except Exception as e:
                print(f"Error loading presets: {e}")

    def delete_and_save(self, list_widget, item):
        list_widget.takeItem(list_widget.row(item))
        self.save_settings()

    def open_json_folder_menu(self, pos):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet(STYLESHEET)
        menu.addAction("Open File Location").triggered.connect(self.reveal_json_in_explorer)
        menu.exec_(self.btn_json.mapToGlobal(pos))

    def reveal_json_in_explorer(self):
        path = self.get_settings_path()
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder))

    # ------------------------------------------------------------------
    def rebuild_groups_ui(self):
        self.group_list_widget.clear()
        for grp_data in self.grouped_presets:
            self.create_group_item(grp_data)

    def create_group_item(self, grp_data):
        title  = grp_data.get("group", "Untitled")
        colors = grp_data.get("colors", [])

        group_wid = CollapsibleGroup(title)
        list_w = group_wid.list_widget
        list_w.dropped.connect(self.save_settings)

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

    def add_item_to_list(self, list_widget, color_val, name):
        item = QtWidgets.QListWidgetItem(name)
        item.setData(QtCore.Qt.UserRole, color_val)
        ui_color = ColorUtils.get_ui_color_from_data(color_val)
        pix = QtGui.QPixmap(45, 45)
        pix.fill(ui_color)
        item.setIcon(QtGui.QIcon(pix))
        list_widget.addItem(item)

    # ------------------------------------------------------------------
    def on_item_clicked(self, item):
        raw_data = item.data(QtCore.Qt.UserRole)
        targets = MayaLogic.get_target_nodes(self.chk_trans.isChecked(), self.chk_shape.isChecked())
        MayaLogic.apply_smart_override(targets, raw_data)
        if targets:
            cmds.inViewMessage(amg=f"Applied {item.text()}", pos="topCenter", fade=True)

    def add_new_group(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "New Group", "Group Name:")
        if ok and text:
            self.grouped_presets.append({"group": text, "colors": []})
            self.rebuild_groups_ui()
            self.group_list_widget.scrollToBottom()

    def edit_json(self):
        self.sync_order_from_ui()
        dlg = JsonEditorDialog(self.grouped_presets, self)
        if dlg.exec_():
            self.grouped_presets = dlg.result_data
            self.rebuild_groups_ui()
            self.save_settings()
            cmds.inViewMessage(amg="Layout Updated & Saved", pos="topCenter", fade=True)

    def sync_order_from_ui(self):
        new_presets = []
        for i in range(self.group_list_widget.count()):
            item   = self.group_list_widget.item(i)
            widget = self.group_list_widget.itemWidget(item)
            colors = []
            for r in range(widget.list_widget.count()):
                c_item = widget.list_widget.item(r)
                colors.append([c_item.data(QtCore.Qt.UserRole), c_item.text()])
            new_presets.append({"group": widget.header.title_label.text(), "colors": colors})
        self.grouped_presets = new_presets

    def open_context_menu(self, list_widget, pos):
        item = list_widget.itemAt(pos)
        menu = QtWidgets.QMenu()
        menu.setStyleSheet(STYLESHEET)

        if item:
            raw_data = item.data(QtCore.Qt.UserRole)

            side_menu = menu.addMenu("Assign to Side...")
            side_menu.setStyleSheet(STYLESHEET)
            side_menu.addAction("Set to Left").triggered.connect(
                partial(self.set_side_color, "Left", raw_data))
            side_menu.addAction("Set to Center").triggered.connect(
                partial(self.set_side_color, "Center", raw_data))
            side_menu.addAction("Set to Right").triggered.connect(
                partial(self.set_side_color, "Right", raw_data))
            menu.addSeparator()

            c = ColorUtils.get_ui_color_from_data(raw_data)
            hex_s = c.name().upper()
            rgb_s = f"{c.redF():.3f}, {c.greenF():.3f}, {c.blueF():.3f}"
            menu.addAction(f"Copy Hex  ({hex_s})").triggered.connect(lambda: self.copy_to_clip(hex_s))
            menu.addAction(f"Copy RGB  ({rgb_s})").triggered.connect(lambda: self.copy_to_clip(rgb_s))
            menu.addSeparator()
            menu.addAction("Delete Item").triggered.connect(
                lambda: self.delete_and_save(list_widget, item))
        else:
            menu.addAction("Add Color Here").triggered.connect(
                lambda: self.add_color_to_list(list_widget))

        menu.exec_(list_widget.mapToGlobal(pos))

    def copy_to_clip(self, text):
        QtGui.QGuiApplication.clipboard().setText(text)
        cmds.inViewMessage(amg=f"Copied: {text}", pos="topCenter", fade=True)

    def add_color_to_list(self, list_widget):
        col = QtWidgets.QColorDialog.getColor()
        if col.isValid():
            name, ok = QtWidgets.QInputDialog.getText(self, "Name", "Color Name:")
            if ok:
                self.add_item_to_list(list_widget, col.name(), name or "Custom")
                self.save_settings()

    # ------------------------------------------------------------------
    def center_on_maya(self):
        for w in QtWidgets.QApplication.topLevelWidgets():
            if w.objectName() == "MayaWindow":
                geo = self.frameGeometry()
                geo.moveCenter(w.frameGeometry().center())
                self.move(geo.topLeft())
                break

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


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
def show():
    maya_win = None
    for w in QtWidgets.QApplication.topLevelWidgets():
        if w.objectName() == "MayaWindow":
            maya_win = w
            break

    global my_colour_tool
    try:
        my_colour_tool.close()
        my_colour_tool.deleteLater()
    except Exception:
        pass

    my_colour_tool = CTRLColourChanger(parent=maya_win)
    my_colour_tool.show()

# show()


# ------------------------------------------------------------------
# AUTO-ICON UPDATER
# ------------------------------------------------------------------
def update_shelf_icon():
    import maya.mel as mel
    SCRIPT_NAME = "CTRLColourChanger"
    ICON_FILE   = "CTRLColourChanger_icon.png"
    try:
        current_shelf = mel.eval("tabLayout -q -selectTab $gShelfTopLevel")
        buttons = cmds.shelfLayout(current_shelf, q=True, childArray=True) or []
        for btn in buttons:
            cmd = cmds.shelfButton(btn, q=True, command=True) or ""
            if SCRIPT_NAME in cmd:
                current_img = cmds.shelfButton(btn, q=True, image=True)
                if "pythonFamily" in current_img or "commandButton" in current_img:
                    cmds.shelfButton(btn, e=True, image=ICON_FILE)
                    print(f"Icon updated for {SCRIPT_NAME}")
    except Exception as e:
        print(f"Could not auto-update icon: {e}")

# update_shelf_icon()