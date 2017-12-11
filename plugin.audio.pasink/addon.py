'''
Created on 10.12.2017

@author: heckie
'''
import os
import re
import subprocess
import sys
import urlparse

import xbmcgui
import xbmcplugin
import xbmcaddon

__PLUGIN_ID__ = "plugin.audio.pasink"

settings = xbmcaddon.Addon(id=__PLUGIN_ID__);
addon_handle = int(sys.argv[1])
addon_dir = xbmc.translatePath( settings.getAddonInfo('path') )

_menu = []

default_sink = {}
alsa_sinks = []
bluez_sinks = []
bluez_sinked = {}
combined_sink = {}




def _run_pasink(params):

    call = [addon_dir + os.sep
                          + "lib"
                          + os.sep
                          + "pasink"] + params


    p = subprocess.Popen(call,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()
    value_string = out.decode("utf-8")

    return value_string.split("\n")




def _read_sinks():

    global default_sink
    global alsa_sinks
    global bluez_sinks
    global bluez_sinked
    global combined_sink

    _default_sink = {}
    _alsa_sinks = []
    _bluez_sinks = []
    _bluez_sinked = {}
    _combined_sink = {}

    _pasink_out = _run_pasink(["-d"])

    _section = ""
    for _line in _pasink_out:

        _data = _line.split("\t")
        if _line == "":
            continue
        elif _data[0] == "Default sink:":
            _section = "default"
            continue
        elif _data[0] == "Plugged Alsa card devices:":
            _section = "alsa"
            continue
        elif _data[0] == "Sinked Bluetooth A2DP device:":
            _section = "sinked"
            continue
        elif _data[0] == "Paired Bluetooth A2DP devices:":
            _section = "paired"
            continue
        elif _data[0] == "Combined sink:":
            _section = "combined"
            continue

        if _section == "default":
            _default_sink = {
                "id"     : _data[4],
                "status" : _data[1],
                "driver" : _data[2],
                "name"   : _data[3],
                "sink"   : _data[4],
                "vol"    : _data[5]
                }
        elif _section == "alsa":
            _alsa_sinks += [{
                "id"     : _data[4],
                "status" : _data[1],
                "driver" : _data[2],
                "name"   : _data[3],
                "sink"   : _data[4],
                "vol"    : _data[5]
            }]
        elif _section == "sinked":
            _bluez_sinked = {
                "id"     : _data[4],
                "status" : _data[1],
                "driver" : _data[2],
                "name"   : _data[3],
                "sink"   : _data[4],
                "vol"    : _data[5]
                }
        elif _section == "paired":
            _bluez_sinks += [{
                "id"     : _data[0],
                "mac"    : _data[0],
                "status" : _data[1],
                "name"   : _data[2]
            }]
        elif _section == "combined":
            _combined_sink = {
                "id"     : _data[4],
                "status" : _data[1],
                "driver" : _data[2],
                "name"   : _data[3],
                "sink"   : _data[4],
                "vol"    : _data[5]
                }
        else:
            pass

    default_sink = _default_sink
    alsa_sinks = _alsa_sinks
    bluez_sinks = _bluez_sinks
    bluez_sinked = _bluez_sinked
    combined_sink = _combined_sink

    return _default_sink, _alsa_sinks, _bluez_sinks, _bluez_sinked, _combined_sink




def _build_menu():

    global _menu

    alsa_entries = []
    bluez_entries = []
    combined_entries = []

    for bluez in bluez_sinks:

        bluez_entries += [
            {
                "path" : bluez["id"],
                "name" : "%s (%s)" % (bluez["name"], bluez["status"]) ,
                "icon" : "icon_bluetooth",
                "action" : [ "switch" ]
            }
        ]

    for alsa in alsa_sinks:

        if re.findall("hdmi", alsa["name"].lower()):
            icon = "icon_hdmi"
        elif re.findall("displayport", alsa["name"].lower()):
            icon = "icon_dp"
        elif re.findall("usb", alsa["name"].lower()):
            icon = "icon_usb"
        else:
            icon = "icon_analog"

        alsa_entries += [
            {
                "path" : alsa["id"],
                "name" : "%s (%s)" % (alsa["name"], alsa["vol"]),
                "icon" : icon,
                "action" : [ "switch" ]
            }
        ]

        combined_entries += [
            {
                "path" : alsa["id"],
                "name" : "%s ..." % alsa["name"],
                "icon" : icon,
                "node" : bluez_entries
            }
        ]


    entries = [
        {
            "path" : "",
            "name" : "Default: %s (%s)" % (default_sink["name"],
                                           default_sink["vol"]),
            "icon" : "icon_default"
        }
    ]
    entries += alsa_entries + bluez_entries
    entries += [
            {
                "path" : "combined",
                "name" : "combine sinks ...",
                "icon" : "icon_combine",
                "node" : combined_entries
            }
        ]

    _menu = [
        { # root
        "path" : "",
        "node" : entries
        }
    ]




def init():

    _read_sinks()
    _build_menu()




def _get_directory_by_path(path):

    if path == "/":
        return _menu[0]

    tokens = path.split("/")[1:]
    directory = _menu[0]

    while len(tokens) > 0:
        path = tokens.pop(0)
        for node in directory["node"]:
            if node["path"] == path:
                directory = node
                break

    return directory




def _build_param_string(param, values, current = ""):

    if values == None:
        return current

    for v in values:
        current += "?" if len(current) == 0 else "&"
        current += param + "=" + v

    return current




def _add_list_item(entry, path):

    if path == "/":
        path = ""

    item_path = path + "/" + entry["path"]
    item_id = item_path.replace("/", "_")

    if settings.getSetting("display%s" % item_id) == "false":
        return

    param_string = ""
    if "action" in entry:
        param_string = _build_param_string(
            param = "action",
            values = entry["action"],
            current = param_string)

    if "node" in entry:
        is_folder = True
    else:
        is_folder = False

    label = entry["name"]
    if settings.getSetting("label%s" % item_id) != "":
        label = settings.getSetting("label%s" % item_id)

    if "icon" in entry:
        icon_file = os.path.join(addon_dir, "resources", "assets", entry["icon"] + ".png")
    else:
        icon_file = None

    li = xbmcgui.ListItem(label, iconImage=icon_file)

    xbmcplugin.addDirectoryItem(handle=addon_handle,
                            listitem=li,
                            url="plugin://" + __PLUGIN_ID__
                            + item_path
                            + param_string,
                            isFolder=is_folder)




def fill_directory(path):

    directory = _get_directory_by_path(path)

    for entry in directory["node"]:
        _add_list_item(entry, path)

    xbmcplugin.endOfDirectory(addon_handle)




def _lookup_name_by_id(id):

    for sink in alsa_sinks + bluez_sinks:
        if sink["id"] == id:
            return sink["name"]

    return id




def execute(path, params):

    if params["action"][0] != "switch":
        return

    splitted_path = path.split("/")

    if len(splitted_path) < 2:
        return

    splitted_path.pop(0)

    if splitted_path[0] == "combined" and len(splitted_path) == 3:
        msg = "Prepare combined sink"
        splitted_path.pop(0)
        s = _lookup_name_by_id(splitted_path[0])
        s += "\n" + _lookup_name_by_id(splitted_path[1])
    else:
        msg = "Prepare single sink ..."
        s = _lookup_name_by_id(splitted_path[0])

    xbmc.executebuiltin("Notification(%s, %s, %s/icon.png)"
                        % (msg, s, addon_dir))

    _run_pasink(splitted_path)

    msg = "Sink successfully set"
    xbmc.executebuiltin("Notification(%s, %s, %s/icon.png)"
                        % (msg, s, addon_dir))




if __name__ == '__main__':

    path = urlparse.urlparse(sys.argv[0]).path
    url_params = urlparse.parse_qs(sys.argv[2][1:])

    init()
    if "action" in url_params:
        execute(path, url_params)
    else:
        fill_directory(path)
