import json
import os
import subprocess

import xbmcaddon
import xbmcvfs


class PASink():

    _state = None
    _default = None

    ALSA_OUTPUT = "alsa_output"
    BLUEZ_SINK = "bluez_sink"
    COMBINED_SINK = "combined"

    def __init__(self) -> None:

        returncode, out, err = self._exec_pasink(["--json"])
        if returncode != 0:
            return

        self._state = json.loads(out)

        for _s in self._state["sinks"]:
            _s["alias"] = _s["name"]
            if _s["default"]:
                self._default = _s

        for _s in self._state["bluez"]:
            _s["sink"] = "%s.%s.a2dp_sink" % (PASink.BLUEZ_SINK, _s["mac"].replace(
                ":", "_"))
            _s["alias"] = _s["name"]
            _s["default"] = True if _s["sink"] == self._default["sink"] else False

    def get_alsa_outputs(self):

        return self._state["sinks"]

    def get_bluez_sinks(self):

        return self._state["bluez"]

    def get_default(self):

        return self._default

    def is_bluez_sink(self, sink):

        return sink and sink.startswith(PASink.BLUEZ_SINK)

    def is_combined_sink(self, sink):

        return PASink.COMBINED_SINK == sink

    def set_sink(self, sink1, sink2=None):

        def _get_target(sink):

            if not sink:
                return None

            elif self.is_bluez_sink(sink):
                _s = next(
                    filter(lambda _s: _s["sink"] == sink, self._state["bluez"]))
                return _s["mac"] if _s else None

            else:
                return sink

        sink1 = _get_target(sink1)
        sink2 = _get_target(sink2)

        if not sink1:
            return

        elif not sink2 or sink1 == sink2:
            returncode, out, err = self._exec_pasink([sink1])

        else:
            returncode, out, err = self._exec_pasink([sink1, sink2])

        return returncode == 0

    def disconnect(self):

        returncode, out, err = self._exec_pasink(["-d"])
        return returncode == 0

    def _exec_pasink(self, params):

        addon = xbmcaddon.Addon()
        _addon_dir = xbmcvfs.translatePath(addon.getAddonInfo('path'))

        call = [os.sep.join(
            [_addon_dir, "resources", "lib", "pasink"])] + params

        p = subprocess.Popen(call,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = p.communicate()
        return p.returncode, out, err
