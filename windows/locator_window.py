import PySimpleGUI as sg
import sys
import numpy as np
import os
import cv2
from helpers.background_editor import delete_rectangle, draw_rectangle, repaint_rectangle_green
from screen_object_maker import create_error_popup
from windows.windows import Windows
from windows import table_window, mask_window

_INPUT_NAME = '-INPUT_LOCATOR_NAME-'
_INPUT_TOP_X = '-INPUT_TOP_X-'
_INPUT_TOP_Y = '-INPUT_TOP_Y-'
_INPUT_BOT_X = '-INPUT_BOT_X-'
_INPUT_BOT_Y = '-INPUT_BOT_Y-'
_EDIT = '-EDIT_LOCATOR-'
_SAVE = '-SAVE_LOCATOR-'
_SAVE_AS_IMAGE = '-SAVE_LOCATOR_AS_IMAGE-'
_CREATE_TABLE = '-CREATE_TABLE-'
_CREATE_MASK = '-CREATE_LOCATOR_MASK-'
_CLOSE = '-CLOSE_LOCATOR-'


def _check_image_name(locator, path):
    if locator.name is None or locator.name == "":
        create_error_popup('Имя картинки не может быть пустым')
        return False
    file_names = os.listdir(path)
    for file_name in file_names:
        if f"{locator.name}.png" == file_name:
            create_error_popup("Картинка с таким именем уже есть")
            return False
    return True


def _check_locator_name(locator, locators):
    if locator.name is None or locator.name == "":
        create_error_popup('Имя не может быть пустым')
        return False
    for L in locators:
        if L is not locator and L.name == locator.name:
            create_error_popup('Локатор с таким именем уже есть')
            return False
    return True


def _create_layout(locator):
    name = locator.name if locator.name is not None else ""
    layout = [
        [sg.Text('Name', size=(5, 1)),
         sg.InputText(name, size=(18, 1), key=_INPUT_NAME, enable_events=True)],
        [sg.Text('top X:', size=(5, 1)), sg.InputText(f'{locator.top_x}', size=(5, 1), key=_INPUT_TOP_X),
         sg.Text('top Y:', size=(5, 1)), sg.InputText(f'{locator.top_y}', size=(5, 1), key=_INPUT_TOP_Y)],
        [sg.Text('bot X:', size=(5, 1)), sg.InputText(f'{locator.bot_x}', size=(5, 1), key=_INPUT_BOT_X),
         sg.Text('bot Y:', size=(5, 1)), sg.InputText(f'{locator.bot_y}', size=(5, 1), key=_INPUT_BOT_Y)],
        [sg.Button('Edit', key=_EDIT),
         sg.Button('Save', key=_SAVE),
         sg.Button('Save as image', key=_SAVE_AS_IMAGE)],
        [sg.Button('Table', key=_CREATE_TABLE),
         sg.Button('Mask', key=_CREATE_MASK),
         sg.Button('Close', key=_CLOSE)]]
    return layout


def create(locator):
    layout = _create_layout(locator)
    return sg.Window('Everything bagel', layout, finalize=True,
                     keep_on_top=True, no_titlebar=True, grab_anywhere=True,
                     modal=True, location=(locator.top_x, locator.bot_y + 1))


def handle_event(event, values, state):
    if event == _EDIT:
        top_x = int(values[_INPUT_TOP_X])
        top_y = int(values[_INPUT_TOP_Y])
        bot_x = int(values[_INPUT_BOT_X])
        bot_y = int(values[_INPUT_BOT_Y])
        delete_rectangle(state.current_locator)
        state.current_locator.set_coordinate(top_x, top_y, bot_x, bot_y)
        new_crop_img = np.copy(state.background_image[top_y - 1:bot_y + 1, top_x - 1:bot_x + 1])
        state.current_locator.image = new_crop_img
        draw_rectangle(top_x, top_y, bot_x, bot_y)

    elif event == _INPUT_NAME:
        state.current_locator.name = values[_INPUT_NAME]

    elif event == _CREATE_TABLE:
        state.windows[Windows.Table] = table_window.create()

    elif event == _CREATE_MASK:
        state.hsv_mask_for = "locator"
        state.windows[Windows.Mask] = mask_window.create()

    elif event == _SAVE_AS_IMAGE:
        path = sys.path[0] + r"\temp"
        if _check_image_name(state.current_locator, path):
            cv2.imwrite(path + f"\\{state.current_locator.name}.png", state.current_locator.image)
            repaint_rectangle_green(state.current_locator)
            state.windows[Windows.Locator].close()
            state.windows[Windows.Locator] = None
            state.current_locator = None

    elif event == _SAVE:
        if _check_locator_name(state.current_locator, state.locators):
            if state.current_locator not in state.locators:
                state.locators.append(state.current_locator)
            state.windows[Windows.Locator].close()
            state.windows[Windows.Locator] = None
            state.current_locator = None

    if event == _CLOSE:
        delete_rectangle(state.current_locator)
        if state.current_locator in state.locators:
            state.locators.remove(state.current_locator)
        state.windows[Windows.Locator].close()
        state.windows[Windows.Locator] = None
        state.current_locator = None
