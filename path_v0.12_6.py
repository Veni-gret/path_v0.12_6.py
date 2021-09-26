import pygame as pg
from collections import deque
import time
import copy
from settings import Settings
from math import hypot as path_len

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
LIGHT_BLUE = (64, 128, 255)
GREEN = (0, 200, 64)
YELLOW = (225, 225, 0)
PINK = (230, 50, 230)
PI = 3.14
RED = (225, 0, 50)
FPS = 60

# mouse eat cheese
# add icon for damage
# do damage to mouse
# if enemy hit target and i add block base square become availible MASS refactor

class Game:
    def __init__(self):
        self.settings = Settings()
        self.WIN_WIDTH = 800
        self.WIN_HEIGHT = 600
        self.square_number_x = 16
        self.square_number_y = 10
        self.game_field_x = 800
        self.game_field_y = 500

        self.block_image = pg.image.load('4.png')
        self.normal_square_image = pg.image.load('Grass_finish.bmp')
        self.cheese_image = pg.image.load('cheese.png')

        self.rect_dict = {}
        self.image_dict = {}

#        self.bl = Block()

        self.main_surface = pg.display.set_mode((self.settings.win_width, self.settings.win_height))
        self.square_size_x = self.game_field_x // self.square_number_x
        self.square_size_y = self.game_field_y // self.square_number_y
        self.battlefield = Battlefield()
        self.graph = self.battlefield.graph_make()
        self.field_set = self.battlefield.field_set()
        self.normal_square = FieldObject(self.normal_square_image, (50, 50),self.battlefield.surface)
        self.cheese = FieldObject(self.cheese_image, (25, 25),self.battlefield.surface)

        for point in self.field_set:
            self.rect_dict[point] = self.normal_square.get_rect(point)
            self.image_dict[point] = self.normal_square.place(point)

        self.added_objects_dict = {}
        self.added_objects_dict_2 = {}

# Control panel
        self.control_panel_dict_2 = {}

        self.control_panel = ControlPanel()
        self.icon_1 = PanelObject(self.block_image, (50, 50), self.control_panel.surface)
        self.icon_2 = PanelObject(self.cheese_image, (50, 50), self.control_panel.surface)
        self.icon_1.get_rect((25, 25))
        self.icon_2.get_rect((75, 25))

        self.control_panel_dict_2[self.icon_1.position] = self.icon_1
        self.control_panel_dict_2[self.icon_2.position] = self.icon_2

#       self.control_panel_width = 800
#       self.control_panel_height = 100
        self.clock = pg.time.Clock()
        self.step = 0
        self.control_panel.surface.fill(self.settings.white)
        self.battlefield.surface.fill(self.settings.white)
        self.enemy_list = []
        self.enemy_number = 4
        for enemy in range(self.enemy_number):
            enemy = Enemy(50, self.battlefield.surface)
            self.enemy_list.append(enemy)

        self.block_point_list = []
        y = 25.0
        for enemy in self.enemy_list:
            enemy.start_point(25.0, y)
            y += 100.0
        self.path_change = False
        self.back_on_path = False
        self.enemy_targets = []

    def run(self):
        play = True
        for square in self.block_point_list:
            self.added_objects_dict[square] = Block(self.block_image, (35, 35),self.battlefield.surface)
        start_time = time.time()
        while play:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    play = False
                if event.type == pg.MOUSEBUTTONUP and time.time()-start_time > 0.2:

                    # control_panel_event
                    for key in self.control_panel_dict_2:
                        if self.control_panel_dict_2[key].rect.collidepoint((event.pos[0], event.pos[1]-self.game_field_y)):
                            self.control_panel.selected_item = self.control_panel_dict_2[key]
                    # battlefiel_event
                    for key in self.image_dict:
                        for enemy in self.enemy_list:
                            if self.image_dict[key][1].collidepoint(enemy.enemy_pos):
                                enemy.collide_point = key

                        if self.image_dict[key][1].collidepoint(event.pos):

                            # check empty square or not
                            empty = True
                            for enemy in self.enemy_list:
                                if not self.image_dict[key][1].collidepoint(enemy.enemy_pos):
                                    empty = True
                                else:
                                    empty = False
                                    break
                            if key in self.added_objects_dict_2:
                                empty = False

                            if empty and self.control_panel.selected_item:
                                self.icon_1.purpose = Block(self.block_image, (35, 35), self.battlefield.surface)
                                self.icon_2.purpose = Target(self.cheese_image, (35, 35), self.battlefield.surface)
                                self.added_objects_dict_2[key] = self.control_panel.selected_item.purpose
                                self.added_objects_dict_2[key].get_rect(key)
