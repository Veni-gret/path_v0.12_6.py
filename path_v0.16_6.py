import pygame as pg
from collections import deque
import time
import copy
from settings import Settings
from math import hypot as path_len
from math import sin, cos, pi, radians


# mouse right reaction for "killed" cheese DONE DONE DONE
# make enemy with a icon  DONE
# chose an enemy DONE
# add icon for damage Done

# do damage to mouse Done
# remove enemy from selected after kill Done
# ring DONE
# stop to plasing rock then enemy on the spot
# Make control panellllll started Done
# make spot wihte
# incorect spell action then cast spell after the dot

class Game:
    def __init__(self):
        self.settings = Settings()
        self.game_field_x = self.settings.game_field_x
        self.game_field_y = self.settings.game_field_y

        self.block_image = pg.image.load('4.png')
        self.normal_square_image = pg.image.load('Grass_finish.bmp')
        self.cheese_image = pg.image.load('cheese.png')
        self.enemy_image = pg.image.load('Icons_33.png')
        self.damage = pg.image.load('Icons_09.png')
        self.ring_image = pg.image.load('Ring_2.png')
        self.panel_image = pg.image.load('main_frame.png')
        self.hp_mask_image = pg.image.load('HP_mask.png')
        self.mob_mask_image = pg.image.load('moob_mask.png')
        self.wol_holly_fire_image = pg.image.load('ability_1.png')

        self.image_dict = {}

#        self.bl = Block()
        self.drawer = Drawer()

        self.main_surface = pg.display.set_mode((self.settings.win_width, self.settings.win_height))
        self.square_size_x = self.settings.square_size_x
        self.square_size_y = self.settings.square_size_y
        self.battlefield = Battlefield()
        self.graph = self.battlefield.get_graph()
        self.field_set = self.battlefield.field_set()
        self.normal_square = FieldObject(self.normal_square_image, (50, 50), self.battlefield.surface)
        self.normal_square_obj = self.normal_square.get_object()
        self.cheese = FieldObject(self.cheese_image, (25, 25), self.battlefield.surface)
        self.ring = FieldObject(self.ring_image, (200, 200), self.battlefield.surface)

        self.image_dict = self.battlefield.get_rect_dict(self.normal_square)

        self.added_objects_dict_2 = {}

# Control panel
        self.control_panel_dict_2 = {}
        self.control_panel_spots_dict = {}
        self.control_panel = ControlPanel()
        self.panel = PanelObject(self.panel_image, (self.settings.control_panel_width,
                                                    self.settings.control_panel_height), self.control_panel.surface)
        self.panel.get_rect_2((self.settings.control_panel_width/2, self.settings.control_panel_height/2))

        self.hp_mask = PanelObject(self.hp_mask_image, self.settings.enemy_panel_health_size,
                                   self.control_panel.surface)

        self.hp_mask.get_rect_2(self.settings.enemy_panel_health_position_centre)

        self.mob_mask = PanelObject(self.mob_mask_image, (self.settings.enemy_icon_size[0]+5,
                                                          self.settings.enemy_icon_size[1] + 5),
                                    self.control_panel.surface)

        self.mob_mask.get_rect_2(self.settings.enemy_icon_position)

        self.control_panel_dict_2[self.mob_mask.position] = self.mob_mask
        self.control_panel_dict_2[self.hp_mask.position] = self.hp_mask


