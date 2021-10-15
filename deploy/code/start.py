#!/usr/bin/env python3

import os
import os.path as path
import threading

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import simpleaudio as sa

from itertools import chain

IMAGES_PATH = path.abspath(path.join(os.path.dirname(__file__), "../images"))
SOUNDS_PATH = path.abspath(path.join(path.dirname(__file__), "../sounds"))
FONTS_PATH = path.abspath(path.join(path.dirname(__file__), "../fonts"))

DEFAULT_FONT_PATH = os.path.join(FONTS_PATH, "Roboto-Regular.ttf")
INACTIVE_KEY_COLOR = 'purple'
ACTIVE_KEY_COLOR = 'red'

class LearningBoard:
    deck = None
    current_scene = None

    scene_to_keyset = {}

    def __init__(self, deck, scene='abc_mama', brightness=50):
        self.deck = deck
        self.scene_to_keyset = self.get_scene_to_keyset()
        deck.set_brightness(brightness)
        self.set_scene(scene)
        deck.set_key_callback(self.key_change_callback)

    def get_abc_key(self, letter, voice):
        icon_inactive = os.path.join(IMAGES_PATH, f'abc/{INACTIVE_KEY_COLOR}/{letter}.png')
        icon_active = os.path.join(IMAGES_PATH, f'abc/{ACTIVE_KEY_COLOR}/{letter}.png')
        return {
            'image_inactive': self.render_key_image(icon_inactive),
            'image_active': self.render_key_image(icon_active),
            'sound_path': os.path.join(SOUNDS_PATH, f'{voice}/abc/{letter}.wav'),
        }

    def get_123_key(self, number, voice):
        padded_number = f'{number:03}'
        icon_inactive = os.path.join(IMAGES_PATH, f'123/{INACTIVE_KEY_COLOR}/{padded_number}.png')
        icon_active = os.path.join(IMAGES_PATH, f'123/{ACTIVE_KEY_COLOR}/{padded_number}.png')
        return {
            'image_inactive': self.render_key_image(icon_inactive),
            'image_active': self.render_key_image(icon_active),
            'sound_path': os.path.join(SOUNDS_PATH, f'{voice}/123/{padded_number}.wav'),
        }

    def get_scene_to_keyset(self):
        scene_to_keyset = {}
        scene_to_keyset['abc_mama'] = (
            [self.get_abc_key(chr(i+97), 'mama') for i in range(0, 26)]
            + ([None] * 3)
            + [
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'mama.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'mama.png')),
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'papa_dim.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'papa.png')),
                    'goto_scene': 'abc_papa',
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, '123/purple/001.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, '123/purple/001.png')),
                    'goto_scene': '123_mama',
                },
            ]
        )
        scene_to_keyset['abc_papa'] = (
            [self.get_abc_key(chr(i+97), 'papa') for i in range(0, 26)]
            + ([None] * 3)
            + [
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'mama_dim.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'mama.png')),
                    'goto_scene': 'abc_mama',
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'papa.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'papa.png')),
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, '123/purple/001.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, '123/purple/001.png')),
                    'goto_scene': '123_papa',
                },
            ]
        )
        scene_to_keyset['123_mama'] = (
            [self.get_123_key(i, 'mama') for i in chain(range(0, 20), range(20, 100 + 1, 10))]
            + [
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'mama.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'mama.png')),
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'papa_dim.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'papa.png')),
                    'goto_scene': '123_papa',
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'abc/purple/a.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'abc/purple/a.png')),
                    'goto_scene': 'abc_mama',
                },
            ]
        )
        scene_to_keyset['123_papa'] = (
            [self.get_123_key(i, 'papa') for i in chain(range(0, 20), range(20, 100 + 1, 10))]
            + [
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'mama_dim.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'mama.png')),
                    'goto_scene': '123_mama',
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'papa.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'papa.png')),
                },
                {
                    'image_inactive': self.render_key_image(os.path.join(IMAGES_PATH, 'abc/purple/a.png')),
                    'image_active': self.render_key_image(os.path.join(IMAGES_PATH, 'abc/purple/a.png')),
                    'goto_scene': 'abc_papa',
                },
            ]
        )
        return scene_to_keyset

    def set_scene(self, scene):
        self.deck.reset()
        self.current_scene = scene
        for index, key in enumerate(self.scene_to_keyset[self.current_scene]):
            if key is not None:
                self.update_key_image(index, key['image_inactive'])

    '''
    Generates a custom tile with run-time generated text and custom image via the
    PIL module.
    '''
    def render_key_image(self, icon_filename, font_filename=DEFAULT_FONT_PATH, label_text=''):
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
    def update_key_image(self, key_index, image):
        # Use a scoped-with on the deck to ensure we're the only thread using it
        # right now.
        with self.deck:
            # Update requested key with the generated image.
            self.deck.set_key_image(key_index, image)

    def play_sound(self, sound_file_path):
        print(f'Play sound {sound_file_path}')
        wave_obj = sa.WaveObject.from_wave_file(sound_file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()


    '''
    Prints key state change information, updates rhe key image and performs any
    associated actions when a key is pressed.
    '''
    def key_change_callback(self, deck, key_index, state):
        print("Deck {} Key {} = {}".format(self.deck.id(), key_index, state), flush=True)
        keyset = self.scene_to_keyset[self.current_scene]
        key = keyset[key_index] if len(keyset) > key_index else None
        if key is None:
            return

        if state:
            self.update_key_image(key_index, key['image_active'])
            print(key)
            if 'sound_path' in key:
                self.play_sound(key['sound_path'])
            if 'goto_scene' in key:
                self.set_scene(key['goto_scene'])
        else:
            self.update_key_image(key_index, key['image_inactive'])

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
