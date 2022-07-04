import pygame
import sys
import random
import copy
from pygame.locals import *


class Button:
    def __init__(self, display, position, filename, size):
        """图片按钮的初始化

        :param display:
        :param position: 按钮位置
        :param filename: 图片名
        :param size: 图片大小
        """
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, size)   # 将图片转化为指定大小
        self.position = position
        display.blit(self.image, self.position)     # 显示图片

    def click(self):
        """判断鼠标按下时是否点击该按钮

        :return: 是否点击该按钮
        """
        cursor_x, cursor_y = pygame.mouse.get_pos()     # 获取鼠标点击事件发生时的坐标
        x, y = self.position
        width, height = self.image.get_size()
        # 返回是否在按钮内，即判断出点击是否发生在按钮上
        return x <= cursor_x <= x + width and y <= cursor_y <= y + height


class Box:
    def __init__(self, left_top, text, color):
        """ 2048 格子的显示

        :param left_top: 格子左上角顶点
        :param text: 2048 格子数字
        :param color: 2048 数字对应的颜色
        """
        self.size = 100     # 每个数字的格子大小
        self.font = pygame.font.SysFont("arial", 36)
        self.left_top = left_top    # 每个数字格子左上角坐标
        self.text = text        # 显示的数字
        self.color = color      # 显示的颜色

    def draw_box(self, display):
        """ 画出 2048 格子

        :param display:
        :return:
        """
        x, y = self.left_top
        pygame.draw.rect(display, self.color, (x, y, self.size, self.size))
        number = self.font.render(self.text, True, (0, 0, 0))
        number_rect = number.get_rect()
        number_rect.center = (x + 50, y + 50)   # 在rect的中心画出数字
        display.blit(number, number_rect)       # 显示数字