#       self.control_panel_width = 800
#       self.control_panel_height = 100
        self.clock = pg.time.Clock()
        self.step = 0
        self.control_panel.surface.fill(self.settings.white)
        self.battlefield.surface.fill(self.settings.white)
        self.enemy_list = []
        self.enemy_number = 4
        for enemy in range(self.enemy_number):
            enemy = Enemy(50, self.battlefield.surface, self.field_set, self.enemy_image, (25, 25))
            self.enemy_list.append(enemy)

        y = 25.0
        for enemy in self.enemy_list:
            enemy.start_point(25.0, y)
            y += 100.0
        self.path_change = False
        self.back_on_path = False
        self.click_for_enemy = False
        self.enemy_targets = []

        self.clicker = Clicker(self.battlefield, self.control_panel, self.ring)

        self.icon_5 = PanelObject(self.block_image, (45, 45), self.control_panel.surface)
        self.icon_4 = PanelObject(self.cheese_image, (45, 45), self.control_panel.surface)
        self.icon_6 = PanelObject(self.damage, (45, 45), self.control_panel.surface)
        self.icon_7 = PanelObject(self.cheese_image, (45, 45), self.control_panel.surface)
        self.icon_8 = PanelObject(self.damage, (45, 45), self.control_panel.surface)
        self.clicker.add_ring_object_list([self.icon_4, self.icon_5, self.icon_6, self.icon_7, self.icon_8])

        first_x = 219
        for spot in range(1, 11):
            self.control_panel_spots_dict[spot] = [ControlPanelSpot(self.control_panel.surface, (27, 27),
                                                                    (first_x, 35))]
            first_x += 40
# "Word of light: Holly Fire"
        self.wol_holly_fire = AbilitySkill("Word of light: Holly Fire", 1, 5, 'ability_1.png', 10, 3)

        self.wol_holly_fire.set_description("""Make instance damage to target 
                                      and burn it for time""")

        self.wol_holly_fire.make_effect_list(Ability("health", [-15, -30, -60, -120, -240], "instance"),
                                             Ability("speed", [-15, -30, -60, -120, -240], 5))
# "Word of shadow:Pain"
        self.wos_pain = AbilitySkill("Word of shadow:Pain", 1, 5, 'ability_2.png', 10, "instance")

        self.wol_holly_fire.set_description("""Make instance damage to target 
                                      and burn it for time""")

        self.wos_pain.make_effect_list(Ability("health", [-40, -80, -160, -320, -640], 10))

        self.control_panel_spots_dict[1][0].set_ability(self.wol_holly_fire)
        self.control_panel_spots_dict[2][0].set_ability(self.wos_pain)

    def run(self):
        play = True
        start_time = time.time()
        while play:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    play = False
                if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    if self.clicker.ring_work:
                        self.icon_4.purpose = Target(self.cheese_image, (35, 35), self.battlefield.surface)

                        self.icon_5.purpose = Block(self.block_image, (35, 35), self.battlefield.surface)

                        selected_icon = self.clicker.chose_ring_icon(event.pos)
                        if selected_icon:
                            selected_icon.selected = True
                            print(selected_icon.purpose)
                            self.added_objects_dict_2[self.clicker.point] = selected_icon.purpose
                            self.added_objects_dict_2[self.clicker.point].get_rect_2(self.clicker.point)
                            for enemy in self.enemy_list:
                                enemy.click = True
                    else:
                        self.clicker.click_action(event.pos, self.enemy_list, self.added_objects_dict_2,
                                                  self.control_panel_spots_dict)
                        # control_panel_event
