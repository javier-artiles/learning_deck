#!/usr/bin/env python3

import os
import os.path as path
import threading

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import simpleaudio as sa

IMAGES_PATH = path.abspath(path.join(os.path.dirname(__file__), "../images"))
SOUNDS_PATH = path.abspath(path.join(path.dirname(__file__), "../sounds"))
FONTS_PATH = path.abspath(path.join(path.dirname(__file__), "../fonts"))


# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    print(icon_filename)
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 0, 0])

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)


# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
    # Last button in the example application is the exit button.
    exit_key_index = deck.key_count() - 1

    if key == exit_key_index:
        name = "exit"
        icon = "{}.png".format("Exit")
        font = "Roboto-Regular.ttf"
        label = "Bye" if state else "Exit"
    else:
        name = "emoji"
        icon = "{}.png".format("Pressed" if state else "Released")
        font = "Roboto-Regular.ttf"
        label = "Pressed!" if state else "Key {}".format(key)

    return {
        "name": name,
        "icon": os.path.join(IMAGES_PATH, icon),
        "font": os.path.join(FONTS_PATH, font),
        "label": label
    }


# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    # key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    if (key > 25):
        return
    font =  os.path.join(FONTS_PATH, "Roboto-Regular.ttf")
    label = ''
    letter = chr(key+97)
    print(key)
    print(letter)
    icon = os.path.join(IMAGES_PATH, f'abc/purple/{letter}.png')
    image = render_key_image(deck, icon, font, label)

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)

def play_sound(sound_file_path):
    abs_sound_path = os.path.join(SOUNDS_PATH, sound_file_path)
    print(abs_sound_path)
    wave_obj = sa.WaveObject.from_wave_file(abs_sound_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()
    print('played')

# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)
    letter = chr(key+97)
    if state and letter.isalpha():
        play_sound(f'mama/abc/{letter}.wav')

    # # Update the key image based on the new key state.
    # update_key_image(deck, key, state)

    # # Check if the key is changing to the pressed state.
    # if state:
    #     key_style = get_key_style(deck, key, state)

    #     # When an exit button is pressed, close the application.
    #     if key_style["name"] == "exit":
    #         # Use a scoped-with on the deck to ensure we're the only thread
    #         # using it right now.
    #         with deck:
    #             # Reset deck, clearing all button images.
    #             deck.reset()

    #             # Close deck handle, terminating internal worker threads.
    #             deck.close()


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

        # Set initial key images.
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            if t is threading.currentThread():
                continue

            if t.is_alive():
                t.join()
