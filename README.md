# kodi-addon-pasink

_Kodi addon in order to set Pulse-Audio sinks with bluez and combined-sink support_

Imagine that you have a flat with more than one room (probably you don't live in London, UK). Your computer, located in the livingroom, is connected to your stereo and TV set. It runs KODI and represents the media hub of your infrastructure. Of course you can listen to music in the livingroom. But how can you easily switch to your bluetooth speakers in the kitchen, bedroom or bathroom without having too much configuration issues and the need of opening the audio settings of your OS?

I have written this KODI plugin in order to make it as easy as possible to switch between audio sinks. In addition I wanted to combine a local wired sink with a bluetooth audio device (A2DP).

This plugin is based on my project [pasink](https://github.com/Heckie75/pasink) 


## Requirements / pre-conditions


This plugin calls the command `pasink`. pasink interally uses the following:

1. `bluez` - Bluetooth tools and daemons, especially the command `bluetoothctl`

The script uses `bluetoothctl` in order to list already paired A2DP bluetooth devides and to connect to them by name or mac address. 

2. `expect`

Internally pasink remote controls `bluetoothctl` like a macro. This will be done by using `expect`
`expect` can be installed as follows:

```
$ sudo apt install expect
```

3. `pulseaudio`

Pulse-Audio is the audio server. It should come with any state-of-the-art linux distribution out of the box. You might want to check if the following command line tools are available which are called by `pasink` internally:

a) `pacmd`

b) `pactl`

You MUST check and adjust some configuration. Please make sure that the following line is in the file `/etc/pulse/default.pa`:

```
load-module module-switch-on-connect
```

This module is required because it is responsible to automatically setup a new audio sink after a bluetooth A2DP device has been connected.  


## Install kodi plugin / addon

First of all download the plugin archive file, i.e. [plugin.audio.pasink.tgz](/plugin.audio.pasink.tgz)

You must extract this archive in the Kodi plugin folder
```
### change to kodi's addon directory
$ cd ~/.kodi/addons/

### extract plugin
$ tar xzf ~/Downloads/plugin.audio.pasink.tgz
```

After you have restarted Kodi you must activate the plugin explicitly. 
1. Start Kodi
2. Go to "Addons" menu
3. Select "User addons"
4. Select "Music" addons, select "Pulse-Audio Sink Setter" and activate it


## Screenshots 

<img src="plugin.audio.pasink/resources/assets/screen_1_info.png?raw=true">
<img src="plugin.audio.pasink/resources/assets/screen_2_hdmi.png?raw=true">
<img src="plugin.audio.pasink/resources/assets/screen_3_usb.png?raw=true">
<img src="plugin.audio.pasink/resources/assets/screen_4_bluez.png?raw=true">
<img src="plugin.audio.pasink/resources/assets/screen_5_combine.png?raw=true">
<img src="plugin.audio.pasink/resources/assets/screen_6_settings.png?raw=true">
<img src="plugin.audio.pasink/resources/assets/screen_7_aliases.png?raw=true">
