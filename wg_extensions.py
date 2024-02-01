# coding: utf8
import json
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from util_ext import scan_extensions, ExtensionsData
from global_vars import (
    ExtensionStatusRole,
    ExtensionIdRole,
    accept_warning,
)


class UiWgExtensions(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.cmbx_browsers = QtWidgets.QComboBox(window)
        self.cbx_safe = QtWidgets.QCheckBox("安全", window)
        self.cbx_unsafe = QtWidgets.QCheckBox("不安全", window)
        self.cbx_unknown = QtWidgets.QCheckBox("未知", window)
        self.cbx_safe.setChecked(True)
        self.cbx_unsafe.setChecked(True)
        self.cbx_unknown.setChecked(True)
        self.cbx_chrome_compat = QtWidgets.QCheckBox("谷歌兼容模式", window)
        self.pbn_export_unknown = QtWidgets.QPushButton("导出未知", window)
        self.hly_top.addWidget(self.cmbx_browsers)
        self.hly_top.addWidget(self.cbx_safe)
        self.hly_top.addWidget(self.cbx_unsafe)
        self.hly_top.addWidget(self.cbx_unknown)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.cbx_chrome_compat)
        self.hly_top.addWidget(self.pbn_export_unknown)

        self.lv_extensions = QtWidgets.QListView(window)
        self.vly_m.addWidget(self.lv_extensions)


class ExtensionsListModel(QtCore.QAbstractListModel):

    def __init__(self, browser: str, parent=None):
        super().__init__(parent)
        self.all_extensions = {}  # type: ExtensionsData
        self.names = []  # type: list[tuple[str, str]]
        self.icons = {}  # type: dict[str, QtGui.QIcon]
        self.safe_info = {}  # type: dict[str, dict]
        self.blank_icon = QtGui.QIcon(":/images/blank_128.png")
        self.update(browser)

    def update(self, browser: str, is_chrome_compat=False):
        self.all_extensions.clear()
        self.names.clear()
        self.icons.clear()
        self.safe_info.clear()

        self.all_extensions = scan_extensions(browser, is_chrome_compat)
        for ext_id in self.all_extensions:
            name = self.all_extensions[ext_id].name
            icon = self.all_extensions[ext_id].icon
            self.names.append((ext_id, name))
            if len(icon) == 0:
                self.icons[ext_id] = self.blank_icon
            else:
                self.icons[ext_id] = QtGui.QIcon(icon)
        self.names.sort(key=lambda x: x[1].lower())

        with open("plg_db_v2.0.json", "r", encoding="utf-8") as f:
            self.safe_info = json.load(f)

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.names)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()
        ext_id, name = self.names[row]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return name
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self.icons[ext_id]
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            is_safe = self.data(index, ExtensionStatusRole)

            if is_safe is True:
                return QtGui.QBrush(QtGui.QColor("lightgreen"))
            elif is_safe is False:
                return QtGui.QBrush(QtGui.QColor("lightpink"))
            else:
                return QtGui.QBrush(QtCore.Qt.BrushStyle.NoBrush)
        if role == ExtensionStatusRole:
            if ext_id not in self.safe_info:
                return None
            else:
                return self.safe_info[ext_id]["safe"]
        if role == ExtensionIdRole:
            return ext_id


class BrowsersListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.browsers = ["Chrome", "Edge", "Brave"]
        self.icons = [
            QtGui.QIcon(":/images/browsers/chrome_32.png"),
            QtGui.QIcon(":/images/browsers/edge_32.png"),
            QtGui.QIcon(":/images/browsers/brave_32.png"),
        ]

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.browsers)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.browsers[row]
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self.icons[row]


class WgExtensions(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiWgExtensions(self)

        self.browsers_list_model = BrowsersListModel(self)
        self.ui.cmbx_browsers.setModel(self.browsers_list_model)

        browser = self.get_current_browser()
        self.extensions_list_model = ExtensionsListModel(browser, self)
        self.ui.lv_extensions.setModel(self.extensions_list_model)

        self.ui.cbx_chrome_compat.clicked.connect(self.on_cbx_chrome_compat_clicked)
        self.ui.cmbx_browsers.currentTextChanged.connect(self.on_cmbx_browsers_current_text_changed)
        self.ui.cbx_safe.clicked.connect(self.on_cbx_safe_clicked)
        self.ui.cbx_unsafe.clicked.connect(self.on_cbx_unsafe_clicked)
        self.ui.cbx_unknown.clicked.connect(self.on_cbx_unknown_clicked)
        self.ui.pbn_export_unknown.clicked.connect(self.on_pbn_export_unknown_clicked)

    def get_current_browser(self) -> str:
        return self.ui.cmbx_browsers.currentData(QtCore.Qt.ItemDataRole.DisplayRole)

    def show_all_rows(self):
        # 在 update 之前调用
        self.filters_clicked(True, True)
        self.filters_clicked(False, True)
        self.filters_clicked(None, True)

    def apply_rows_hidden(self):
        # 在 update 之后调用
        self.filters_clicked(True, self.ui.cbx_safe.isChecked())
        self.filters_clicked(False, self.ui.cbx_unsafe.isChecked())
        self.filters_clicked(None, self.ui.cbx_unknown.isChecked())

    def update_model(self, browser: str):
        # 切换浏览器时
        self.show_all_rows()
        self.extensions_list_model.update(browser, self.ui.cbx_chrome_compat.isChecked())
        self.apply_rows_hidden()

    def on_cbx_chrome_compat_clicked(self):
        self.update_model(self.get_current_browser())

    def on_cmbx_browsers_current_text_changed(self, text: str):
        self.update_model(text)

    def filters_clicked(self, safe_mark: bool | None, checked: bool):
        for row in range(self.extensions_list_model.rowCount()):
            idx = self.extensions_list_model.index(row)
            is_safe = self.extensions_list_model.data(idx, ExtensionStatusRole)
            if is_safe is safe_mark:
                self.ui.lv_extensions.setRowHidden(row, not checked)

    def on_cbx_safe_clicked(self, checked: bool):
        self.filters_clicked(True, checked)

    def on_cbx_unsafe_clicked(self, checked: bool):
        self.filters_clicked(False, checked)

    def on_cbx_unknown_clicked(self, checked: bool):
        self.filters_clicked(None, checked)

    def on_pbn_export_unknown_clicked(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "导出未知")
        if len(dirname) == 0:
            return

        browser = self.get_current_browser()
        ex_file = Path(dirname, f"未知插件_{browser}.json")
        if accept_warning(self, ex_file.exists(), "警告", "文件已存在，确认覆盖吗？"):
            return

        unknown_ext = {}
        for row in range(self.extensions_list_model.rowCount()):
            idx = self.extensions_list_model.index(row)
            is_safe = self.extensions_list_model.data(idx, ExtensionStatusRole)
            if is_safe is None:
                ext_id = self.extensions_list_model.data(idx, ExtensionIdRole)
                name = self.extensions_list_model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
                unknown_ext[ext_id] = {"name": name}

        with open(ex_file, "w", encoding="utf8") as f:
            json.dump(unknown_ext, f, indent=4, ensure_ascii=False)
        QtWidgets.QMessageBox.information(self, "提示", f"已导出到 {ex_file}")

