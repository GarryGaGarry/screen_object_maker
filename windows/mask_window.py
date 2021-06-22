import PySimpleGUI as sg
import cv2
import numpy as np

from helpers.background_editor import update_background_image
from windows.windows import Windows

_USE_MASK = '-USE_MASK-'
_SAVE = '-SAVE_MASK-'
_CLOSE = '-CLOSE_MASK-'
_SWITCHER = '-SWITCHER_HSV_OR_BGR-'

_FIRST_NAME_MIN = '-FIRST_NAME_MIN-'
_SECOND_NAME_MIN = '-SECOND_NAME_MIN-'
_THIRD_NAME_MIN = '-THIRD_NAME_MIN-'
_FIRST_NAME_MAX = '-FIRST_NAME_MAX-'
_SECOND_NAME_MAX = '-SECOND_NAME_MAX-'
_THIRD_NAME_MAX = '-THIRD_NAME_MAX-'

_FIRST_INPUT_MIN = '-FIRST_INPUT_MIN-'
_SECOND_INPUT_MIN = '-SECOND_INPUT_MIN-'
_THIRD_INPUT_MIN = '-THIRD_INPUT_MIN-'
_FIRST_INPUT_MAX = '-FIRST_INPUT_MAX-'
_SECOND_INPUT_MAX = '-SECOND_INPUT_MAX-'
_THIRD_INPUT_MAX = '-THIRD_INPUT_MAX-'

_FIRST_SLIDER_MIN = '-FIRST_SLIDER_MIN-'
_SECOND_SLIDER_MIN = '-SECOND_SLIDER_MIN-'
_THIRD_SLIDER_MIN = '-THIRD_SLIDER_MIN-'
_FIRST_SLIDER_MAX = '-FIRST_SLIDER_MAX-'
_SECOND_SLIDER_MAX = '-SECOND_SLIDER_MAX-'
_THIRD_SLIDER_MAX = '-THIRD_SLIDER_MAX-'

_SLIDER_VALUES = [_FIRST_SLIDER_MIN, _SECOND_SLIDER_MIN, _THIRD_SLIDER_MIN,
                  _FIRST_SLIDER_MAX, _SECOND_SLIDER_MAX, _THIRD_SLIDER_MAX]

_INPUT_VALUES = [_FIRST_INPUT_MIN, _SECOND_INPUT_MIN, _THIRD_INPUT_MIN,
                 _FIRST_INPUT_MAX, _SECOND_INPUT_MAX, _THIRD_INPUT_MAX]


def _check_value(value):
    if value not in ['', ' ']:
        return value
    else:
        return 0


def _apply_mask(minimum, maximum, state):
    hsv_background_image = None
    if state.hsv_mask_for == "background":
        if state.hsv_mode:
            hsv_background_image = cv2.cvtColor(state.origin_image, cv2.COLOR_BGR2HSV)
        else:
            hsv_background_image = np.copy(state.origin_image)
        hsv_background_image = cv2.inRange(hsv_background_image, minimum, maximum)
    elif state.hsv_mask_for == "locator":
        width, height = state.current_locator.image.shape[:2]
        y = state.current_locator.top_y
        x = state.current_locator.top_x

        if state.hsv_mode:
            hsv_image = cv2.cvtColor(state.current_locator.image, cv2.COLOR_BGR2HSV)
        else:
            hsv_image = state.current_locator.image
        hsv_image = cv2.inRange(hsv_image, minimum, maximum)
        hsv_image_final = np.empty(hsv_image.shape + (3,))
        hsv_image_final[:, :, :] = hsv_image[:, :, np.newaxis]

        hsv_background_image = np.copy(state.origin_image)
        hsv_background_image[y:y + width, x:x + height] = hsv_image_final[:]
    print(hsv_background_image)
    update_background_image(hsv_background_image)


def _get_sliders_values(values):
    min1 = int(values[_FIRST_SLIDER_MIN])
    min2 = int(values[_SECOND_SLIDER_MIN])
    min3 = int(values[_THIRD_SLIDER_MIN])
    max1 = int(values[_FIRST_SLIDER_MAX])
    max2 = int(values[_SECOND_SLIDER_MAX])
    max3 = int(values[_THIRD_SLIDER_MAX])
    minimum = np.array((min1, min2, min3), np.uint8)
    maximum = np.array((max1, max2, max3), np.uint8)
    return minimum, maximum


