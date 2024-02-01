# coding: utf8
import sys
from PySide6 import QtWidgets
from mw_dailycheck import MwDailyCheck

import daily_check_rc

version = (0, 1, 0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MwDailyCheck(version)
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
