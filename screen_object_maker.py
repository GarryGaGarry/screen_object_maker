import threading
import PySimpleGUI as sg
import cv2
import numpy as np
import pyautogui
import time
from pynput import mouse

sg.theme('DarkAmber')


def create_error_popup(text):
    sg.popup_quick_message(text, keep_on_top=True, background_color="RED", location=(800, 900))


from helpers.locator import Locator
from helpers.application_state import ApplicationState
from helpers.background_editor import init as background_editor_init
from helpers.background_editor import draw_rectangle
from windows.windows import Windows
from windows import background_window, generator_window, locator_window, table_window, mask_window, start_window


def find_top_and_bottom_points(_first_x, _first_y, _second_x, _second_y):
    if _first_x < _second_x:
        _top_x = _first_x
        _bot_x = _second_x
    else:
        _top_x = _second_x
        _bot_x = _first_x

    if _first_y < _second_y:
        _top_y = _first_y
        _bot_y = _second_y
    else:
        _top_y = _second_y
        _bot_y = _first_y
    return _top_x, _top_y, _bot_x, _bot_y


def create_locator(_first_x, _first_y, _second_x, _second_y):
    _top_x, _top_y, _bot_x, _bot_y = find_top_and_bottom_points(_first_x, _first_y, _second_x, _second_y)
    crop_img = np.copy(state.background_image[_top_y - 1:_bot_y + 1, _top_x - 1:_bot_x + 1])
    state.locator_queue.put(Locator(crop_img, _top_x, _top_y, _bot_x, _bot_y))
    draw_rectangle(_top_x, _top_y, _bot_x, _bot_y)


def check_point_in_locator(_x, _y):
    for _locator in state.locators:
        if _locator.is_there_this_point(_x, _y):
            return _locator
    return None


def mouse_listener():
    def on_click(_x, _y, button, pressed):
        if state.create_new_locator_flag and button.name == "left":
            if pressed:
                state.first_x = _x
                state.first_y = _y
            else:
                state.second_x = _x
                state.second_y = _y
                _locator = check_point_in_locator(state.first_x, state.first_y)
                if _locator is None:
                    _locator = check_point_in_locator(state.second_x, state.second_y)
                if _locator is None:
                    create_locator(state.first_x, state.first_y, state.second_x, state.second_y)
                    state.create_new_locator_flag = False
                else:
                    state.error_queue.put("Locator creation error")
        elif not state.create_new_locator_flag and button.name == "left" and state.windows[Windows.Locator] is None\
                and state.windows[Windows.Table] is None and state.windows[Windows.Mask] is None\
                and state.windows[Windows.Generator] is None and state.windows[Windows.Start] is None:
            _locator = check_point_in_locator(_x, _y)
            if _locator is not None:
                state.locator_queue.put(_locator)
                time.sleep(0.5)

    with mouse.Listener(
            on_click=on_click) as listener:
        listener.join()


if __name__ == '__main__':
    state = ApplicationState.init()
    state.background_image = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    state.origin_image = np.copy(state.background_image)

    state.windows = {Windows.Background: background_window.create(state.background_image),
                     Windows.Start: start_window.create(),
                     Windows.Locator: None,
                     Windows.Mask: None,
                     Windows.Table: None,
                     Windows.Generator: None}

    background_image_element = state.windows[Windows.Background][background_window.BACKGROUND]
    background_editor_init(state, background_image_element)
    threading.Thread(target=mouse_listener, daemon=True).start()

    while True:
        window, event, values = sg.read_all_windows(timeout=1)

        if not state.locator_queue.empty():
            state.current_locator = state.locator_queue.get()
            state.windows[Windows.Locator] = locator_window.create(state.current_locator)

        if not state.error_queue.empty():
            error = state.error_queue.get()
            if error == "Locator creation error":
                create_error_popup('Локатор накладывается на другой локатор')

        if window is state.windows[Windows.Background]:
            background_window.handle_event(event, values, state)

        elif window is state.windows[Windows.Start]:
            start_window.handle_event(event, values, state)

        elif window is state.windows[Windows.Locator]:
            locator_window.handle_event(event, values, state)

        elif window is state.windows[Windows.Table]:
            table_window.handle_event(event, values, state)

        elif window is state.windows[Windows.Mask]:
            mask_window.handle_event(event, values, state)

        elif window is state.windows[Windows.Generator]:
            generator_window.handle_event(event, values, state)

        if state.stop_application:
            break