class Board:
    def __init__(self, display):
        """ 2048 棋盘的初始化

        :param display:
        """
        self.font = pygame.font.SysFont("arial", 25)    # 字体设置
        self.board = [[0, 0, 0, 0] for _ in range(4)]   # 棋盘的初始化
        self.colors = {                                 # 每个数字对应的颜色
            0: (200, 195, 180),
            2: (240, 230, 220),
            4: (235, 225, 200),
            8: (240, 175, 120),
            16: (245, 150, 100),
            32: (245, 125, 95),
            64: (245, 95, 60),
            128: (240, 210, 115),
            256: (235, 205, 100),
            512: (240, 200, 80),
            1024: (240, 200, 60),
            2048: (225, 188, 0)
        }
        self.screen_left_gap = 50           # 棋盘到左边界的距离
        self.screen_top_gap = 100           # 棋盘到上边界的距离
        self.box_gap = 5                    # 每个棋格之间的距离
        self.score = 0                      # 当前得分
        self.new_game = Button(display, (self.screen_left_gap + 320,
                                         self.screen_left_gap // 2 + 5), "button.jpg", (100, 60))
        self.rand_board()
        self.rand_board()

    def clear_and_set(self):
        """ 清空棋盘并重新设置

        :return:
        """
        self.score = 0
        self.board = [[0, 0, 0, 0] for _ in range(4)]
        self.rand_board()
        self.rand_board()

    def combine(self, box_set):
        """ 判断并操作格子合并

        :param box_set: 需要判断是否可以合并的格子
        :return: 合并后的格子
        """
        result = [0, 0, 0, 0]   # 合并后的情况
        number = []     # 该行或列中不为 0 的数字
        for box in box_set:
            if box != 0:
                number.append(box)
        if len(number) == 4:    # 当待合并的数字中有四个数时
            if number[0] == number[1]:      # 如果第一个和第二个相等
                result[0] = number[0] + number[1]   # 合并第一个和第二个
                self.score = self.score + result[0]
                if number[2] == number[3]:  # 如果第三个和第四个还想等
                    result[1] = number[2] + number[3]   # 合并第三个和第四个
                    self.score = self.score + result[1]
                else:
                    result[1] = number[2]
                    result[2] = number[3]
            elif number[1] == number[2]:    # 如果第二个和第三个相等
                result[0] = number[0]
                result[1] = number[1] + number[2]       # 合并第二个和第三个
                self.score = self.score + result[1]
                result[2] = number[3]
            elif number[2] == number[3]:    # 如果第三个和第四个相等
                result[0] = number[0]
                result[1] = number[1]
                result[2] = number[2] + number[3]       # 合并第三个和第四个
                self.score = self.score + result[2]
            else:       # 如果不能合并，则依此复制
                for i in range(len(number)):
                    result[i] = number[i]
        elif len(number) == 3:      # 当待合并的数字中有三个数时
            if number[0] == number[1]:      # 如果第一个和第二个相等
                result[0] = number[0] + number[1]   # 合并第一个和第二个
                self.score = self.score + result[0]
                result[1] = number[2]
            elif number[1] == number[2]:    # 如果第二个和第三个相等
                result[0] = number[0]
                result[1] = number[1] + number[2]       # 合并第二个和第三个
                self.score = self.score + result[1]
            else:       # 如果不能合并，则依此复制
                for i in range(len(number)):
                    result[i] = number[i]
        elif len(number) == 2:      # 当待合并的数字中有两个数时
            if number[0] == number[1]:      # 如果两个数相等
                result[0] = number[0] + number[1]   # 合并
                self.score = self.score + result[0]
            else:       # 如果不能合并，则依此复制
                for i in range(len(number)):
                    result[i] = number[i]
        elif len(number) == 1:      # 当待合并的数字中只有一个数时
            result[0] = number[0]   # 直接复制
        return result   # 返回合并后的情况

    def draw_board(self, display):
        """ 画出 2048 整体界面

        :param display:
        :return:
        """
        x = self.screen_left_gap
        y = self.screen_top_gap
        size = 425
        pygame.draw.rect(display, (187, 173, 160), (x, y, size, size))
        x, y = x + self.box_gap, y + self.box_gap
        for i in range(4):
            for j in range(4):
                number = self.board[i][j]
                if number == 0:
                    text = ""
                else:
                    text = str(number)
                color = self.colors[number]
                box = Box((x, y), text, color)
                box.draw_box(display)
                x = x + self.box_gap + box.size
            x = self.screen_left_gap + self.box_gap
            y = y + self.screen_top_gap + self.box_gap
        pygame.draw.rect(display, (187, 173, 160),
                         (self.screen_left_gap + 220, self.screen_left_gap // 2 + 5, 80, 60))
        score = self.font.render(str(self.score), True, Color(255, 255, 255)).convert_alpha()
        score_rect = score.get_rect()
        score_rect.center = (self.screen_left_gap + 260, self.screen_left_gap // 2 + 50)
        display.blit(score, score_rect)
        self.show_info(display, " score:", 225)

    def game_over(self):
        """ 判断游戏是否结束

        :return:
        """
        # 如果已经出现了2048，那么游戏结束
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 2048:
                    return True
        # 如果还有位置未填满，则游戏并未结束
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return False
        # 如果所有位置都填满，且相邻格子之间没有相同数字，则游戏并未结束
        for i in range(4):
            for j in range(3):
                if self.board[i][j] == self.board[i][j + 1]:
                    return False
        for i in range(3):
            for j in range(4):
                if self.board[i][j] == self.board[i + 1][j]:
                    return False
        return True

    def move_down(self):
        """ 向下合并，同时判断是否发生合并

        :return: 是否发生合并
        """
        current_board = copy.deepcopy(self.board)
        for i in range(4):
            temp = []
            for j in range(4):
                temp.append(self.board[3 - j][i])   # 向下合并时，行顺序需要倒过来
            temp = self.combine(temp)
            for j in range(4):
                self.board[3 - j][i] = temp[j]      # 合并之后，需要逆序存回去
        return current_board != self.board

    def move_left(self):
        """ 向左合并，同时判断是否发生合并

        :return: 是否发生合并
        """
        current_board = copy.deepcopy(self.board)
        for i in range(4):
            temp = self.combine(self.board[i])      # 向左合并时，顺序正常
            for j in range(4):
                self.board[i][j] = temp[j]
        return current_board != self.board

    def move_right(self):
        """ 向右合并，同时判断是否发生合并

        :return: 是否发生合并
        """
        current_board = copy.deepcopy(self.board)
        for i in range(4):
            temp = self.combine(self.board[i][::-1])    # 向右合并时，列顺序需要倒过来
            for j in range(4):
                self.board[i][3 - j] = temp[j]          # 合并之后，需要逆序存回去
        return current_board != self.board

    def move_up(self):
        """ 向上合并，同时判断是否发生合并

        :return: 是否发生合并
        """
        current_board = copy.deepcopy(self.board)
        for i in range(4):
            temp = []
            for j in range(4):
                temp.append(self.board[j][i])       # 向下合并时，需要转置
            temp = self.combine(temp)
            for j in range(4):
                self.board[j][i] = temp[j]          # 合并之后，需要再转置存回去
        return current_board != self.board

    def play(self):
        """ 用户操作

        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                change = False
                if event.key == K_w or event.key == K_UP:
                    change = self.move_up()
                elif event.key == K_s or event.key == K_DOWN:
                    change = self.move_down()
                elif event.key == K_a or event.key == K_LEFT:
                    change = self.move_left()
                elif event.key == K_d or event.key == K_RIGHT:
                    change = self.move_right()
                if not self.game_over() and change:
                    self.rand_board()
                    if self.game_over():
                        print("Game Over and we will start a new game!\n")
                        print("Your final score is", board.score)
                        # board.clear_and_set()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    if board.new_game.click():  # 按下新的游戏按钮
                        board.clear_and_set()
                        board.draw_board(screen)

    def rand_board(self):
        """ 从空白的格子随机生成一个数字

        :return:
        """
        blank = []      # 首先获取所有空白格子的左边点
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    blank.append((i, j))
        choice = random.choice(blank)   # 随机从空白格子选取一个
        number = random.uniform(0, 1)   # 采用均匀分布，按概率生成随机数
        if number < 0.01:
            number = 8
        elif number < 0.1:
            number = 4
        else:
            number = 2
        self.board[choice[0]][choice[1]] = number

    def show_info(self, display, message, position):
        """ 显示文本信息

        :param display:
        :param message: 需要显示的信息
        :param position: 需要显示信息的位置
        :return:
        """
        text = self.font.render(message, True, Color(255, 255, 255))
        text = text.convert_alpha()
        display.blit(text, (self.screen_left_gap + position, self.screen_left_gap // 2 + 5))


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("2048 by PB20111689")
    screen_width, screen_height = 520, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    background = pygame.image.load("background.jpg").convert()
    screen.blit(background, (0, 0))
    board = Board(screen)
    board.draw_board(screen)
    pygame.display.flip()
    while True:
        board.play()
        board.draw_board(screen)
        pygame.display.flip()