# battlefiel_event

                        for key in self.image_dict:
                            for enemy in self.enemy_list:
                                if self.image_dict[key].collidepoint(enemy.enemy_pos):
                                    enemy.collide_point = key

            for enemy in self.enemy_list:
                if enemy.health <= 0:
                    self.enemy_list.remove(enemy)
                    self.clicker.selected_object = None
                    continue
                enemy.action(self.added_objects_dict_2, self.graph)
                if enemy.killer and enemy.target.position in self.added_objects_dict_2:
                    self.added_objects_dict_2.pop(enemy.target.position)

            self.drawer.from_set(self.battlefield.surface, self.field_set, self.normal_square_obj)

            self.drawer.from_dict(self.control_panel.surface, self.control_panel_dict_2)
            if self.clicker.ring_work:
                self.clicker.draw_ring()

            self.drawer.from_dict(self.battlefield.surface, self.added_objects_dict_2)

            for enemy in self.enemy_list:
                enemy.make_target()
                enemy.affected_ability()

            for spot in self.control_panel_spots_dict:
                if self.control_panel_spots_dict[spot][0].ability:
                    self.control_panel_spots_dict[spot][0].countdown_go()

            for spell in self.control_panel_spots_dict:
                if (self.control_panel_spots_dict[spell][0].ability and
                   self.control_panel_spots_dict[spell][0].ability.clicked and
                   self.control_panel_spots_dict[spell][0].ability.casting_time == "instance"):

                    self.clicker.selected_object.set_affected_ability(
                        self.control_panel_spots_dict[spell][0].ability.ability_summary())
                    self.control_panel_spots_dict[spell][0].ability.clicked = False

                elif (self.control_panel_spots_dict[spell][0].ability and
                      self.control_panel_spots_dict[spell][0].ability.clicked and
                      self.control_panel_spots_dict[spell][0].ability.casting_time != "instance" and
                      self.control_panel_spots_dict[spell][0].ability.casting_timer is None):
                    self.control_panel_spots_dict[spell][0].ability.casting_timer = time.time() #beginig of cast
                    self.control_panel_spots_dict[spell][0].ability.clicked = False

                elif (self.control_panel_spots_dict[spell][0].ability and
                      self.control_panel_spots_dict[spell][0].ability.casting_timer is not None and
                      time.time() - self.control_panel_spots_dict[spell][0].ability.casting_timer >=
                      self.control_panel_spots_dict[spell][0].ability.casting_time):
                    self.clicker.selected_object.set_affected_ability(
                        self.control_panel_spots_dict[spell][0].ability.ability_summary())
                    self.control_panel_spots_dict[spell][0].ability.casting_timer = None
                    print("cat")




            if self.clicker.selected_object is not None:
                self.control_panel.make_selected_object(self.clicker.selected_object)

            self.drawer.one_surface(self.control_panel.surface, self.panel.square, self.panel.rect)

            self.drawer.one_surface(self.main_surface, self.battlefield.surface, self.battlefield.rect)

            self.drawer.one_surface(self.main_surface, self.control_panel.surface, self.control_panel.rect)
            self.control_panel.surface.fill(self.settings.white)

            pg.display.update()
#            if self.clicker.selected_object:
#                print(self.clicker.selected_object.affected_ability_dict)
#                print(self.clicker.selected_object.health)

            self.clock.tick(self.settings.fps)
        pg.quit()

    def empty_square(self, square, enemy_list, obj_list):
        empty = True
        for enemy in enemy_list:
            if not self.image_dict[square].collidepoint(enemy.enemy_pos):
                empty = True
            else:
                empty = False
                break
        if square in obj_list:
            empty = False
        return empty


