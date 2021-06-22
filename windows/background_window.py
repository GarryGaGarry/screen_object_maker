import sys
import cv2
import pyautogui
import PySimpleGUI as sg
import numpy as np

from helpers.locator import Locator
from helpers.text_finder import find_text
from helpers.background_editor import update_background_image, draw_rectangle
from windows.windows import Windows
from windows import generator_window, mask_window


BACKGROUND = "-BACKGROUND-"


def _create_layout(image_bytes):
    layout = [[sg.Image(data=image_bytes, key=BACKGROUND)]]
    return layout


def _create_right_click_menu():
    menu = [[''], [' ', 'New Locator', 'HSV Mask', 'Find Text', 'Clear', 'Generate', 'Exit']]
    return menu


def create(image):
    image_bytes = cv2.imencode('.png', image)[1].tobytes()
    layout = _create_layout(image_bytes)
    return sg.Window('Background', layout,
                     size=pyautogui.size(),
                     finalize=True,
                     keep_on_top=True,
                     no_titlebar=True,
                     margins=(0, 0),
                     element_padding=(0, 0),
                     right_click_menu=_create_right_click_menu())


def handle_event(event, values, state):
    if event == 'New Locator':
        state.create_new_locator_flag = True

    elif event == 'HSV Mask':
        state.hsv_mask_for = 'background'
        state.windows[Windows.Mask] = mask_window.create()

    elif event == 'Find Text':
        args = {'east': 'frozen_east_text_detection.pb', 'speed': 4, 'min_confidence': 0.5,
                'path_to_tesseract': r'C:\tools\tesseract\tesseract.exe'}
        boxes = find_text(state.origin_image, args)
        for (top_x, top_y, bot_x, bot_y) in boxes:
            image = np.copy(state.background_image[top_y - 1:bot_y + 1, top_x - 1:bot_x + 1])
            state.locators.append(Locator(image, top_x, top_y, bot_x, bot_y))
            draw_rectangle(top_x, top_y, bot_x, bot_y)

    elif event == 'Clear':
        for key in state.windows:
            if state.windows[key] is not None and state.windows[key] is not state.windows[Windows.Background]:
                state.windows[key].close()
                state.windows[key] = None
        state.clear()
        update_background_image(state.background_image)

    elif event == 'Generate':
        state.windows[Windows.Generator] = generator_window.create(state)

    elif event in [sg.WIN_CLOSED, 'Exit']:
        for key in state.windows:
            if state.windows[key] is not None and state.windows[key] is not state.windows[Windows.Background]:
                state.windows[key].close()
                state.windows[key] = None
        state.windows[Windows.Background].close()
        state.windows[Windows.Background] = None
        state.stop_application = True
