# coding: utf8
from PySide6 import QtWidgets
from util_func import (
    get_isp_name,
    get_win_manufacturer,
    get_win_license,
)


class UiWgBasic(object):

    def __init__(self, window: QtWidgets.QWidget):
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.gbx_isp = QtWidgets.QGroupBox("网络运营商", window)
        self.vly_m.addWidget(self.gbx_isp)
        self.vly_gbx_isp = QtWidgets.QVBoxLayout()
        self.gbx_isp.setLayout(self.vly_gbx_isp)

        self.lne_isp = QtWidgets.QLineEdit(self.gbx_isp)
        self.lne_isp.setReadOnly(True)
        self.vly_gbx_isp.addWidget(self.lne_isp)

        self.gbx_manu = QtWidgets.QGroupBox("系统制造商", window)
        self.vly_m.addWidget(self.gbx_manu)
        self.hly_gbx_manu = QtWidgets.QHBoxLayout()
        self.gbx_manu.setLayout(self.hly_gbx_manu)
        self.lb_model = QtWidgets.QLabel("型号：", self.gbx_manu)
        self.lne_model = QtWidgets.QLineEdit(self.gbx_manu)
        self.lne_model.setReadOnly(True)
        self.lb_manufacturer = QtWidgets.QLabel("制造商：", self.gbx_manu)
        self.lne_manufacturer = QtWidgets.QLineEdit(self.gbx_manu)
        self.lne_manufacturer.setReadOnly(True)
        self.hly_gbx_manu.addWidget(self.lb_model)
        self.hly_gbx_manu.addWidget(self.lne_model)
        self.hly_gbx_manu.addWidget(self.lb_manufacturer)
        self.hly_gbx_manu.addWidget(self.lne_manufacturer)

        self.gbx_license = QtWidgets.QGroupBox("许可证", window)
        self.vly_m.addWidget(self.gbx_license)
        self.vly_gbx_license = QtWidgets.QVBoxLayout()
        self.gbx_license.setLayout(self.vly_gbx_license)
        self.pte_license = QtWidgets.QPlainTextEdit(self.gbx_license)
        self.vly_gbx_license.addWidget(self.pte_license)
        self.pte_license.setReadOnly(True)

        # self.vly_m.addStretch(1)


class WgBasic(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiWgBasic(self)

        self.ui.lne_isp.setText(get_isp_name())
        model, manufacturer = get_win_manufacturer()
        self.ui.lne_model.setText(model)
        self.ui.lne_manufacturer.setText(manufacturer)

        self.ui.pte_license.setPlainText(get_win_license())

