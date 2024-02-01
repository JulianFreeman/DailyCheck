# coding: utf8
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from global_vars import get_with_chained_keys


PLAT = sys.platform
USER_PATH = os.path.expanduser("~")

USER_DATA_PATH_MAP = {
    "win32": {
        "Chrome": Path(USER_PATH, "AppData", "Local", "Google", "Chrome", "User Data"),
        "Edge": Path(USER_PATH, "AppData", "Local", "Microsoft", "Edge", "User Data"),
        "Brave": Path(USER_PATH, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data"),
    },
    "darwin": {
        "Chrome": Path(USER_PATH, "Library", "Application Support", "Google", "Chrome"),
        "Edge": Path(USER_PATH, "Library", "Application Support", "Microsoft Edge"),
        "Brave": Path(USER_PATH, "Library", "Application Support", "BraveSoftware", "Brave-Browser"),
    },
}

USER_DATA_PATH = USER_DATA_PATH_MAP[PLAT]


@dataclass
class ProfileNode(object):
    gaia_given_name: str
    gaia_name: str
    name: str
    shortcut_name: str
    user_name: str


ProfilesData = dict[str, ProfileNode]


def scan_profiles(browser: str) -> ProfilesData:
    local_state_path = Path(USER_DATA_PATH[browser], "Local State")
    local_state_data: dict = json.loads(local_state_path.read_text(encoding="utf8"))
    info_cache_data: dict = get_with_chained_keys(local_state_data, ["profile", "info_cache"])

    profiles_data: ProfilesData = {}

    for profile_id in info_cache_data:
        profile_data: dict = info_cache_data[profile_id]
        profile_node = ProfileNode(
            gaia_given_name=profile_data.get("gaia_given_name", ""),
            gaia_name=profile_data.get("gaia_name", ""),
            name=profile_data.get("name", ""),
            shortcut_name=profile_data.get("shortcut_name", ""),
            user_name=profile_data.get("user_name"),
        )
        profiles_data[profile_id] = profile_node

    return profiles_data


@dataclass
class ExtensionNode(object):
    icon: str
    name: str
    # path: str
    profiles: list[str] = field(default_factory=list)


ExtensionsData = dict[str, ExtensionNode]


def get_extension_icon_path(ext_icons: dict[str, str], ext_path: str, profile_path: Path) -> str:
    if len(ext_icons) == 0:
        return ""

    if "128" in ext_icons:
        icon_file = ext_icons["128"]
    else:
        icon_file = ext_icons[str(max(map(lambda x: int(x), ext_icons.keys())))]
    # 如果路径以 / 开头，会被认为是根而忽略其他，因此需要检查一下
    if icon_file.startswith("/"):
        icon_file = icon_file[1:]

    full_path = Path(profile_path, "Extensions", ext_path, icon_file)
    return str(full_path)


def scan_extensions(browser: str, is_chrome_compat=False) -> ExtensionsData:
    profile_data = scan_profiles(browser)
    extensions_data: ExtensionsData = {}

    browser_data_path = USER_DATA_PATH[browser]
    if browser == "Chrome" and is_chrome_compat:
        pref_file = "Preferences"
    else:
        pref_file = "Secure Preferences"

    for profile_id in profile_data:
        profile_path = Path(browser_data_path, profile_id)
        secure_pref_path = Path(profile_path, pref_file)
        secure_pref_data: dict = json.loads(secure_pref_path.read_text(encoding="utf8"))
        ext_settings_data: dict = get_with_chained_keys(secure_pref_data, ["extensions", "settings"], dict())

        for ext_id in ext_settings_data:
            ext_data: dict = ext_settings_data[ext_id]
            # 这里插件有几种情况
            ext_path: str = ext_data.get("path", "")
            if len(ext_path) == 0:
                # 如果 path 是空，则该插件可能是一些内部插件，不予收集
                continue
            elif not (ext_path.startswith(ext_id) or os.path.exists(ext_path)):
                # 如果 path 以插件 ID 开头，则为商店安装的插件，
                # 如果不是以插件 ID 开头，但是是一个存在的路径，则为离线安装的插件
                # 否则，可能也是内部插件，不予收集
                continue
            ext_manifest: dict = ext_data.get("manifest", {})
            if len(ext_manifest) == 0:
                # 如果 manifest 为空，则该插件可能是离线插件，需要额外找它的 manifest
                ext_manifest_path = Path(ext_path, "manifest.json")
                ext_manifest: dict = json.loads(ext_manifest_path.read_text(encoding="utf8"))

            if ext_id not in extensions_data:
                ext_node = ExtensionNode(
                    icon=get_extension_icon_path(ext_manifest.get("icons", {}), ext_path, profile_path),
                    name=ext_manifest.get("name", ""),
                    # path=ext_data.get("path", ""),
                    profiles=[profile_id],
                )
                extensions_data[ext_id] = ext_node
            else:
                ext_node = extensions_data[ext_id]
                ext_node.profiles += [profile_id]

    return extensions_data