def _get_inputs_values(values):
    min1 = int(_check_value(values[_FIRST_INPUT_MIN]))
    min2 = int(_check_value(values[_SECOND_INPUT_MIN]))
    min3 = int(_check_value(values[_THIRD_INPUT_MIN]))
    max1 = int(_check_value(values[_FIRST_INPUT_MAX]))
    max2 = int(_check_value(values[_SECOND_INPUT_MAX]))
    max3 = int(_check_value(values[_THIRD_INPUT_MAX]))
    minimum = np.array((min1, min2, min3), np.uint8)
    maximum = np.array((max1, max2, max3), np.uint8)

    return minimum, maximum


def _change_sliders_values(values, state):
    state.windows[Windows.Mask][_FIRST_SLIDER_MIN].update(int(_check_value(values[_FIRST_INPUT_MIN])))
    state.windows[Windows.Mask][_SECOND_SLIDER_MIN].update(int(_check_value(values[_SECOND_INPUT_MIN])))
    state.windows[Windows.Mask][_THIRD_SLIDER_MIN].update(int(_check_value(values[_THIRD_INPUT_MIN])))
    state.windows[Windows.Mask][_FIRST_SLIDER_MAX].update(int(_check_value(values[_FIRST_INPUT_MAX])))
    state.windows[Windows.Mask][_SECOND_SLIDER_MAX].update(int(_check_value(values[_SECOND_INPUT_MAX])))
    state.windows[Windows.Mask][_THIRD_SLIDER_MAX].update(int(_check_value(values[_THIRD_INPUT_MAX])))


def _change_inputs_values(values, state):
    state.windows[Windows.Mask][_FIRST_INPUT_MIN].update(str(int(values[_FIRST_SLIDER_MIN])))
    state.windows[Windows.Mask][_SECOND_INPUT_MIN].update(str(int(values[_SECOND_SLIDER_MIN])))
    state.windows[Windows.Mask][_THIRD_INPUT_MIN].update(str(int(values[_THIRD_SLIDER_MIN])))
    state.windows[Windows.Mask][_FIRST_INPUT_MAX].update(str(int(values[_FIRST_SLIDER_MAX])))
    state.windows[Windows.Mask][_SECOND_INPUT_MAX].update(str(int(values[_SECOND_SLIDER_MAX])))
    state.windows[Windows.Mask][_THIRD_INPUT_MAX].update(str(int(values[_THIRD_SLIDER_MAX])))


def _rename_to_hsv(state):
    state.windows[Windows.Mask][_SWITCHER].update("BGR")
    state.windows[Windows.Mask][_FIRST_NAME_MIN].update('H min')
    state.windows[Windows.Mask][_SECOND_NAME_MIN].update('S min')
    state.windows[Windows.Mask][_THIRD_NAME_MIN].update('V min')
    state.windows[Windows.Mask][_FIRST_NAME_MAX].update('H max')
    state.windows[Windows.Mask][_SECOND_NAME_MAX].update('S max')
    state.windows[Windows.Mask][_THIRD_NAME_MAX].update('V max')


def _rename_to_bgr(state):
    state.windows[Windows.Mask][_SWITCHER].update("HSV")
    state.windows[Windows.Mask][_FIRST_NAME_MIN].update('B min')
    state.windows[Windows.Mask][_SECOND_NAME_MIN].update('G min')
    state.windows[Windows.Mask][_THIRD_NAME_MIN].update('R min')
    state.windows[Windows.Mask][_FIRST_NAME_MAX].update('B max')
    state.windows[Windows.Mask][_SECOND_NAME_MAX].update('G max')
    state.windows[Windows.Mask][_THIRD_NAME_MAX].update('R max')


def _stop_use_hsv_mask(state):
    state.use_hsv_mask = False
    state.windows[Windows.Mask][_USE_MASK].update("Use mask")
    update_background_image(state.background_image)


