# Learning Deck

Learning Deck is a tool I built to teach the alphabet, numbers and potentially much more to my daughter Alma.
It's a very simple Python script that runs on a Raspberry Pi + Stream Deck and trigger sounds to associate a symbol with a word or sound.

There are a bunch of similar and much cheaper options out there, but I personally wanted some pretty specific features
* a board with tactile buttons that I could customize over time (e.g. add solfege)
* me and my wife's voice
* recordings in both Spanish (my native language) and English (my wife's) 

## Thanks

I want to thank the folks at [Visuals By Impulse](https://visualsbyimpulse.com/) for allowing me to include 
their beautiful [Rainbow Stream Deck icons](https://visualsbyimpulse.com/store/free-rainbow-stream-deck-icons/) here.
They have some amazing designs and you should definitely check them out.

## The hardware

* [Raspberry Pi 4 Model B - 4 GB RAM](https://www.adafruit.com/product/4296). You'll also need a microSD card for storage.
* [Flirc Raspberry Pi 4 Case](https://www.amazon.com/gp/product/B07WG4DW52/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1).
* [Elgato Stream Deck XL](https://www.amazon.com/gp/product/B07RL8H55Z/).
* A portable speaker to plug into the Raspberry Pi (I guess Bluetooth could work just fine too).
* I wanted to the unit to be fully portable, so I also used a [small USB power bank](https://www.amazon.com/gp/product/B06XS9RMWS/) that can be lodged on the Stream Deck compartment.

## How to set it up

### Setup your Raspberry Pi OS

[Install Raspberry Pi OS on your microSD card using Raspberry Pi Imager](https://www.raspberrypi.com/software/).

### Install dependencies

Now that your Pi is ready, hop onto the terminal.

```
# Ensure system is up to date, upgrade all out of date packages
sudo apt update && sudo apt dist-upgrade -y

# Install the pip Python package manager
sudo apt install -y python3-pip python3-setuptools

# Install system packages needed for the default LibUSB HIDAPI backend
sudo apt install -y libudev-dev libusb-1.0-0-dev libhidapi-libusb0

# Install system packages needed for the Python Pillow package installation
sudo apt install -y libjpeg-dev zlib1g-dev libopenjp2-7 libtiff5

# Install python library dependencies
pip3 install wheel
pip3 install pillow

# Add udev rule to allow all users non-root access to Elgato StreamDeck devices:
sudo tee /etc/udev/rules.d/10-streamdeck.rules << EOF
    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fd9", GROUP="users", TAG+="uaccess"
    EOF
# Reload udev rules to ensure the new permissions take effect
    sudo udevadm control --reload-rules

# Install the latest version of the StreamDeck library via pip
pip3 install streamdeck

# Install the audio library
pip3 install simpleaudio
```

### Download and setup this script

1. Clone this repo on your Raspberry Pi.
2. Update crontab so that this script runs on startup.
```
crontab -e
```
At the end of the file add this line, making sure you are pointing to the directory where you cloned the repo
```
@reboot python3 /home/pi/workspace/learning_deck/deploy/code/start.py
```

### Enjoy! (and customize)

Now you should be able to reboot and, assuming everything is wired properly, the StreamDeck will startup with the ABC scene ready to go.
Of course the whole point here is to have a very personalized learning board, so please go ahead and record your own voices and change up the icons as needed.
How to do this should be pretty obvious from the layout of the project.

## Demo

Coming up soon
