# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui
from util_func import (
    get_win_installed_software,
    extract_win_icon_from_file,
)
from global_vars import SoftwareStatusRole


class UiWgSoftware(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)
        self.cbx_safe = QtWidgets.QCheckBox("安全", window)
        self.cbx_unsafe = QtWidgets.QCheckBox("不安全", window)
        self.cbx_unknown = QtWidgets.QCheckBox("未知", window)
        self.cbx_safe.setChecked(True)
        self.cbx_unsafe.setChecked(True)
        self.cbx_unknown.setChecked(True)
        self.pbn_import_filter = QtWidgets.QPushButton("导入过滤文件", window)
        self.pbn_export_unknown = QtWidgets.QPushButton("导出未知", window)
        self.hly_top.addWidget(self.cbx_safe)
        self.hly_top.addWidget(self.cbx_unsafe)
        self.hly_top.addWidget(self.cbx_unknown)
        self.hly_top.addStretch(1)
        self.hly_top.addWidget(self.pbn_import_filter)
        self.hly_top.addWidget(self.pbn_export_unknown)

        self.lv_software = QtWidgets.QListView(window)
        self.vly_m.addWidget(self.lv_software)


class SoftwareListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_software = get_win_installed_software()
        self.all_software_wz_qic = {}
        blank_icon = QtGui.QIcon(":/images/blank_128.png")
        for s in self.all_software:
            self.all_software_wz_qic[s] = extract_win_icon_from_file(
                self.all_software[s],
                blank_icon
            )
        self.names = sorted(self.all_software.keys(), key=lambda x: x.lower())
        self.filter_dict = {}

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.names)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        row = index.row()
        name = self.names[row]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return name
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self.all_software_wz_qic[name]
        if role == SoftwareStatusRole:
            if name not in self.filter_dict:
                return -1
            else:
                return self.filter_dict[name]["safe"]


class WgSoftware(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiWgSoftware(self)

        self.software_list_model = SoftwareListModel(self)
        self.ui.lv_software.setModel(self.software_list_model)

        # self.ui.pbn_export_unknown.clicked.connect(self.on_pbn_export_unknown_clicked)

    def on_pbn_export_unknown_clicked(self):
        unknown_software = {}
        sl_model = self.ui.lv_software.model()  # type: SoftwareListModel
        for r in range(sl_model.rowCount()):
            idx = sl_model.index(r)
            name = sl_model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
            safe = sl_model.data(idx, SoftwareStatusRole)
            if safe == -1:
                unknown_software[name] = {"safe": -1}

        


