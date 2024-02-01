# coding: utf8
import sys
from PySide6 import QtWidgets
from wg_basic import WgBasic
from wg_software import WgSoftware

import daily_check_rc


class UiMainWindow(object):

    def __init__(self, window: QtWidgets.QWidget):
        window.resize(800, 600)
        window.setWindowTitle("日常检查工具")

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.tw_m = QtWidgets.QTabWidget(window)
        self.vly_m.addWidget(self.tw_m)

        self.wg_basic = WgBasic(window)
        self.wg_software = WgSoftware(window)

        # self.tw_m.addTab(self.wg_basic, "基本信息")
        self.tw_m.addTab(self.wg_software, "已安装软件")


class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiMainWindow(self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
