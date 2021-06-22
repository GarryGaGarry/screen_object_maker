from queue import Queue
import numpy as np


class ApplicationState:
    __instance = None

    @staticmethod
    def init():
        if ApplicationState.__instance is None:
            ApplicationState.__instance = ApplicationState()
        return ApplicationState.__instance

    def __init__(self):
        self.stop_application = False
        self.screen_name = None
        self.windows = {}

        self.global_hsv_mask = []
        self.global_bgr_mask = []
        self.use_hsv_mask = False
        self.hsv_mask_for = None
        self.hsv_mode = True

        self.locators = []
        self.current_locator = None
        self.create_new_locator_flag = False
        self.first_x = None
        self.first_y = None
        self.second_x = None
        self.second_y = None

        self.error_queue = Queue()
        self.locator_queue = Queue()

        self.background_image = None
        self.origin_image = None

    def clear(self):
        self.locators = []
        self.current_locator = None
        self.create_new_locator_flag = False
        self.use_hsv_mask = False
        self.hsv_mask_for = None
        self.first_x = None
        self.first_y = None
        self.second_x = None
        self.second_y = None
        self.background_image = np.copy(self.origin_image)
