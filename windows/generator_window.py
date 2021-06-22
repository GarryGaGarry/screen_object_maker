import PySimpleGUI as sg
import sys
import cv2
from windows.windows import Windows

_INPUT_RESULT = "-INPUT_RESULT-"
_SAVE_RESULT = "-SAVE_RESULT_FILE-"
_CLOSE = "-CLOSE_GENERATOR-"


def _generate_result_file(state):
    result = f"""import numpy as np
from locator.Locator import Locator
from screen.screens.BaseScreen import BaseScreen


class {state.screen_name}Screen(BaseScreen):
"""

    for index, hsv_mask in enumerate(state.global_hsv_mask):
        result += f"    global_hsv_{index} = np.array({list(hsv_mask[0])}, np.uint8), np.array({list(hsv_mask[1])}, np.uint8)\n"
    result += "\n"

    for index, bgr_mask in enumerate(state.global_bgr_mask):
        result += f"    global_bgr_{index} = np.array({list(bgr_mask[0])}, np.uint8), np.array({list(bgr_mask[1])}, np.uint8)\n"
    result += "\n"

    for l in state.locators:
        if l.it_is_table():
            result += f"    {l.name} = TableLocator({l.top_x}, {l.top_y}, {l.bot_x}, {l.bot_y}, " \
                      f"{l.width}, {l.height}, {l.x_offset}, {l.y_offset})\n"
        else:
            result += f"    {l.name} = Locator({l.top_x}, {l.top_y}, {l.bot_x}, {l.bot_y})\n"
            if l.hsv_masks:
                for index, hsv_mask in enumerate(l.hsv_masks):
                    result += f"    {l.name}.hsv_masks[{index}] =  np.array({list(hsv_mask[0])}, np.uint8), np.array({list(hsv_mask[1])}, np.uint8)\n"
            if l.bgr_masks:
                for index, bgr_mask in enumerate(l.bgr_masks):
                    result += f"    {l.name}.bgr_masks[{index}] = np.array({list(bgr_mask[0])}, np.uint8), np.array({list(bgr_mask[1])}, np.uint8)\n"
        result += "\n"
    return result


def _create_layout(result):
    layout = [
        [sg.Multiline(result, key=_INPUT_RESULT, size=(70, 30))],
        [sg.Button('Save file', key=_SAVE_RESULT), sg.Button('Close', key=_CLOSE)]
    ]
    return layout


def create(state):
    result = _generate_result_file(state)
    layout = _create_layout(result)

    return sg.Window('Screen Generator', layout,
                     location=(300, 300),
                     finalize=True,
                     keep_on_top=True,
                     modal=True,
                     no_titlebar=True,
                     grab_anywhere=True)


def handle_event(event, values, state):
    if event == _SAVE_RESULT:
        result = values[_INPUT_RESULT]
        path = sys.path[0] + r"\temp"
        with open(path + f'\\{state.screen_name}Screen.py', 'w') as file:
            file.write(result)
        for locator in state.locators:
            cv2.imwrite(path + f"\\{locator.name}.png", locator.image)

    elif event == _CLOSE:
        state.windows[Windows.Generator].close()
        state.windows[Windows.Generator] = None
