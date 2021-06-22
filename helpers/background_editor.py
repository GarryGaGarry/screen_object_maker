import cv2

state = None
background_element = None


def init(application_state, background_image_element):
    global state, background_element
    state = application_state
    background_element = background_image_element


def update_background_image(image):
    image_bytes = cv2.imencode('.png', image)[1].tobytes()
    background_element.update(data=image_bytes)


def clear_locator_area(locator):
    width, height = locator.image.shape[:2]
    y = locator.top_y
    x = locator.top_x
    state.background_image[y + 1:y + width - 2, x + 1:x + height - 2] = locator.image[2:width - 1, 2:height - 1]
    update_background_image(state.background_image)


def delete_rectangle(locator):
    width, height = locator.image.shape[:2]
    y = locator.top_y - 1
    x = locator.top_x - 1
    state.background_image[y:y + width, x:x + height] = locator.image[:]
    update_background_image(state.background_image)


def repaint_rectangle_green(locator):
    cv2.rectangle(state.background_image, (locator.top_x, locator.top_y), (locator.bot_x, locator.bot_y), (0, 255, 0), 1)
    update_background_image(state.background_image)


def draw_rectangle(top_x, top_y, bot_x, bot_y):
    cv2.rectangle(state.background_image, (top_x, top_y), (bot_x, bot_y), (0, 0, 250), 1)
    update_background_image(state.background_image)


def draw_table(start_x, start_y, offset_x, offset_y, cell_width, cell_height, count_cell_column, count_cell_row):
    current_y = start_y
    for _ in range(count_cell_row):
        current_y += offset_y
        current_x = start_x
        for _ in range(count_cell_column):
            current_x += offset_x
            cv2.rectangle(state.background_image, (current_x, current_y),
                          (current_x + cell_width, current_y + cell_height), (0, 0, 250), 1)
            current_x += cell_width
        current_y += cell_height

    update_background_image(state.background_image)