#                                if self.added_objects_dict_2[key].target_rank == 0:
                                self.block_point_list.append(key)

                            start_time = time.time()

                            self.enemy_targets = []
                            for obj in self.added_objects_dict_2:
                                if self.added_objects_dict_2[obj].target_rank > 0:
                                    self.enemy_targets.append(self.added_objects_dict_2[obj])

                            for enemy in self.enemy_list:
                                enemy.path = []
                                enemy.new_path = True
                                enemy.target_list = self.enemy_targets
                            self.path_change = False

            if not self.path_change:
                for enemy in self.enemy_list:
                    enemy.make_a_path_2(self.block_point_list, self.graph)

                self.path_change = True
            for enemy in self.enemy_list:
                enemy.action()

            self.battlefield.draw_objects(self.image_dict)
            self.control_panel.draw_objects_2(self.control_panel_dict_2)

            for obj in self.added_objects_dict_2:
                self.added_objects_dict_2[obj].make_target()

            for enemy in self.enemy_list:
                enemy.make_enemy(enemy.enemy_pos)
            self.battlefield.draw(self.main_surface)
            self.control_panel.draw(self.main_surface)

            pg.display.update()

            self.clock.tick(FPS)
        pg.quit()


class FieldObject:

    def __init__(self, image, size, surface):
        self.settings = Settings()
        self.size = size
        self.rect = None
        self.square = pg.transform.scale(image, self.size)
        self.position = None
        self.max_health = 20
        self.health = 20
        self.surface = surface

    def get_rect(self, center):

        self.rect = self.square.get_rect(center=center)
        self.position = center
        return self.rect

    def place(self, center):
        place = [self.square, self.get_rect(center)]
        return place

    def make_target(self):
        self.surface.blit(self.square, self.get_rect(self.position))
        if self.max_health != self.health:
            self.health_bar()

    def health_bar(self):
        pg.draw.rect(self.surface, self.settings.red, (self.position[0]-self.size[0]//2, self.position[1]-self.size[1]+5, 30, 6))
        pg.draw.rect(self.surface, self.settings.green, (self.position[0]-self.size[0]//2, self.position[1]-self.size[1]+5, (self.health*30//self.max_health), 6))



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
        self.surface = surface



class PanelObject(FieldObject):
    def __init__(self, image, size, surface):
        super().__init__(image, size, surface)
        self.selected = False
        self.purpose = None


class ControlPanel:
    def __init__(self):
        self.settings = Settings()
        self.top_left_corner = (0, self.settings.game_field_y)

        self.rect = pg.Rect(self.top_left_corner, (self.settings.control_panel_width, self.settings.control_panel_height))
        self.surface = pg.Surface((self.rect.width, self.rect.height))
        self.selected_item = None

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def draw_objects_2(self, objects_dict):
        for key in objects_dict:
            self.surface.blit(objects_dict[key].square, objects_dict[key].get_rect(key))


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
        self.array = self.__field_array()
        self.number_of_squares = (self.settings.square_number_x, self.settings.square_number_y)
        self.rad = 1
        self.grath = {}
        self.r_long_row = self.__around_long_row()
        self.r_short_row = self.__around_short_row()

    def __field_array(self):
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

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def draw_objects(self, objects_dict):
        for key in objects_dict:
            self.surface.blit(objects_dict[key][0], objects_dict[key][1])

    def draw_objects_2(self, objects_dict):
        for key in objects_dict:
            self.surface.blit(objects_dict[key].square, objects_dict[key].get_rect(key))

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

    def graph_make(self):
        """
        make a grath from array
        :return: grath in a form of dictionary
        """
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


class Enemy:
    def __init__(self, health, surface):
        self.x = 0
        self.y = 0
        self.r = 10
        self.dx = 0
        self.dy = 0
        self.surface = surface
        self.enemy_pos = (self.x, self.y)
        self.step = 0
        self.collide_point = None
        self.rat_path = PathMaker()
        self.next_step = None
        self.enemy_rage = None
        self.path = None
        self.max_health = health
        self.health = 25
        self.level = 1
        self.settings = Settings()
        self.new_path = True
        self.ready_for_attack = False
        self.attack_step = 120
        self.target_list = []
        self.target = None
        self.rage = False
        self.go_to = None
    def start_point(self, x, y):
        self.x = x
        self.y = y
        self.enemy_pos = self.enemy_pos
        return self.enemy_pos

    def make_enemy(self, pos):
        self.enemy_rage = self.rat_path.rage
        if not self.enemy_rage:
            pg.draw.circle(self.surface, GREEN, (pos[0], pos[1]), self.r)

            self.health_bar()
        else:
            pg.draw.circle(self.surface, RED, (pos[0], pos[1]), self.r*2)

    def make_a_path_2(self, blocked, graph):
        if not self.target_list:
            path = (self.x, self.y)
            self.path = path
            return path
        else:
            print(self.target_list)
            if not self.rage:
                parents = self.__path_from_graph(self.enemy_pos, self.target_list, graph, self.collide_point, blocked)
            if self.rage:
                blocked = []
                parents = self.__path_from_graph(self.enemy_pos, self.target_list, graph, self.collide_point, blocked)

            self.path = [self.go_to]

            parent = parents[self.go_to]

            while parent != self.enemy_pos:
                self.path.append(parent)
                parent = parents[parent]
            self.path.append(self.enemy_pos)
            if self.collide_point is not None:
                self.point_2 = self.next_step
                if self.point_2 in self.path and (
                        path_len((self.enemy_pos[0] - self.point_2[0]), (self.enemy_pos[1] - self.point_2[1])) <
                        path_len((self.collide_point[0] - self.point_2[0]), (self.collide_point[1] - self.point_2[1]))
                ):
                    self.path.remove(self.collide_point)
            return self.path

    def __path_from_graph(self, go_from, target_list, graph, collide_point, blocked):
        parents_nearest = None
        distance_to_closest_target = 400000
        for target in target_list:
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
            if target.position not in distance:
                continue

            if distance_to_closest_target >= distance[target.position]:
                distance_to_closest_target = distance[target.position]
                self.go_to = target.position
                self.distance_to_target = distance_to_closest_target
                self.target = target
                parents_nearest = parents
        if parents_nearest is None:
            self.rage = True
            return
        else:
            return parents_nearest

    def give_target(self):
        return self.target


    def make_a_path(self, blocked, graph):
        if not self.target_list:
            path = (self.x, self.y)
            self.path = path
            return path
        else:
            path = self.rat_path.levenstein(self.enemy_pos, self.target_list, blocked, self.collide_point, self.next_step, graph)
            self.path = path
            return path

    def action(self):
        if not self.target_list:
            self.enemy_pos = (self.x, self.y)
        else:
            if self.ready_for_attack:
                self.hit()

            if self.new_path:
                self.step_calk()
            self.movement()

    def step_calk(self):
        move_from_x = self.path[-1][0]
        move_from_y = self.path[-1][1]

        move_to_x = self.path[-2][0]
        move_to_y = self.path[-2][1]
        len_path = path_len((move_to_x - move_from_x), (move_to_y - move_from_y))
        d_step = len_path / 0.5
        if move_to_x != move_from_x:
            k = (move_to_y - move_from_y) / (move_to_x - move_from_x)
            d_step_x = (move_to_x - move_from_x) / d_step
            self.dx = d_step_x
            self.dy = k * self.dx

        else:
            self.dx = 0
            d_step_y = (move_to_y - move_from_y) / d_step
            self.dy = d_step_y
        self.new_path = False

    def movement(self):
        if len(self.path) <= 2:
            self.enemy_pos = (self.x, self.y)
            self.ready_for_attack = True
            print(self.target)
        else:
            if self.x != self.path[-2][0]:
                if self.path[-2][0] != self.path[-1][0]:
                    self.x += self.dx
                    self.y += self.dy
                    if abs(self.path[-2][0] - self.x) < abs(self.dx):
                        self.x = self.path[-2][0]
                        self.y = self.path[-2][1]
                        self.enemy_pos = (self.x, self.y)
                        self.path.pop()
                        self.new_path = True

                else:
                    self.y += self.dy
                    if abs(self.path[-2][1] - self.y) < self.dy:
                        self.x = self.path[-2][0]
                        self.y = self.path[-2][1]
                        self.path.pop(0)
                        self.new_path = True
            else:
                self.path.pop(0)
                self.new_path = True
            self.next_step = self.path[-2]
            self.enemy_pos = (self.x, self.y)

    def health_bar(self):
        pg.draw.rect(self.surface, self.settings.red, (self.x-self.r-5, self.y-self.r-10, 30, 6))
        pg.draw.rect(self.surface, self.settings.green, (self.x-self.r-5, self.y-self.r-10, (self.health*30//self.max_health), 6))

    def hit(self):
        if 60 < self.attack_step <= 120:
            self.x += self.dx
            self.y += self.dy
            self.attack_step -= 1
        elif 0 < self.attack_step <= 60:
            self.x -= self.dx
            self.y -= self.dy
            self.attack_step -= 1
        else:
            self.x = self.path[-1][0]
            self.y = self.path[-1][1]
            self.attack_step = 120


class PathMaker:
    """
    Make a path in grath( array (X;Y))
    """

    def __init__(self, rad=1):
        self.settings = Settings()
        self.go_to = (0, 0)
        self.go_from = (0, 0)
        self.number_of_squares = (self.settings.square_number_x, self.settings.square_number_y)
        self.field_width = self.settings.game_field_x
        self.field_height = self.settings.game_field_y
        self.rad = rad
        self.grath = {}
        self.in_the_square = False
        self.square_size_x = self.field_width / self.number_of_squares[0]  # in the short line
        self.square_size_y = self.field_height / self.number_of_squares[1]
        self.path = []
        self.point_2 = None
        self.rage = False
        self.distance_to_target = None
        self.go_to = None
        self.target = None


    def levenstein(self, go_from, target_list, blocked, collide_p, next_step, graph):
        """
        Make a path in grath from  start point to the end point
        :param target_list:
        :param graph:
        :param next_step:
        :param collide_p:
        :param go_from: start point on grath
        :param blocked: point not allow to use
        :return: path in form of list of vertexes (array indexes(i, j))
        """

        print(target_list)
        if not self.rage:
            parents = self.__path_from_graph(go_from, target_list, graph, collide_p, blocked)
        if self.rage:
            blocked = []
            parents = self.__path_from_graph(go_from, target_list, graph, collide_p, blocked)


        self.path = [self.go_to]

        parent = parents[self.go_to]

        while parent != go_from:
            self.path.append(parent)
            parent = parents[parent]
        self.path.append(go_from)
        if collide_p is not None:
            self.point_2 = next_step
            if self.point_2 in self.path and (path_len((go_from[0]-self.point_2[0]), (go_from[1]-self.point_2[1])) <
                                              path_len((collide_p[0] - self.point_2[0]), (collide_p[1] - self.point_2[1]))
                                              ):
                self.path.remove(collide_p)
        return self.path

    def __path_from_graph(self, go_from, target_list, graph, collide_point, blocked):
        parents_nearest = None
        distance_to_closest_target = 400000
        for target in target_list:
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
            if target.position not in distance:
                continue

            if distance_to_closest_target >= distance[target.position]:
                distance_to_closest_target = distance[target.position]
                self.go_to = target.position
                self.distance_to_target = distance_to_closest_target
                self.target = target
                parents_nearest = parents
        if parents_nearest is None:
            self.rage = True
            return
        else:
            return parents_nearest

    def give_target(self):
        return self.target

my_game = Game()

my_game.run()
