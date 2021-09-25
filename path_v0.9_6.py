import pygame as pg
from collections import deque
import time
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
# make a hit function
# place cheese with mouse click
# make two icon for block and cheese

class Game:
    def __init__(self):
        self.settings = Settings()
        self.WIN_WIDTH = 800
        self.WIN_HEIGHT = 600
        self.square_number_x = 16
        self.square_number_y = 10
        self.game_field_x = 800
        self.game_field_y = 500

        self.rect_dict = {}
        self.image_dict = {}

        self.main_surface = pg.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.square_size_x = self.game_field_x // self.square_number_x
        self.square_size_y = self.game_field_y // self.square_number_y
        self.battlefield = Battlefield()
        self.field_set = self.battlefield.field_set()
        self.block = FieldObject((35, 35))
        self.block.get_image('4.png')
        self.normal_square = FieldObject((50, 50))
        self.normal_square.get_image('Grass_finish.bmp')
        self.cheese = FieldObject((25, 25))
        self.cheese.get_image('cheese.png')

        for point in self.field_set:
            self.rect_dict[point] = self.normal_square.get_rect(point)
            self.image_dict[point] = self.normal_square.place(point)


        self.added_objects_dict = {}


#       self.control_panel_width = 800
#       self.control_panel_height = 100
        self.clock = pg.time.Clock()
        self.step = 0

        self.battlefield.surface.fill(WHITE)
        self.enemy_list = []
        self.blocked = None
        self.enemy_number = 4
        for enemy in range(self.enemy_number):
            enemy = Enemy(50, self.battlefield.surface)
            self.enemy_list.append(enemy)

        self.block_point_list = []
        y = 25
        for enemy in self.enemy_list:
            enemy.start_point(25, y)
            y += 100
        self.path_change = False
        self.back_on_path = False

    def run(self):
        play = True
        print(self.rect_dict)
        print(self.field_set)
        print(self.image_dict)
        for square in self.block_point_list:
            self.added_objects_dict[square] = self.block.place(square)
        for enemy in self.enemy_list:
            print(enemy)
            enemy.make_a_path(self.block_point_list)
        start_time = time.time()
        self.added_objects_dict[(775, 25)] = self.cheese.place((775, 25))
        while play:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    play = False
                if event.type == pg.MOUSEBUTTONUP and time.time()-start_time > 0.2:
                    for key in self.image_dict:
                        for enemy in self.enemy_list:
                            if self.image_dict[key][1].collidepoint(enemy.enemy_pos):
                                enemy.collide_point = key

                        if self.image_dict[key][1].collidepoint(event.pos):
                            for enemy in self.enemy_list:
                                if not self.image_dict[key][1].collidepoint(enemy.enemy_pos):
                                    empty = True
                                else:
                                    empty = False
                                    break
                            if empty:
                                self.added_objects_dict[key] = self.block.place(key)
                                self.block_point_list.append(key)
                            start_time = time.time()

                            for enemy in self.enemy_list:
                                enemy.path = []
                            self.path_change = False


            if not self.path_change:
                for enemy in self.enemy_list:
                    enemy.make_a_path(self.block_point_list)
                self.path_change = True
            for enemy in self.enemy_list:
                enemy.move_to()

            self.battlefield.draw_objects(self.image_dict)
            self.battlefield.draw_objects(self.added_objects_dict)
            for enemy in self.enemy_list:
                enemy.make_enemy(enemy.enemy_pos)
            self.battlefield.draw(self.main_surface)
            pg.display.update(self.battlefield.rect)

            self.clock.tick(FPS)
        pg.quit()


