class Settings:
    def __init__(self):
        self.win_width = 800
        self.win_height = 600
        self.square_number_x = 16
        self.square_number_y = 10
        self.game_field_x = 800
        self.game_field_y = 500
        self.square_size_x = self.game_field_x / self.square_number_x
        self.square_size_y = self.game_field_y / self.square_number_y
        self.control_panel_width = 800
        self.control_panel_height = 100
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (225, 0, 0)
        self.gray = (125, 125, 125)
        self.light_blue = (64, 128, 255)
        self.green = (0, 200, 64)
        self.yellow = (225, 225, 0)
        self.pink = (230, 50, 230)


        self.fps = 60

# controll panel positions
        self.enemy_icon_size = (30, 30)
        self.enemy_icon_position = (41, 40)
        self.enemy_panel_health_size = (88, 50)
        self.enemy_panel_health_position_centre = (110, 40)
