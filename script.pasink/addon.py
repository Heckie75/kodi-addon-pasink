import json
import os
import re
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from resources.lib.pasink import PASink

_MAX_SINKS = 10

addon = xbmcaddon.Addon()
addon_dir = xbmcvfs.translatePath(addon.getAddonInfo('path'))

pasink = None


def get_display_name(sink):

    for key in [PASink.ALSA_OUTPUT, PASink.BLUEZ_SINK]:
        for i in range(_MAX_SINKS):
            if sink["sink"] == addon.getSetting("%s_sink_%i" % (key, i)):
                alias = addon.getSetting("%s_alias_%i" % (key, i))
                return alias if alias else sink["name"]

    return sink["name"]


def is_hidden(sink):

    for key in [PASink.ALSA_OUTPUT, PASink.BLUEZ_SINK]:
        for i in range(_MAX_SINKS):
            if sink["sink"] == addon.getSetting("%s_sink_%i" % (key, i)):
                return "true" == addon.getSetting("%s_hide_%i" % (key, i))

    return False


def refresh_settings(alsa_outputs, bluez_sinks):

    def _check(sink, key):

        for i in range(_MAX_SINKS):

            sid = addon.getSettingString("%s_sink_%i" % (key, i))
            if sid == sink["sink"]:
                sname = addon.getSetting("%s_name_%i" % (key, i))
                if sname != sink["name"]:
                    addon.setSetting(
                        "%s_name_%i" % (key, i), sink["name"])

                salias = addon.getSetting(
                    "%s_alias_%i" % (key, i))

                return

            elif not sid and i not in free_aliases[key]:
                free_aliases[key].append(i)

                inserts[key].append(sink)

                return

    def _update(key):

        for sink in inserts[key]:
            if key == PASink.ALSA_OUTPUT and pasink.is_bluez_sink(sink["sink"]):
                continue

            slot = None
            if len(free_aliases[key]) > 0:
                slot = free_aliases[key].pop(0)
            else:
                continue

            addon.setSetting("%s_sink_%i" % (key, slot), sink["sink"])
            addon.setSetting("%s_name_%i" %
                             (key, slot), sink["name"])
            addon.setSetting("%s_alias_%i" % (key, slot), "")

    inserts = {
        PASink.ALSA_OUTPUT: [],
        PASink.BLUEZ_SINK: []
    }
    free_aliases = {
        PASink.ALSA_OUTPUT: [],
        PASink.BLUEZ_SINK: []
    }

    for sink in alsa_outputs:
        _check(sink, PASink.ALSA_OUTPUT)

    for sink in bluez_sinks:
        _check(sink, PASink.BLUEZ_SINK)

    _update(PASink.ALSA_OUTPUT)
    _update(PASink.BLUEZ_SINK)


def get_icon_file(sink: str, combine=False) -> str:

    if combine:
        icon = "icon_combine"

    elif sink.startswith(PASink.BLUEZ_SINK):
        icon = "icon_bluetooth"

    elif "hdmi" in sink.lower():
        icon = "icon_hdmi"

    elif "displayport" in sink.lower():
        icon = "icon_dp"

    elif "usb" in sink.lower():
        icon = "icon_usb"

    else:
        icon = "icon_analog"

    return os.path.join(
        addon_dir, "resources", "assets", icon + ".png")


def set_sink(sink1: str, name1: str, sink2=None, name2=None) -> None:

    def confirm(sink: str, name1: str, name2=None):

        icon_file = get_icon_file(sink, combine=name2 != None)
        if name2:
            msg = addon.getLocalizedString(32010) % (name1, name2)
        else:
            msg = addon.getLocalizedString(32009) % name1

        xbmcgui.Dialog().notification(heading=addon.getLocalizedString(32008),
                                      message=msg, icon=icon_file)

    def error(sink, name1, name2=None):

        icon_file = os.path.join(
            addon_dir, "resources", "assets", "icon_default.png")

        if name2:
            msg = addon.getLocalizedString(32043) % (name1, name2)
        else:
            msg = addon.getLocalizedString(32042) % name1

        xbmcgui.Dialog().notification(heading=addon.getLocalizedString(32041),
                                      message=msg, icon=icon_file)

    success = pasink.set_sink(sink1=sink1, sink2=sink2)
    if success:
        confirm(sink1, name1, name2)

    else:
        error(sink1, name1, name2)


