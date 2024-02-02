# coding: utf8
import os
import sys
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from mw_dailycheck import MwDailyCheck

import daily_check_rc

version = (0, 1, 0)

ORG_NAME = "JnPrograms"
APP_NAME = "DailyCheck"


def set_default_settings():
    plat = sys.platform
    user_path = os.path.expanduser("~")
    user_data_path_map = {
        "win32": {
            "Chrome": Path(user_path, r"AppData\Local\Google\Chrome\User Data"),
            "Edge": Path(user_path, r"AppData\Local\Microsoft\Edge\User Data"),
            "Brave": Path(user_path, r"AppData\Local\BraveSoftware\Brave-Browser\User Data"),
        },
        "darwin": {
            "Chrome": Path(user_path, "Library/Application Support/Google/Chrome"),
            "Edge": Path(user_path, "Library/Application Support/Microsoft Edge"),
            "Brave": Path(user_path, "Library/Application Support/BraveSoftware/Brave-Browser"),
        },
    }
    exec_path_map = {
        "win32": {
            "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "Brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        },
        "darwin": {
            "Chrome": r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "Edge": r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "Brave": r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        },
    }
    user_data_path = user_data_path_map[plat]
    exec_path = exec_path_map[plat]
    us = QtCore.QSettings()
    us.setValue("ChromeExec", exec_path["Chrome"])
    us.setValue("EdgeExec", exec_path["Edge"])
    us.setValue("BraveExec", exec_path["Brave"])
    us.setValue("ChromeData", user_data_path["Chrome"])
    us.setValue("EdgeData", user_data_path["Edge"])
    us.setValue("BraveData", user_data_path["Brave"])


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    set_default_settings()

    win = MwDailyCheck(version)
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
