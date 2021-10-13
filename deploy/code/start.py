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


class LearningBoard:
    deck = None
    current_scene = None

    def __init__(self, deck, scene='abc', brightness=50):
        self.deck = deck
        deck.set_brightness(brightness)
        self.set_scene(scene)
        deck.set_key_callback(self.key_change_callback)
    
    def set_scene(self, scene):
        self.current_scene = scene
        for key in range(self.deck.key_count()):
            self.update_key_image(key, False)
    
    '''
    Generates a custom tile with run-time generated text and custom image via the
    PIL module.
    '''
    def render_key_image(self, icon_filename, font_filename, label_text):
        # Resize the source image asset to best-fit the dimensions of a single key,
        # leaving a margin at the bottom so that we can draw the key title
        # afterwards.
        icon = Image.open(icon_filename)
        image = PILHelper.create_scaled_image(self.deck, icon, margins=[0, 0, 0, 0])

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image a few pixels from the bottom of the key.
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, 14)
        draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")

        return PILHelper.to_native_format(self.deck, image)

    '''
    Creates a new key image based on the key index, style and current key state
    and updates the image on the StreamDeck.
    '''
    def update_key_image(self, key, state):
        if (key > 25):
            return
        font =  os.path.join(FONTS_PATH, "Roboto-Regular.ttf")
        label = ''
        letter = chr(key+97)
        print(key)
        print(letter)
        icon = os.path.join(IMAGES_PATH, f'abc/purple/{letter}.png')
        image = self.render_key_image(icon, font, label)

        # Use a scoped-with on the deck to ensure we're the only thread using it
        # right now.
        with self.deck:
            # Update requested key with the generated image.
            self.deck.set_key_image(key, image)

    def play_sound(self, sound_file_path):
        abs_sound_path = os.path.join(SOUNDS_PATH, sound_file_path)
        print(abs_sound_path)
        wave_obj = sa.WaveObject.from_wave_file(abs_sound_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        print('played') 


    '''
    Prints key state change information, updates rhe key image and performs any
    associated actions when a key is pressed.
    '''
    def key_change_callback(self, deck, key, state):
        print("Deck {} Key {} = {}".format(self.deck.id(), key, state), flush=True)
        letter = chr(key+97)
        if state and letter.isalpha():
            self.play_sound(f'mama/abc/{letter}.wav')

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

        learning_board = LearningBoard(deck)

        # Wait until all application threads have terminated
        for t in threading.enumerate():
            if t is threading.currentThread():
                continue

            if t.is_alive():
                t.join()