class FieldObject:
    def __init__(self, size):
        self.size = size
        self.square = None
        self.rect = None

    def get_image(self, image):
        self.square = pg.image.load(image)
        self.square = pg.transform.scale(self.square, self.size)

    def get_rect(self, center):

        self.rect = self.square.get_rect(center=center)
        return self.rect

    def place(self, center):
        place = [self.square, self.get_rect(center)]
        return place


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

    def start_point(self, x, y):
        self.x = x
        self.y = y
        self.enemy_pos = (self.x, self.y)
        return self.enemy_pos

    def make_enemy(self, pos):
        self.enemy_rage = self.rat_path.rage
        if not self.enemy_rage:
            pg.draw.circle(self.surface, GREEN, (pos[0], pos[1]), self.r)

            self.health_bar()
        else:
            pg.draw.circle(self.surface, RED, (pos[0], pos[1]), self.r*2)

    def make_a_path(self, blocked):
        path = self.rat_path.levenstein(self.enemy_pos, (775, 25), blocked, self.collide_point, self.next_step)
        self.path = path
        return path

    def action(self):
        if self.new_path:
            self.step_calk()

    def step_calk(self):
        move_from_x = self.path[-1][0]
        move_from_y = self.path[-1][1]

        move_to_x = self.path[-2][0]
        move_to_y = self.path[-2][1]
        len_path = path_len((move_to_x - move_from_x), (move_to_y - move_from_y))
        d_step = len_path / 0.5
        if self.x != move_to_x:
            if move_to_x != move_from_x:
                k = (move_to_y - move_from_y) / (move_to_x - move_from_x)
                b = move_from_y - k * move_from_x
                d_step_x = (move_to_x - move_from_x) / d_step
                print(len_path)
                self.dx = d_step_x
                self.dy = k * self.x + b

            else:
                d_step_y = (move_to_y - move_from_y) / d_step
                self.dy = d_step_y


    def move_to(self):
        if len(self.path) <= 2:
            self.enemy_pos = (self.x, self.y)
        else:
            move_from_x = self.path[-1][0]
            move_from_y = self.path[-1][1]

            move_to_x = self.path[-2][0]
            move_to_y = self.path[-2][1]
            len_path = path_len((move_to_x - move_from_x), (move_to_y - move_from_y))
            d_step = len_path / 0.5
            if self.x != move_to_x:
                if move_to_x != move_from_x:
                    k = (move_to_y - move_from_y) / (move_to_x - move_from_x)
                    b = move_from_y - k * move_from_x
                    d_step_x = (move_to_x - move_from_x) / d_step
                    print(len_path)
                    self.dx = d_step_x
                    self.x += self.dx
                    self.y = k * self.x + b
                    if abs(move_to_x - self.x) < abs(d_step_x):
                        self.x = move_to_x
                        self.y = move_to_y
                        self.enemy_pos = (self.x, self.y)
                        self.path.pop()

                else:
                    d_step_y = (move_to_y - move_from_y) / d_step
                    self.dy = d_step_y
                    self.y += self.dy
                    if abs(move_to_y - self.y) < d_step_y:
                        self.x = move_to_x
                        print('ready')
                        self.y = move_to_y
                        self.path.pop(0)
            else:
                self.path.pop()
            self.next_step = self.path[-2]

            self.enemy_pos = (self.x, self.y)

    def health_bar(self):
        pg.draw.rect(self.surface, self.settings.red, (self.x-self.r-5, self.y-self.r-10, 30, 6))
        pg.draw.rect(self.surface, self.settings.green, (self.x-self.r-5, self.y-self.r-10, (self.health/self.max_health*30), 6))

    def hit(self):
        move_from_x = self.path[-1][0]
        move_from_y = self.path[-1][1]

        move_to_x = self.path[-2][0]
        move_to_y = self.path[-2][1]
        len_path = path_len((move_to_x - move_from_x), (move_to_y - move_from_y))
        d_step = len_path / 0.5
        if self.x != move_to_x:
            if move_to_x != move_from_x:
                k = (move_to_y - move_from_y) / (move_to_x - move_from_x)
                b = move_from_y - k * move_from_x
                d_step_x = (move_to_x - move_from_x) / d_step
                self.dx = d_step_x
                self.x += self.dx
                self.y = k * self.x + b

            else:
                d_step_y = (move_to_y - move_from_y) / d_step
                self.dy = d_step_y
                self.y += self.dy

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
        self.r_long_row = self.__around_long_row()
        self.r_short_row = self.__around_short_row()
        self.square_size_x = self.field_width / self.number_of_squares[0]  # in the short line
        self.square_size_y = self.field_height / self.number_of_squares[1]
        self.array = self.__field_array()
        self.path = []
        self.point_2 = None
        self.rage = False

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
        return array_i

    def levenstein(self, go_from, go_to, blocked, collide_p, next_step):
        """
        Make a path in grath from  start point to the end point
        :param collide_p:
        :param go_from: start point on grath
        :param go_to: end point on grath
        :param blocked: point not allow to use
        :return: path in form of list of vertexes (array indexes(i, j))
        """
        if not self.rage:
            graph = self.__graph_make(blocked, go_from, collide_p)
            parents = self.__path_from_graph(go_from, go_to, graph)
        if self.rage:
            blocked = []
            graph = self.__graph_make(blocked, go_from, collide_p)
            parents = self.__path_from_graph(go_from, go_to, graph)



        self.path = [go_to]

        parent = parents[go_to]

        while parent != go_from:
            self.path.append(parent)
            parent = parents[parent]
        self.path.append(go_from)
        if collide_p is not None:
            self.point_2 = next_step
            if self.point_2 in self.path and (path_len((go_from[0]-self.point_2[0]), (go_from[1]-self.point_2[1])) <
                                              path_len((collide_p[0] - self.point_2[0]), (collide_p[1] - self.point_2[1]))):
                self.path.remove(collide_p)
        return self.path

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

    def __graph_make(self, blocked, go_from, collide_point):
        """
        make a grath from array
        :param blocked: point not allow to use
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
                            if self.array[i + i_s - 1][j + j_s - 1] not in blocked:
                                grath[self.array[i - 1][j - 1]].add(self.array[i + i_s - 1][j + j_s - 1])
        self.grath = grath

        if collide_point is not None and collide_point != go_from:
            cat = collide_point
            if cat == go_from:
                print("CATCH YOU")
            self.grath[go_from] = {cat}
            self.grath[cat].add(go_from)

        return self.grath

    def __path_from_graph(self, go_from, go_to, graph):
        parents = {}
        distance = {go_from: 0}
        queue = deque([go_from])

        while queue:
            current_vertex = queue.popleft()
            for vertex in graph[current_vertex]:

                if vertex not in distance:
                    distance[vertex] = distance[current_vertex] + 1

                    parents.update({vertex: current_vertex})
                    queue.append(vertex)
        if go_to not in parents:
            self.rage = True
            return
        return parents


my_game = Game()

my_game.run()
