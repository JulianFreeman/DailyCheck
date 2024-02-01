# coding: utf8
import os
import wmi
import json
import win32gui
import requests
import subprocess
from pathlib import Path
from PySide6.QtCore import QDir, QSettings
from PySide6.QtGui import QImage, QIcon, QPixmap


def get_isp_name() -> str:
    req = requests.get("https://ipinfo.io/")
    if req.status_code == 200:
        try:
            data = json.loads(req.content)
            return data.get("org", "[Not found]")
        except json.JSONDecodeError:
            return "[Decode Error]"
    return "[Return Error]"


def get_win_manufacturer() -> list[str]:
    w = wmi.WMI()
    cs_ls = w.Win32_ComputerSystem()
    if len(cs_ls) > 0:
        cs = cs_ls[0]
        return [cs.model, cs.Manufacturer]
    return []


def get_win_license() -> str:
    temp_out = str(Path(QDir.tempPath(), "lic.txt"))
    return_code = subprocess.call(
        rf'cscript /Nologo /U "C:\Windows\System32\slmgr.vbs" /dlv >{temp_out}',
        shell=True,
    )
    if return_code == 0:
        with open(temp_out, "r", encoding="utf-16-le") as f:
            return f.read()
    return ""


def get_win_installed_software() -> dict[str, str]:

    def gather_software(path: str, software_dict: dict[str, str]):
        reg = QSettings(path, QSettings.Format.NativeFormat)
        soft = reg.childGroups()
        for s in soft:
            c = QSettings(path + "\\" + s.split("/")[0], QSettings.Format.NativeFormat)
            name = str(c.value("DisplayName"))
            if name == "None":
                continue
            icon = str(c.value("DisplayIcon"))
            software_dict[name] = icon

    all_software = {}
    gather_software(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", all_software)
    gather_software(r"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", all_software)
    gather_software(r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall", all_software)

    return all_software


def extract_win_icon_from_file(icon: str, default: QIcon) -> QIcon:
    if icon == "None":
        return default
    if icon.endswith(",0"):
        icon = icon[:-2]
    icon = icon.replace('"', "")
    icon = icon.replace("'", "")
    if not os.path.exists(icon):
        return default
    if not icon.endswith(("exe", "EXE")):
        return QIcon(icon)

    large, small = win32gui.ExtractIconEx(icon, 0)
    if len(small) > 0:
        win32gui.DestroyIcon(small[0])
    if len(large) > 0:
        image = QImage.fromHICON(large[0])
        return QIcon(QPixmap(image))
    else:
        return default