def select():

    def _get_sink_options(blacklisted_sinks=list()):

        default = pasink.get_default()
        alsa_outputs = pasink.get_alsa_outputs()
        bluez_sinks = pasink.get_bluez_sinks()

        preselect = -1
        disconnect = None
        names = list()
        sinks = list()

        i = 0
        for sink in alsa_outputs + bluez_sinks:

            name = get_display_name(sink)
            if is_hidden(sink) or sink["sink"] in blacklisted_sinks:
                continue

            elif pasink.is_bluez_sink(sink["sink"]):
                if sink["status"] in ["SUSPENDED", "RUNNING"]:
                    disconnect = name
                    name = addon.getLocalizedString(32044) % name

                elif sink["status"] == "SINKED":
                    continue

            names.append(name)
            sinks.append(sink["sink"])
            preselect = i if sink["default"] else preselect
            i += 1

        return sinks, names, preselect, disconnect

    # Step 1: ask for sink1
    sinks, names, preselect, disconnect = _get_sink_options()

    if disconnect:
        names.append(addon.getLocalizedString(32045) % disconnect)

    selected = xbmcgui.Dialog().select(
        addon.getLocalizedString(32002), names, preselect=preselect)

    if selected < 0:
        return

    elif disconnect and selected == len(names) - 1:
        pasink.disconnect()
        xbmcgui.Dialog().notification(heading=addon.getLocalizedString(32001),
                                      message=addon.getLocalizedString(
                                          32046) % disconnect,
                                      icon=os.path.join(addon_dir, "resources", "assets", "icon_default.png"))
        return

    sink1 = sinks[selected]
    name1 = names[selected]

    # Step 2: ask for confirmation or another sink if possible
    if pasink.is_combined_sink(sink1):
        action = xbmcgui.Dialog().yesno(heading=addon.getLocalizedString(32003),
                                        message=addon.getLocalizedString(32004) % name1)
        action = 1 if action else 0

    else:
        action = xbmcgui.Dialog().yesnocustom(heading=addon.getLocalizedString(32005),
                                              message=addon.getLocalizedString(32004) % name1, customlabel=addon.getLocalizedString(32006))
    # Step 2.1: confirmed
    if action == 1:
        set_sink(sink1=sink1, name1=name1)

    # Step 2.2: another sink
    elif action == 2:
        blacklisted_sinks = [sink1, PASink.COMBINED_SINK]
        if pasink.is_bluez_sink(sink1):
            blacklisted_sinks += list(
                filter(lambda _s: pasink.is_bluez_sink(_s), sinks))

        sinks, names, preselect, disconnect = _get_sink_options(
            blacklisted_sinks=blacklisted_sinks)

        selected = xbmcgui.Dialog().select(
            addon.getLocalizedString(32007), names, preselect=preselect)

        if selected < 0:
            return

        sink2 = sinks[selected]
        name2 = names[selected]

        set_sink(sink1=sink1, name1=name1, sink2=sink2, name2=name2)


def add_to_favourites(type: str, id: int) -> None:

    sink = addon.getSettingString("%s_sink_%i" % (type, id))
    title = addon.getSettingString("%s_alias_%i" % (type, id))
    if not title:
        title = addon.getSettingString("%s_name_%i" % (type, id))

    thumbnail = os.path.join(addon_dir, "icon.png")

    kodi_json = dict()
    kodi_json["jsonrpc"] = "2.0"
    kodi_json["id"] = 1
    kodi_json["method"] = "Favourites.AddFavourite"
    kodi_json["params"] = {
        "title": title,
        "type": "media",
        "path": "plugin://script.pasink/?sink=%s&name=%s" % (sink, title),
        "thumbnail": thumbnail
    }
    xbmc.executeJSONRPC(json.dumps(kodi_json))
    xbmcgui.Dialog().notification(heading=addon.getLocalizedString(32001),
                                  message=addon.getLocalizedString(
        32047),
        icon=thumbnail)


if __name__ == "__main__":

    args = sys.argv
    if len(args) == 2 and args[1] == "discover":
        pasink = PASink()
        refresh_settings(pasink.get_alsa_outputs(), pasink.get_bluez_sinks())

    elif len(args) == 4 and args[1] == "add_fav":
        add_to_favourites(type=args[2], id=int(args[3]))

    elif len(args) == 4 and args[2].startswith("?sink"):
        pasink = PASink()
        m = re.match("^\?sink=(.+)&name=(.+)$", args[2])
        set_sink(sink1=m.groups()[0], name1=m.groups()[1])

    else:
        pasink = PASink()
        select()