def _create_layout():
    layout = [
        [sg.Text('H min', size=(5, 1), key=_FIRST_NAME_MIN),
         sg.InputText('0', size=(5, 1), key=_FIRST_INPUT_MIN, enable_events=True),
         sg.Slider(range=(0, 255), key=_FIRST_SLIDER_MIN, orientation='h',
                   size=(35, 10), default_value=0, enable_events=True)],
        [sg.Text('S min', size=(5, 1), key=_SECOND_NAME_MIN),
         sg.InputText('0', size=(5, 1), key=_SECOND_INPUT_MIN, enable_events=True),
         sg.Slider(range=(0, 255), key=_SECOND_SLIDER_MIN, orientation='h',
                   size=(35, 10), default_value=0, enable_events=True)],
        [sg.Text('V min', size=(5, 1), key=_THIRD_NAME_MIN),
         sg.InputText('0', size=(5, 1), key=_THIRD_INPUT_MIN, enable_events=True),
         sg.Slider(range=(0, 255), key=_THIRD_SLIDER_MIN, orientation='h',
                   size=(35, 10), default_value=0, enable_events=True)],
        [sg.Text('H max', size=(5, 1), key=_FIRST_NAME_MAX),
         sg.InputText('255', size=(5, 1), key=_FIRST_INPUT_MAX, enable_events=True),
         sg.Slider(range=(0, 255), key=_FIRST_SLIDER_MAX, orientation='h',
                   size=(35, 10), default_value=255, enable_events=True)],
        [sg.Text('S max', size=(5, 1), key=_SECOND_NAME_MAX),
         sg.InputText('255', size=(5, 1), key=_SECOND_INPUT_MAX, enable_events=True),
         sg.Slider(range=(0, 255), key=_SECOND_SLIDER_MAX, orientation='h',
                   size=(35, 10), default_value=255, enable_events=True)],
        [sg.Text('V max', size=(5, 1), key=_THIRD_NAME_MAX),
         sg.InputText('255', size=(5, 1), key=_THIRD_INPUT_MAX, enable_events=True),
         sg.Slider(range=(0, 255), key=_THIRD_SLIDER_MAX, orientation='h',
                   size=(35, 10), default_value=255, enable_events=True)],
        [sg.Button('Use mask', key=_USE_MASK, size=(13, 1)),
         sg.Button('BGR', key=_SWITCHER),
         sg.Button('Save', key=_SAVE),
         sg.Button('Close', key=_CLOSE)]]
    return layout


def create():
    layout = _create_layout()
    return sg.Window('hsv mask', layout,
                     finalize=True, keep_on_top=True, modal=True)


def handle_event(event, values, state):
    if event == _USE_MASK:
        if state.use_hsv_mask:
            _stop_use_hsv_mask(state)
        else:
            state.use_hsv_mask = True
            minimum, maximum = _get_sliders_values(values)
            _apply_mask(minimum, maximum, state)
            state.windows[Windows.Mask][_USE_MASK].update("Stop use mask")

    elif event in _SLIDER_VALUES:
        minimum, maximum = _get_sliders_values(values)
        _change_inputs_values(values, state)
        if state.use_hsv_mask:
            _apply_mask(minimum, maximum, state)

    elif event in _INPUT_VALUES:
        minimum, maximum = _get_inputs_values(values)
        _change_sliders_values(values, state)
        if state.use_hsv_mask:
            _apply_mask(minimum, maximum, state)

    elif event == _SWITCHER:
        if state.hsv_mode:
            _rename_to_bgr(state)
            state.hsv_mode = False
        else:
            _rename_to_hsv(state)
            state.hsv_mode = True
        if state.use_hsv_mask:
            minimum, maximum = _get_sliders_values(values)
            _apply_mask(minimum, maximum, state)

    elif event == _SAVE:
        minimum, maximum = _get_sliders_values(values)
        if state.current_locator is not None:
            if state.hsv_mode:
                state.current_locator.hsv_masks.append((minimum, maximum))
            else:
                state.current_locator.bgr_masks.append((minimum, maximum))
        else:
            if state.hsv_mode:
                state.global_hsv_mask.append((minimum, maximum))
            else:
                state.global_bgr_mask.append((minimum, maximum))

    elif event == _CLOSE:
        _stop_use_hsv_mask(state)
        state.hsv_mode = True
        state.windows[Windows.Mask].close()
        state.hsv_mask_for = None
        state.windows[Windows.Mask] = None
