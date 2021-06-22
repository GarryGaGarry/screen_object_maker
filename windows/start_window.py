import PySimpleGUI as sg
import sys
import os
import re
import numpy as np
from windows.windows import Windows
from helpers.locator import Locator
from screen_object_maker import create_error_popup
from helpers.background_editor import draw_rectangle, draw_table

_OK = '-OK_NAME-'
_LOAD = '-LOAD_SCREEN-'
_INPUT = '-INPUT_SCREEN_NAME-'

path = sys.path[0] + r"\temp"


def _find_global_mask(line, state):
    pattern_global_mask = r'[ ]*global_(hsv|bgr)_.*\[(.*)\].*\[(.*)\].*'
    result = re.search(pattern_global_mask, line)
    if result is not None:
        minimum = list(map(lambda x: int(x), result[2].split(",")))
        maximum = list(map(lambda x: int(x), result[3].split(",")))
        minimum = np.array(minimum, np.uint8)
        maximum = np.array(maximum, np.uint8)
        if result[1] == 'hsv':
            state.global_hsv_mask.append((minimum, maximum))
        elif result[1] == 'bgr':
            state.global_bgr_mask.append((minimum, maximum))


def _find_locators(line, state):
    pattern_locator = r'[ ]*(.*) = Locator\((.*), (.*), (.*), (.*)\).*'
    result = re.search(pattern_locator, line)
    if result is not None:
        top_x = int(result[2])
        top_y = int(result[3])
        bot_x = int(result[4])
        bot_y = int(result[5])
        crop_img = np.copy(state.background_image[top_y - 1:bot_y + 1, top_x - 1:bot_x + 1])
        locator = Locator(crop_img, top_x, top_y, bot_x, bot_y)
        locator.name = result[1]
        draw_rectangle(top_x, top_y, bot_x, bot_y)
        state.locators.append(locator)


def _find_table_locators(line, state):
    pattern_locator = r'[ ]*(.*) = TableLocator\((.*), (.*), (.*), (.*), (.*), (.*), (.*), (.*)\).*'
    result = re.search(pattern_locator, line)
    if result is not None:
        top_x = int(result[2])
        top_y = int(result[3])
        bot_x = int(result[4])
        bot_y = int(result[5])
        cell_width = int(result[6])
        cell_height = int(result[7])
        x_offset = int(result[8])
        y_offset = int(result[9])

        height = bot_y - top_y
        width = bot_x - top_x
        count_cell_column = width // (cell_width + x_offset)
        count_cell_row = height // (cell_height + y_offset)

        crop_img = np.copy(state.background_image[top_y - 1:bot_y + 1, top_x - 1:bot_x + 1])
        locator = Locator(crop_img, top_x, top_y, bot_x, bot_y)
        locator.name = result[1]
        locator.set_table_params(cell_width, cell_height, x_offset, y_offset)

        draw_rectangle(top_x, top_y, bot_x, bot_y)
        draw_table(top_x, top_y, x_offset, y_offset,
                   cell_width, cell_height, count_cell_column, count_cell_row)
        state.locators.append(locator)


def _find_mask(line, state):
    pattern_locator = r'[ ]*(.*)\.(hsv|bgr)_masks.*\[(.*)\].*\[(.*)\].*'
    result = re.search(pattern_locator, line)
    if result is not None:
        minimum = list(map(lambda x: int(x), result[3].split(",")))
        maximum = list(map(lambda x: int(x), result[4].split(",")))
        minimum = np.array(minimum, np.uint8)
        maximum = np.array(maximum, np.uint8)
        for locator in state.locators:
            if locator.name == result[1]:
                if result[2] == 'hsv':
                    locator.hsv_masks.append((minimum, maximum))
                elif result[2] == 'bgr':
                    locator.bgr_masks.append((minimum, maximum))
                break


def _load_screen(name, state):
    with open(path + f"\\{name}Screen.py", "r") as file:
        for line in file:
            _find_global_mask(line, state)
            _find_locators(line, state)
            _find_table_locators(line, state)
            _find_mask(line, state)

def _check_screen_name(name):
    file_names = os.listdir(path)
    for file_name in file_names:
        if f"{name}Screen.py" == file_name:
            return True
    return False


def _create_layout():
    layout = [
        [sg.Text('Screen Name', size=(11, 1)),
         sg.InputText('Screen', size=(25, 1), key=_INPUT, enable_events=True, focus=True)],
        [sg.Button('OK', key=_OK, bind_return_key=True), sg.Button('Load', key=_LOAD)]
    ]
    return layout


def create():
    layout = _create_layout()
    return sg.Window('Start', layout,
                     finalize=True,
                     no_titlebar=True,
                     keep_on_top=True,
                     grab_anywhere=True,
                     return_keyboard_events=True,
                     modal=True)


def handle_event(event, values, state):
    if event == _LOAD:
        screen_name = values[_INPUT]
        if _check_screen_name(screen_name):
            _load_screen(screen_name, state)
            state.screen_name = screen_name
            state.windows[Windows.Start].close()
            state.windows[Windows.Start] = None
        else:
            create_error_popup("Экран с таким именем не найден")

    if event == _OK and values and values[_INPUT]:
        screen_name = values[_INPUT]
        if _check_screen_name(screen_name):
            create_error_popup("Экран с таким именем уже есть")
        else:
            state.screen_name = screen_name
            state.windows[Windows.Start].close()
            state.windows[Windows.Start] = None
