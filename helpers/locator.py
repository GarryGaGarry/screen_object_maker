class Locator:
    def __init__(self, image, top_x, top_y, bot_x, bot_y):
        self.image = image
        self.top_x = top_x
        self.top_y = top_y
        self.bot_x = bot_x
        self.bot_y = bot_y
        self.width = None
        self.height = None
        self.x_offset = None
        self.y_offset = None
        self.name = None
        self.hsv_masks = []
        self.bgr_masks = []

    def set_coordinate(self, top_x, top_y, bot_x, bot_y):
        self.top_x = top_x
        self.top_y = top_y
        self.bot_x = bot_x
        self.bot_y = bot_y

    def set_table_params(self, width, height, x_offset, y_offset):
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset

    def it_is_table(self):
        if self.width is not None and self.height is not None:
            return True
        else:
            return False

    def is_there_this_point(self, x, y):
        if self.top_x <= x <= self.bot_x and self.top_y <= y <= self.bot_y:
            return True
        else:
            return False
