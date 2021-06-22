import PySimpleGUI as sg
import cv2
import sys
from helpers.background_editor import clear_locator_area, draw_table
from windows.windows import Windows

_INPUT_WIDTH = '-INPUT_WIDTH-'
_INPUT_HEIGHT = '-INPUT_HEIGHT-'
_INPUT_X_OFFSET = '-INPUT_X_OFFSET-'
_INPUT_Y_OFFSET = '-INPUT_Y_OFFSET-'
_EDIT = '-EDIT_TABLE-'
_SAVE = '-SAVE_TABLE-'
_CLOSE = '-CLOSE_TABLE-'
_SAVE_IMAGE = '-SAVE_IMAGE-'


def _get_values(values):
    cell_width = int(values[_INPUT_WIDTH])
    cell_height = int(values[_INPUT_HEIGHT])
    offset_x = int(values[_INPUT_X_OFFSET])
    offset_y = int(values[_INPUT_Y_OFFSET])
    return cell_height, cell_width, offset_x, offset_y


def _create_layout():
    layout = [
        [sg.Text('width:', size=(7, 1)), sg.InputText('0', size=(5, 1), key=_INPUT_WIDTH),
         sg.Text('height:', size=(7, 1)), sg.InputText('0', size=(5, 1), key=_INPUT_HEIGHT)],
        [sg.Text('x offset:', size=(7, 1)), sg.InputText('0', size=(5, 1), key=_INPUT_X_OFFSET),
         sg.Text('y offset:', size=(7, 1)), sg.InputText('0', size=(5, 1), key=_INPUT_Y_OFFSET)],
        [sg.Button('Edit', key=_EDIT),
         sg.Button('Save', key=_SAVE),
         sg.Button('Save images', key=_SAVE_IMAGE),
         sg.Button('Close', key=_CLOSE)]]
    return layout


def create():
    layout = _create_layout()
    return sg.Window('Table creator', layout, finalize=True, no_titlebar=True,
                     keep_on_top=True, grab_anywhere=True, modal=True)


def handle_event(event, values, state):
    if event == _SAVE:
        cell_height, cell_width, offset_x, offset_y = _get_values(values)
        state.current_locator.set_table_params(cell_width, cell_height, offset_x, offset_y)
        state.windows[Windows.Table].close()
        state.windows[Windows.Table] = None

    elif event == _EDIT:
        clear_locator_area(state.current_locator)

        cell_height, cell_width, offset_x, offset_y = _get_values(values)

        height = state.current_locator.bot_y - state.current_locator.top_y
        width = state.current_locator.bot_x - state.current_locator.top_x
        count_cell_column = width // (cell_width + offset_x)
        count_cell_row = height // (cell_height + offset_y)

        draw_table(state.current_locator.top_x, state.current_locator.top_y, offset_x, offset_y,
                   cell_width, cell_height, count_cell_column, count_cell_row)

    elif event == _SAVE_IMAGE:
        cell_height, cell_width, offset_x, offset_y = _get_values(values)

        height = state.current_locator.bot_y - state.current_locator.top_y
        width = state.current_locator.bot_x - state.current_locator.top_x
        count_cell_column = width // (cell_width + offset_x)
        count_cell_row = height // (cell_height + offset_y)

        index = 0
        current_y = state.current_locator.top_y
        for _ in range(count_cell_row):
            current_y += offset_y
            current_x = state.current_locator.top_x
            for _ in range(count_cell_column):
                current_x += offset_x
                crop_img = state.background_image[current_y+1:current_y + cell_height, current_x+1:current_x + cell_width]
                path = sys.path[0] + r"\temp"
                cv2.imwrite(path + f"\\img{index}.png", crop_img)
                index += 1
                current_x += cell_width
            current_y += cell_height

    elif event == _CLOSE:
        clear_locator_area(state.current_locator)
        state.windows[Windows.Table].close()
        state.windows[Windows.Table] = None