class FieldObject:

    def __init__(self, image, size, surface):
        self.settings = Settings()
        self.size = size
        self.rect = None
        self.image = image
        self.square = pg.transform.scale(image, self.size)
        self.position = None
        self.max_health = 20
        self.health = 20
        self.surface = surface
        self.health_bar_size_l = 30
        self.health_bar_size_h = 6

    def get_object(self):
        square = pg.transform.scale(self.image, self.size)
        return square

    def get_rect_2(self, center):

        self.rect = self.square.get_rect(center=center)
        self.position = center
        return self.rect

    def make_target(self):
        self.surface.blit(self.square, self.get_rect_2(self.position))
        if self.max_health != self.health:
            self.health_bar()

    def health_bar(self):
        pg.draw.rect(self.surface, self.settings.red, (self.position[0]-self.size[0]//2,
                     self.position[1]-self.size[1]+5, self.health_bar_size_l, self.health_bar_size_h))
        pg.draw.rect(self.surface, self.settings.green, (self.position[0]-self.size[0]//2,
                     self.position[1]-self.size[1]+5, (self.health*self.health_bar_size_l//self.max_health),
                                                         self.health_bar_size_h))


class GrassSquare(FieldObject):
    pass


class Block(FieldObject):
    def __init__(self, image, size, surface):
        super().__init__(image, size, surface)
        self.target_rank = 0
        self.max_health = 5
        self.health = 5


class Target(FieldObject):
    def __init__(self, image, size, surface):
        super().__init__(image, size, surface)
        self.target_rank = 3
        self.max_health = 20
        self.health = 20


class PanelObject(FieldObject):
    def __init__(self, image, size, surface):
        super().__init__(image, size, surface)
        self.selected = False
        self.purpose = None


class Selected_object(FieldObject):
    def __init__(self, image, size, surface):
        super().__init__(image, size, surface)


class ControlPanel:
    def __init__(self):
        self.settings = Settings()
        self.top_left_corner = (0, self.settings.game_field_y)

        self.rect = pg.Rect(self.top_left_corner, (self.settings.control_panel_width,
                                                   self.settings.control_panel_height))
        self.surface = pg.Surface((self.rect.width, self.rect.height))
        self.selected_item = None

    def make_selected_object(self, selected_object):
        if selected_object is not None:
            square = pg.transform.scale(selected_object.square, self.settings.enemy_icon_size)
            self.surface.blit(square, square.get_rect(center=self.settings.enemy_icon_position))
            self.health_bar(selected_object)

    def health_bar(self, selected_object):
        pg.draw.rect(self.surface, self.settings.red, (66, 15, (selected_object.health *
                     self.settings.enemy_panel_health_size[0] // selected_object.max_health),
                                                         self.settings.enemy_panel_health_size[1]))


class Battlefield:
    def __init__(self):
        self.top_left_corner = (0, 0)
        self.settings = Settings()
        self.rect = pg.Rect(self.top_left_corner, (self.settings.game_field_x, self.settings.game_field_y))
        self.surface = pg.Surface((self.rect.width, self.rect.height))
        self.field_width = self.settings.game_field_x
        self.field_height = self.settings.game_field_y
        self.square_size_x = self.settings.square_size_x
        self.square_size_y = self.settings.square_size_y
        self.f_set = set()
        self.array = None
        self.rect_dict = {}
        self.number_of_squares = (self.settings.square_number_x, self.settings.square_number_y)
        self.rad = 1
        self.grath = {}
        self.r_long_row = None
        self.r_short_row = None

    def get_field_array(self):
        """
        make a array from field_width field_height and number_of_squares
        :return:
        """
        array_j = []
        array_i = []
        n = 3
        i = self.square_size_y / 2
        while i <= self.field_height:
            if n % 2 == 1:
                j = self.square_size_x / 2
                while j <= self.field_width:
                    array_j.append((j, i))
                    j += self.square_size_x
                array_i.append(array_j)
                array_j = []
                n += 1
            else:
                j = 0
                while j <= self.field_width:
                    array_j.append((j, i))
                    j += self.square_size_x
                array_i.append(array_j)
                array_j = []
                n += 1
            i += self.square_size_y
            self.array = array_i
        return array_i

    def field_set(self):
        for i in range(len(self.array)):
            for j in range(len(self.array[i])):
                self.f_set.add(self.array[i][j])
        return self.f_set

    def __around_long_row(self):
        """
        make a list of vertexes there oyu may go from current for odd lines
        :return:
        """
        list_of_cord = []
        for i in range(-self.rad, self.rad + 1):
            for j in range(-self.rad, self.rad + 1):
                if (i == 0 and j == 0) or (i != 0 and j == 1):
                    continue
                list_of_cord.append((i, j))
        return list_of_cord

    def __around_short_row(self):
        """
        make a list of vertexes there oyu may go from current for even lines
        :return:
        """
        list_of_cord = []
        for i in range(-self.rad, self.rad + 1):
            for j in range(-self.rad, self.rad + 1):
                if (i == 0 and j == 0) or (i != 0 and j == -1):
                    continue
                list_of_cord.append((i, j))
        return list_of_cord

    def get_graph(self):
        """
        make a grath from array
        :return: grath in a form of dictionary
        """
        self.array = self.get_field_array()
        self.r_long_row = self.__around_long_row()
        self.r_short_row = self.__around_short_row()
        grath = {}
        max_y = self.number_of_squares[1]
        max_x = self.number_of_squares[0]
        for i in range(1, max_y + 1):
            if i % 2 == 0:
                end = 2
                r = self.r_long_row
            else:
                end = 1
                r = self.r_short_row
            for j in range(1, max_x + end):

                if self.array[i - 1][j - 1] not in grath:
                    grath[self.array[i - 1][j - 1]] = set()
                    for i_s, j_s in r:
                        if 0 < i + i_s < max_y + 1 and 0 < j + j_s < len(self.array[i + i_s - 1]) + 1:
                            grath[self.array[i - 1][j - 1]].add(self.array[i + i_s - 1][j + j_s - 1])
        self.grath = grath
        return self.grath

    def get_rect_dict(self, square):
        for point in self.f_set:
            square.get_rect_2(point)
            self.rect_dict[point] = square.rect
        return self.rect_dict


class Drawer:
    def __init__(self):
        pass

    @staticmethod
    def one_surface(surface, obj_surface, obj_rect):
        surface.blit(obj_surface, obj_rect)

    @staticmethod
    def from_set(surface, draw_set, obj_image):
        for dot in draw_set:
            rect = obj_image.get_rect(center=dot)
            surface.blit(obj_image, rect)

    @staticmethod
    def from_dict(surface, draw_dict):
        for obj in draw_dict:
            surface.blit(draw_dict[obj].square, draw_dict[obj].get_rect_2(obj))

    @staticmethod
    def health_bar(surface, draw_dict, hb_size):
        pass


class Enemy:
    def __init__(self, health, surface, field_set, image, size):
        self.field_set = field_set
        self.settings = Settings()
        self.x = 0
        self.y = 0
        self.r = 10
        self.dx = 0
        self.dy = 0
        self.surface = surface
        self.enemy_pos = (self.x, self.y)
        self.collide_point = None
        self.path = None
        self.new_path = True
        self.size = size
        self.level = 1
        self.max_health = health
        self.health = health
        self.attack_step = 120
        self.attack_speed = 120
        self.damage = 2
        self.target_priority_min = 1
        self.target_dict = {}
        self.target_priority_dict = {}
        self.target = None
        self.rage = False
        self.go_to = None
        self.killer = False
        self.click = False
        self.in_attack = False
        self.speed = 50
        self.rect = None
        self.square = pg.transform.scale(image, self.size)
        self.affected_ability_dict = {}

    def target_priority(self):
        max_target_rank = self.target_priority_min
        self.target_priority_dict.clear()
        for target in self.target_dict:
            if self.target_dict[target].target_rank > max_target_rank:
                self.target_priority_dict.clear()
                max_target_rank = self.target_dict[target].target_rank
                self.target_priority_dict[target] = self.target_dict[target]
            elif self.target_dict[target].target_rank == max_target_rank:
                self.target_priority_dict[target] = self.target_dict[target]
        return self.target_priority_dict

    def start_point(self, x, y):
        self.x = x
        self.y = y
        self.enemy_pos = self.enemy_pos
        return self.enemy_pos

    def get_rect_2(self):

        self.rect = self.square.get_rect(center=(self.x, self.y))
        return self.rect

    def make_target(self):
        self.surface.blit(self.square, self.get_rect_2())
        if self.max_health != self.health:
            self.health_bar()

    def make_a_path_2(self, blocked, graph):
        blocked = list(blocked.keys())
        if not self.target_priority_dict:
            self.path = []
            return self.path
        else:
            parents = []
            if not self.rage:
                parents = self.__path_from_graph(self.enemy_pos, graph, self.collide_point, blocked)
            if self.rage:
                blocked = []
                parents = self.__path_from_graph(self.enemy_pos, graph, self.collide_point, blocked)

            self.path = [self.go_to]

            parent = parents[self.go_to]

            while parent != self.enemy_pos:
                self.path.append(parent)
                parent = parents[parent]
            self.path.append(self.enemy_pos)
            if self.collide_point is not None:
                if (path_len((self.enemy_pos[0] - self.path[-1][0]), (self.enemy_pos[1] - self.path[-1][1])) <
                   path_len((self.collide_point[0] - self.path[-1][0]), (self.collide_point[1] - self.path[-1][1]))
                   and len(self.path) >= 4):
                    self.path.remove(self.collide_point)
            self.path.pop(0)
            return self.path

    def __path_from_graph(self, go_from, graph, collide_point, blocked):
        parents_nearest = None
        distance_to_closest_target = 400000
        for target in self.target_priority_dict:
            graph_2 = copy.deepcopy(graph)
            parents = {}
            distance = {go_from: 0}
            queue = deque([go_from])
            if collide_point is not None and collide_point != go_from:
                cat = collide_point
                if cat == go_from:
                    print("CATCH YOU")
                graph_2[go_from] = {cat}
                graph_2[cat].add(go_from)
            for block in blocked:
                graph_2[block] = ()
            while queue:
                current_vertex = queue.popleft()
                for vertex in graph_2[current_vertex]:

                    if vertex not in distance:
                        distance[vertex] = distance[current_vertex] + 1
                        parents.update({vertex: current_vertex})
                        queue.append(vertex)
            if target not in distance:
                continue

            if distance_to_closest_target >= distance[target]:
                distance_to_closest_target = distance[target]
                self.go_to = target
                self.distance_to_target = distance_to_closest_target
                if (self.target is None or self.target.target_rank < self.target_priority_dict[target].target_rank
                        or distance[self.target.position] >= distance[target]):
                    self.target = None
                    self.target = self.target_priority_dict[target]
                parents_nearest = parents
        if parents_nearest is None:
            self.rage = True
            return
        else:
            return parents_nearest

    def action(self, added_objects_dict, graph):
        if self.click:
            self.path = []
            self.new_path = True
            self.target_dict = added_objects_dict
            self.target_priority_dict = self.target_priority()
            self.make_a_path_2(added_objects_dict, graph)
            self.click = False

        if not self.path and not self.in_attack:
            self.enemy_pos = (self.x, self.y)

        elif len(self.path) == 1 or self.in_attack:
            self.attack(added_objects_dict)

        elif not self.in_attack:
            self.movement()
            if self.target not in added_objects_dict.values() and self.enemy_pos in self.field_set:
                self.click = True
        if self.target not in added_objects_dict.values():
            self.target = None

    def step_calk(self):
        if len(self.path) == 1:
            move_from_x = self.path[0][0]
            move_from_y = self.path[0][1]

            move_to_x = self.target.position[0]
            move_to_y = self.target.position[1]

        else:
            move_from_x = self.path[-1][0]
            move_from_y = self.path[-1][1]

            move_to_x = self.path[-2][0]
            move_to_y = self.path[-2][1]
        len_path = path_len((move_to_x - move_from_x), (move_to_y - move_from_y))
        d_step = len_path / (self.speed*0.01)
        if move_to_x != move_from_x:
            k = (move_to_y - move_from_y) / (move_to_x - move_from_x)
            d_step_x = (move_to_x - move_from_x) / d_step
            self.dx = d_step_x
            self.dy = k * self.dx

        else:
            self.dx = 0
            d_step_y = (move_to_y - move_from_y) / d_step
            self.dy = d_step_y

    def movement(self):
        self.step_calk()
        if len(self.path) == 1:
            self.enemy_pos = (self.x, self.y)
        else:

            if self.path[-2][0] != self.path[-1][0]:
                self.x += self.dx
                self.y += self.dy
                if abs(self.path[-2][0] - self.x) < abs(self.dx):
                    self.x = self.path[-2][0]
                    self.y = self.path[-2][1]
                    self.enemy_pos = (self.x, self.y)
                    self.path.pop()

            else:
                self.y += self.dy
                if abs(self.path[-2][1] - self.y) < self.dy:
                    self.x = self.path[-2][0]
                    self.y = self.path[-2][1]
                    self.path.pop()
            self.enemy_pos = (self.x, self.y)

    def health_bar(self):
        pg.draw.rect(self.surface, self.settings.red, (self.x-self.r-5, self.y-self.r-10, 30, 6))
        pg.draw.rect(self.surface, self.settings.green, (self.x-self.r-5, self.y-self.r-10,
                                                         (self.health*30//self.max_health), 6))

    def attack(self, added_objects_dict):
        if not self.in_attack:
            self.step_calk()
        self.in_attack = True
        if 60 < self.attack_step <= self.attack_speed:
            self.x += self.dx
            self.y += self.dy
            self.attack_step -= 1
        elif self.attack_step == self.attack_speed//2:
            if self.target in added_objects_dict.values() and len(self.path) == 1:
                self.target.health -= self.damage
                if self.target.health <= 0:
                    self.killer = True
            self.attack_step -= 1
        elif 0 < self.attack_step < self.attack_speed//2:
            self.killer = False
            self.x -= self.dx
            self.y -= self.dy
            self.attack_step -= 1
        elif self.attack_step == 0:
            self.attack_step = self.attack_speed
            self.x -= self.dx
            self.y -= self.dy
            print(self.path)
            self.collide_point = self.path[0]
            self.in_attack = False
            if self.target not in added_objects_dict.values():
                self.target = None
                self.click = True
                self.in_attack = False
                self.path = []
                self.killer = False

    def set_affected_ability(self, ability):
        self.affected_ability_dict.update(ability)

    def affected_ability(self):
        for ability in self.affected_ability_dict:
            for effect in self.affected_ability_dict[ability]:
                if effect:
                    if effect.affected_time == "instance":
                        self.health += effect.quantity

                        self.affected_ability_dict[ability].remove(effect)

                    elif effect.start_time is None:
                        effect.start_time = time.time()
                        if effect.ability_type == "speed":
                            self.speed += effect.quantity

                    elif time.time()-effect.start_time >= 1:
                        effect.start_time += 1
                        effect.affected_time_counter -= 1
                        if effect.ability_type == "health":
                            self.health += effect.quantity/effect.affected_time

                        if effect.affected_time_counter < 1:
                            if effect.ability_type == "speed":
                                self.speed -= effect.quantity

                            self.affected_ability_dict[ability].remove(effect)

            if not self.affected_ability_dict[ability]:
                self.affected_ability_dict.pop(ability)
            return


class Clicker:
    def __init__(self, battlefield, control_panel, ring):
        self.settings = Settings()
        self.drawer = Drawer()
        self.selected_object = None
        self.mouse_pose = ()
        self.battlefield = battlefield
        self.control_panel = control_panel
        self.enemy_list = None
        self.obj_list = None
        self.battle_rect_dict = self.battlefield.rect_dict
        self.ring = ring
        self.ring_work = False
        self.ring_object_list = []
        self.point = None
        self.icon_rect_list = []
        self.icon_ring_point_dict = {}

    def add_ring_object_list(self, ring_object_list):
        self.ring_object_list = ring_object_list

    def click_action(self, mouse_pos, enemy_list, obj_list, control_panel_spots_dict):
        self.mouse_pose = mouse_pos
        self.enemy_list = enemy_list
        self.obj_list = obj_list
        if self.battlefield.rect.collidepoint(mouse_pos):
            self.__selection(enemy_list)
            self.battlefield_click()
        elif self.control_panel.rect.collidepoint(mouse_pos):
            for spot in control_panel_spots_dict:
                if self.selected_object and (control_panel_spots_dict[spot][0].spot_surface_rect.collidepoint(
                        (mouse_pos[0], mouse_pos[1] - self.settings.game_field_y)) and
                        not control_panel_spots_dict[spot][0].clicked and
                        not control_panel_spots_dict[spot][0].global_countdown_active):
                    control_panel_spots_dict[spot][0].clicked = True
                    control_panel_spots_dict[spot][0].ability.clicked = True

                    control_panel_spots_dict[spot][0].start_time = time.time()

                    for spot_2 in control_panel_spots_dict:
                        if not control_panel_spots_dict[spot_2][0].clicked:
                            control_panel_spots_dict[spot_2][0].global_countdown_active = True
                            control_panel_spots_dict[spot_2][0].start_time = time.time()

    def __selection(self, enemy_list):
        for enemy in enemy_list:
            if enemy.rect.collidepoint(self.mouse_pose):
                self.selected_object = enemy

    def battlefield_click(self):
        for point in self.battle_rect_dict:
            if self.battle_rect_dict[point].collidepoint(self.mouse_pose):
                if self.empty_square(point):
                    self.ring_work = True
                    self.point = point
                    self.action_selection()

    def empty_square(self, point):
        empty = True
        for enemy in self.enemy_list:
            if not self.battle_rect_dict[point].collidepoint(enemy.enemy_pos):
                empty = True
            else:
                empty = False
                break
        if point in self.obj_list:
            empty = False
        return empty

    def action_selection(self):
        self.icon_ring_point_dict.clear()
        angle = 0
        d_angle = 2*pi/5
        self.icon_rect_list = []
        for icon in self.ring_object_list:
            y = cos(angle)*65
            x = sin(angle)*65
            point = (self.ring.size[0]/2+x, self.ring.size[1]/2-y)
            self.icon_ring_point_dict[point] = icon
            self.icon_ring_point_dict[point].get_rect_2(point)

            angle += d_angle

        self.ring_work = True

    def draw_ring(self):
        self.ring.get_rect_2(self.point)
        self.drawer.one_surface(self.battlefield.surface, self.ring.square, self.ring.rect)
        for key in self.icon_ring_point_dict:
            self.drawer.one_surface(self.ring.square, self.icon_ring_point_dict[key].square,
                                    self.icon_ring_point_dict[key].rect)

    def chose_ring_icon(self, mouse_pose):
        selected = None
        for key in self.icon_ring_point_dict:

            if self.icon_ring_point_dict[key].rect.collidepoint((mouse_pose[0]-self.point[0]+100,
                                                                 mouse_pose[1]-self.point[1]+100)):
                selected = self.icon_ring_point_dict[key]
        self.ring_work = False
        return selected


class ControlPanelSpot:
    def __init__(self, surface, size_c, position):
        self.settings = Settings()
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
        self.spot_surface.set_colorkey(self.settings.red)
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
            self.spot_surface.fill(self.settings.black)
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

                pg.draw.polygon(self.spot_surface, self.settings.red, point_list)
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


class Ability:
    def __init__(self, ability_type, quantity, affected_time):
        self.ability_type = ability_type
        self.quantity = quantity
        self.affected_time = affected_time

class AbilitySkill:
    def __init__(self, name, lvl, max_lvl, image_icon, countdown_time, casting_time):
        self.name = name
        self.lvl = lvl
        self.max_lvl = max_lvl
        self.countdown_time = countdown_time
        self.__description = None
        self.effect_list = []
        self.icon = pg.image.load(image_icon)
        self.image = pg.image.load(image_icon)
        self.ability_dict = {}
        self.casting_time = casting_time
        self.clicked = False
        self.casting_timer = None

    def set_description(self, desc):
        self.__description = desc

    def make_effect_list(self, *args):
        for arg in args:
            self.effect_list.append(arg)

    def ability_summary(self):
        self.ability_dict[self.name] = []
        for effect in self.effect_list:
            self.ability_dict[self.name].append(AbilityTrans(self.icon, effect.ability_type,
                                                             effect.quantity[self.lvl-1], effect.affected_time))
        return self.ability_dict


class AbilityTrans:
    def __init__(self, icon, ability_type, quantity, affected_time):
        self.icon = icon
        self.ability_type = ability_type
        self.quantity = quantity
        self.affected_time = affected_time
        self.affected_time_counter = affected_time
        self.start_time = None
        self.cat = 0


my_game = Game()

my_game.run()
