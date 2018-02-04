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

First of all download the plugin archive file, i.e. [plugin.audio.pasink.zip](/plugin.audio.pasink.zip)

You must extract this archive in the Kodi plugin folder
```
### change to kodi's addon directory
$ cd ~/.kodi/addons/

### extract plugin
$ tar xzf ~/Downloads/plugin.audio.pasink.zip
```

After you have restarted Kodi you must activate the plugin explicitly. 
1. Start Kodi
2. Go to "Addons" menu
3. Select "User addons"
4. Select "Music" addons, select "Pulse-Audio Sink Setter" and activate it


## Howto

After you have installed and activated the plugin, there is a new tile in the KODI's addon menu. Since the addon is a music plugin you can also find it in the submenu "Music addons" in your music. 

### Overview

After you have clicked on "Pulse-Audio Sink Setter" the plugin is going to detect your audio devices (ALSA cards) and already paired bluetooth A2DP devices.

**Note:** The plugin doesn't come with pairing capabilities. You must pair your bluetooth audio devices by yourself. 

Afterwards you will see a list like this:

<img src="plugin.audio.pasink/resources/assets/screen_1_info.png?raw=true">

The first entry is showing the default sink which is the sink that is active at this moment. In my case it is the "Belkin C63". In brackets you see the volume that has been set up in the pulse audio mixer, e.g. 100%. 

### ALSA cards and toggling sinks

Next entries are ALSA devices. In my case there is a HDMI device which is the audio output connected to my TV set. 

<img src="plugin.audio.pasink/resources/assets/screen_2_hdmi.png?raw=true">

The next one is an external USB adapter which allows me to connect my Intel NUC to my stereo via an optical digital cable. 

You can toggle between devices just by clicking each entry or pressing enter. A notification in the upper right corner gives you feedback. First step before configuration starts is "Prepare ... sink ...". After configuration has been successful there is a second notification saying "Sink successfully set".

<img src="plugin.audio.pasink/resources/assets/screen_3_usb.png?raw=true">

### Bluetooth A2DP devices

The next two entries "Nokia AD-42W" and "Belkin C63" are bluetooth devices. Both devices are paired but only "Belkin" is connected to a audio sink. 

**Note:** If a bluetooth device is sinked it does NOT automatically mean that audio is played on this device! 

Connecting to a bluetooth device that is in "paired" state (not "sinked") can take a while - maybe up to 30 seconds since the plugin must connect to the bluetooth device and waits until the sink has been created. Unfortunately this procedure isn't very stable. That's why the plugin retries to setup the bluetooth device up to 5 times!

<img src="plugin.audio.pasink/resources/assets/screen_4_bluez.png?raw=true">

### Combine sinks

The last entry is for setting up a combined sink. 

<img src="plugin.audio.pasink/resources/assets/screen_5_combine.png?raw=true">

After you have clicked on "combine sinks ..." you have to select the first audio sink which is of tyle ALSA card. After you have selected the ALSA card you must select the bluetooth A2DP device. Afterwards the plugin is going to build the combined audio sink. In case that the bluetooth device was not "sinked" yet, the plugin will connect the bluetooth device, waits for the sink and so on. That's the reason why this can take a while. 


### Aliases

So far we have seen a list of sound card and bluetooth device names. Wouldn't it be nice to give meaningful names instead? Of course. 

You have learned that the plugin is going to detect your audio and bluetooth A2DP devices, each time you click on "Pulse-Audio Sink Setter" entry. In addition the plugin stores these devices in the settings menu. By opening the addon's settings you can assign aliases for each device. 

<img src="plugin.audio.pasink/resources/assets/screen_6_settings.png?raw=true">

After you have done save the settings, the menu displays aliases instead of technical names like this:

<img src="plugin.audio.pasink/resources/assets/screen_7_aliases.png?raw=true">

**Note:** Aliases don't work for simultanious devices (combined sinks) yet. 
