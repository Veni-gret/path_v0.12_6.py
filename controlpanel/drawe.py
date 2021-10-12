import pygame as pg
from math import sin, cos, radians
import time



class Ability:
    def __init__(self):
        self.countdown_time = 0
        self.activation = False
        self.ability_lvl = 0

    def set_countdown(self, new_countdown_time):
        self.countdown_time = new_countdown_time

    def set_ability_lvl(self, new_lvl):
        self.ability_lvl = new_lvl

    def ability_action(self):
        pass


class DamageOverTime(Ability):
    def __init__(self, ability_name, image_icon, base_countdown_time):
        super().__init__()
        self.ability_name = ability_name
        self.image = pg.image.load(image_icon)
        self.countdown_time = base_countdown_time
        self.ability_lvl = 1
        self.damage_in_second = 5
        self.damage_time = 5
        self.activation = False
        self.ability_start_time = 0
        self.in_progress = False

    def ability_action(self):
        if self.activation:
            self.ability_start_time = time.time()

            print("Cat")
            self.activation = False

class ControlPanelSpot:
    def __init__(self, surface, size_c, position):
        self.surface = surface
        self.global_countdown = 1
        self.global_countdown_active = False
        self.ability = None
        self.countdown = 0
        self.icon_rect = None
        self.icon_size = size_c
        self.icon = None
        self.size = size_c
        self.total_points_number = 36
        self.d_angle = 360 // self.total_points_number
        self.d_countdown = 0
        self.current_countdown = 0
        self.position = position
        self.start_time = 0
        self.points_number = 0
        self.spot_surface = pg.Surface(size_c)
        self.spot_surface.set_colorkey(RED)
        self.spot_surface.set_alpha(150)
        self.spot_surface_rect = self.spot_surface.get_rect(center=position)
        self.clicked = False
        self.countdown_calk = False

    def set_ability(self, ability_s):
        self.icon = pg.transform.scale(ability_s.image, self.icon_size)
        self.icon_rect = self.icon.get_rect(center=self.position)
        self.ability = ability_s

    def countdown_go(self):
        if self.ability:
            self.surface.blit(self.icon, self.icon_rect)
            self.spot_surface.fill(BLACK)
            if self.clicked or self.global_countdown_active:
                if self.clicked:
                    self.countdown = self.ability.countdown_time
                else:
                    self.countdown = self.global_countdown

                if not self.countdown_calk:
                    self.d_countdown = self.countdown / self.total_points_number
                    self.current_countdown = self.d_countdown
                    self.countdown_calk = True

                point_list = [[self.size[0] / 2, self.size[1] / 2], [self.size[0] / 2, 0]]
                angle = 0
                i = 1
                while i != self.points_number + 1:
                    x = sin(radians(angle)) * self.size[0] / 2
                    y = cos(radians(angle)) * self.size[1] / 2
                    point_list.append([self.size[0] / 2 + x, self.size[1] / 2 - y])
                    angle += self.d_angle
                    i += 1
                point_list.append([self.size[0] / 2, self.size[1] / 2])

                pg.draw.polygon(self.spot_surface, RED, point_list)
                self.surface.blit(self.spot_surface, self.spot_surface_rect)

                if time.time() - self.start_time >= self.current_countdown:
                    self.current_countdown += self.d_countdown

                    self.points_number += 1
                    if self.points_number == self.total_points_number:
                        self.points_number = 0
                        self.start_time = 0
                        self.current_countdown = 0
                        self.clicked = False
                        self.countdown_calk = False
                        self.global_countdown_active = False
        else:
            return


# Initialize the game engine
pg.init()

# Define the colors we will use in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set the height and width of the screen
size = [700, 800]
screen = pg.display.set_mode(size)


# Loop until the user clicks the close button.
done = False
clock = pg.time.Clock()
control_panel_spots_dict = {}
first_x = 35
icon_list = ['Icons_01.png', 'Icons_02.png', 'Icons_03.png', 'Icons_04.png', 'Icons_05.png', 'Icons_06.png',
             'Icons_07.png', 'Icons_08.png', 'Icons_09.png', 'Icons_10.png']
for spot in range(1, 11):
    control_panel_spots_dict[spot] = [ControlPanelSpot(screen, (70, 70), (first_x, 35))]
    first_x += 70
spot_a = 1
ability_1 = DamageOverTime('Icons_01.png', 'Icons_01.png', 10)

control_panel_spots_dict[1][0].set_ability(ability_1)


pressed = None
while not done:

    clock.tick(60)

    for event in pg.event.get():  # User did something
        if event.type == pg.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:

            for spot in control_panel_spots_dict:
                if control_panel_spots_dict[spot][0].spot_surface_rect.collidepoint(event.pos):
                    pressed = control_panel_spots_dict[spot]
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:

            for spot in control_panel_spots_dict:
                if (control_panel_spots_dict[spot][0].spot_surface_rect.collidepoint(event.pos) and
                        not control_panel_spots_dict[spot][0].clicked and
                        not control_panel_spots_dict[spot][0].global_countdown_active):
                    if control_panel_spots_dict[spot] == pressed:
                        control_panel_spots_dict[spot][0].clicked = True
                        control_panel_spots_dict[spot][0].ability.activation = True
                        control_panel_spots_dict[spot][0].start_time = time.time()

                        for spot_2 in control_panel_spots_dict:
                            if not control_panel_spots_dict[spot_2][0].clicked:
                                control_panel_spots_dict[spot_2][0].global_countdown_active = True
                                control_panel_spots_dict[spot_2][0].start_time = time.time()

    screen.fill(WHITE)

    for spot in control_panel_spots_dict:
        if control_panel_spots_dict[spot][0].ability:
            control_panel_spots_dict[spot][0].ability.ability_action()
            control_panel_spots_dict[spot][0].countdown_go()

    pg.display.flip()
pg.quit()
