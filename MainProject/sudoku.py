import pygame
import sys
import random
import copy
from pygame.locals import *
from music import Music
import os


class Sudoku:
    def __init__(self, display, file_num=None):
        self.music = Music(display)
        self.flag = [False for _ in range(0, 325)]  # 记录格、行、列、宫的数字情况
        self.init_flag = [False for _ in range(0, 82)]  # 初始生成的记录
        self.sudoku = []  # 记录玩家的数独记录
        for i in range(0, 10):
            self.sudoku.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.dfs_flag = [False for _ in range(0, 325)]
        self.dfs_sudoku = []  # dfs搜索保存的数独记录
        for i in range(0, 10):
            self.dfs_sudoku.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.dfs_answer = []  # 数独的解记录
        for i in range(0, 10):
            self.dfs_answer.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.show_answer = False  # 当前是否为显示解答
        self.dfs_done_flag = False  # 记录是否搜索过解答，可以减少多次搜索带来的时间损耗
        self.font = pygame.font.SysFont("SimHei", 36)
        self.choose = [1, 1]  # 用户当前选择填入数字的位置
        self.rand_sudoku(file_num)

    def check_number(self, num, i, j):
        """判断用户输入的 num 数字是否可以填入到 sudoku[i][j] 的位置。如果可以，便填入并更新 flag 记录；
        如果填入的是 0，则清除当前用户填的数字，并且重置 flag 记录

        :param num: 用户输入的 num 数字
        :param i: 数独的列
        :param j: 数独的行
        :return: 判断结果
        """
        current = (i - 1) * 9 + j
        # 初始位置不可以填入
        if self.init_flag[current]:
            return False
        row = (i - 1) * 9 + num + 81
        col = (j - 1) * 9 + num + 162
        house = (int((i - 1) / 3) * 3 + int((j - 1) / 3)) * 9 + num + 243
        # 清零操作
        if num == 0:
            row = (i - 1) * 9 + self.sudoku[i][j] + 81
            col = (j - 1) * 9 + self.sudoku[i][j] + 162
            house = (int((i - 1) / 3) * 3 + int((j - 1) / 3)) * 9 + self.sudoku[i][j] + 243
            self.flag[current] = self.flag[row] = self.flag[col] = self.flag[house] = False
            return True
        if 1 <= num <= 9:
            if self.flag[current] or self.flag[row] or self.flag[col] or self.flag[house]:
                return False
        self.flag[current] = self.flag[row] = self.flag[col] = self.flag[house] = True
        return True

    def clear(self):
        """清除当前已经填过的数字

        :return:
        """
        self.flag = [False for _ in range(0, 325)]
        for i in range(1, 10):
            for j in range(1, 10):
                current = (i - 1) * 9 + j
                if not self.init_flag[current]:
                    self.sudoku[i][j] = 0
        self.set_flag()

    def dfs(self, x, y):
        """进行 dfs 搜索对数独进行求解，当搜索到解答时将会保存 dfs_answer

        :param x: 数独的列
        :param y: 数独的行
        :return:
        """
        # 当前位置不是 0 时，则不需要搜索
        if self.dfs_sudoku[x][y] != 0:
            if x == 9 and y == 9:
                self.show_answer = True
                self.dfs_answer = copy.deepcopy(self.dfs_sudoku)
                return
            if y == 9:  # 从下一行开始搜索
                self.dfs(x + 1, 1)
            else:  # 从下一列开始搜索
                self.dfs(x, y + 1)
        else:
            for dfs_num in range(1, 10):
                current = (x - 1) * 9 + y
                row = (x - 1) * 9 + dfs_num + 81
                col = (y - 1) * 9 + dfs_num + 162
                house = (int((x - 1) / 3) * 3 + int((y - 1) / 3)) * 9 + dfs_num + 243
                if not self.dfs_flag[row] and not self.dfs_flag[col] \
                        and not self.dfs_flag[house] and not self.init_flag[current]:
                    self.dfs_sudoku[x][y] = dfs_num
                    self.dfs_flag[current] = self.dfs_flag[row] = True
                    self.dfs_flag[col] = self.dfs_flag[house] = True
                    if x == 9 and y == 9:
                        self.show_answer = True
                        self.dfs_answer = copy.deepcopy(self.dfs_sudoku)
                        self.dfs_sudoku[x][y] = 0
                        self.dfs_flag[current] = self.dfs_flag[row] = False
                        self.dfs_flag[col] = self.dfs_flag[house] = False
                        return
                    if y == 9:  # 从下一行开始搜索
                        self.dfs(x + 1, 1)
                    else:  # 从下一列开始搜索
                        self.dfs(x, y + 1)
                    # 回溯
                    self.dfs_sudoku[x][y] = 0
                    self.dfs_flag[current] = self.dfs_flag[row] = False
                    self.dfs_flag[col] = self.dfs_flag[house] = False

    def draw_background(self, display):
        """绘制数独的背景界面，包括九宫格以及装饰纹路

        :param display:
        :return:
        """
        display.fill(Color("0xF0CCFF"))  # 0xFFB6C1
        x, y = 60, 120
        for i in range(0, 10):
            pygame.draw.line(display, Color("white"), (x, y + i * 40), (420, y + i * 40))
            pygame.draw.line(display, Color("white"), (x + i * 40, y), (x + i * 40, 480))
        for i in range(0, 4):
            pygame.draw.line(display, Color("0xFF5555"), (x, y + i * 120), (420, y + i * 120))
            pygame.draw.line(display, Color("0xFF5555"), (x + i * 120, y), (x + i * 120, 480))
        self.grain(display)
        if not self.show_answer:
            self.draw_button(display, 400, 10, 470, 45, "答案")
        else:
            self.draw_button(display, 400, 10, 470, 45, "返回")
        self.draw_button(display, 300, 10, 370, 45, "清空")

    def draw_button(self, display, left, top, right, bottom, name):
        """绘制按钮

        :param display:
        :param left: 按钮的左坐标
        :param top: 按钮的上坐标
        :param right: 按钮的右坐标
        :param bottom: 按钮的下坐标
        :param name: 按钮的名称
        :return:
        """
        pygame.draw.line(display, Color("black"), (left, top), (right, top))
        pygame.draw.line(display, Color("black"), (right, top), (right, bottom))
        pygame.draw.line(display, Color("black"), (right, bottom), (left, bottom))
        pygame.draw.line(display, Color("black"), (left, bottom), (left, top))
        text = self.font.render(str(name), True, Color("0x63c666"))
        display.blit(text, (left, top))

    def draw_choose(self, display):
        """绘制用户选择填入数字位置的颜色，其选中颜色为黑色

        :param display:
        :return:
        """
        x, y = 60, 120
        left_up = (x + (self.choose[1] - 1) * 40, y + (self.choose[0] - 1) * 40)
        right_up = (x + self.choose[1] * 40, y + (self.choose[0] - 1) * 40)
        left_down = (x + (self.choose[1] - 1) * 40, y + self.choose[0] * 40)
        right_down = (x + self.choose[1] * 40, y + self.choose[0] * 40)
        pygame.draw.line(display, Color("black"), left_up, right_up)
        pygame.draw.line(display, Color("black"), right_up, right_down)
        pygame.draw.line(display, Color("black"), right_down, left_down)
        pygame.draw.line(display, Color("black"), left_down, left_up)

    @staticmethod
    def grain(display):
        """绘制纹路

        :param display:
        :return:
        """
        pygame.draw.line(display, Color("0xB82727"), (61, 486), (0, 547))
        pygame.draw.line(display, Color("0xB82727"), (94, 486), (0, 580))
        pygame.draw.line(display, Color("0xB82727"), (140, 486), (7, 619))
        pygame.draw.line(display, Color("0xB82727"), (158, 486), (15, 629))
        pygame.draw.line(display, Color("0xB82727"), (170, 491), (24, 638))
        pygame.draw.line(display, Color("0xB82727"), (170, 491), (212, 491))
        pygame.draw.line(display, Color("0xB82727"), (212, 491), (280, 560))
        pygame.draw.line(display, Color("0xB82727"), (280, 560), (400, 560))
        pygame.draw.line(display, Color("0xB82727"), (400, 560), (480, 480))
        pygame.draw.line(display, Color("0xB82727"), (228, 486), (271, 530))
        pygame.draw.line(display, Color("0xB82727"), (271, 530), (352, 530))
        pygame.draw.line(display, Color("0xB82727"), (352, 530), (396, 486))
        pygame.draw.line(display, Color("0xB82727"), (40, 640), (105, 575))
        pygame.draw.line(display, Color("0xB82727"), (105, 575), (114, 575))
        pygame.draw.line(display, Color("0xB82727"), (114, 575), (168, 520))
        pygame.draw.line(display, Color("0xB82727"), (168, 520), (220, 520))
        pygame.draw.line(display, Color("0xB82727"), (220, 520), (300, 600))
        pygame.draw.line(display, Color("0xB82727"), (300, 600), (360, 600))
        pygame.draw.circle(display, Color("white"), (360, 600), 4)
        pygame.draw.line(display, Color("0xB82727"), (60, 640), (110, 590))
        pygame.draw.line(display, Color("0xB82727"), (110, 590), (119, 590))
        pygame.draw.line(display, Color("0xB82727"), (119, 590), (177, 530))
        pygame.draw.line(display, Color("0xB82727"), (177, 530), (211, 530))
        pygame.draw.line(display, Color("0xB82727"), (211, 530), (290, 608))
        pygame.draw.line(display, Color("0xB82727"), (290, 608), (290, 632))
        pygame.draw.circle(display, Color("white"), (290, 632), 4)
        pygame.draw.circle(display, Color("white"), (137, 593), 3)
        pygame.draw.line(display, Color("0xB82727"), (139, 591), (179, 551))
        pygame.draw.line(display, Color("0xB82727"), (179, 551), (213, 551))
        pygame.draw.line(display, Color("0xB82727"), (213, 551), (242, 582))
        pygame.draw.line(display, Color("0xB82727"), (242, 582), (242, 605))
        pygame.draw.circle(display, Color("white"), (242, 605), 4)
        pygame.draw.circle(display, Color("white"), (159, 592), 3)
        pygame.draw.line(display, Color("0xB82727"), (161, 589), (171, 579))
        pygame.draw.line(display, Color("0xB82727"), (171, 579), (213, 579))
        pygame.draw.line(display, Color("0xB82727"), (213, 579), (220, 585))
        pygame.draw.line(display, Color("0xB82727"), (220, 585), (220, 592))
        pygame.draw.circle(display, Color("white"), (220, 595), 3)
        pygame.draw.circle(display, Color("white"), (110, 600), 3)
        pygame.draw.line(display, Color("0xB82727"), (113, 604), (128, 619))
        pygame.draw.line(display, Color("0xB82727"), (128, 619), (260, 619))
        pygame.draw.line(display, Color("0xB82727"), (260, 619), (280, 639))
        pygame.draw.line(display, Color("0xB82727"), (280, 639), (339, 639))
        pygame.draw.line(display, Color("0xB82727"), (339, 639), (379, 600))
        pygame.draw.line(display, Color("0xB82727"), (379, 600), (379, 576))
        pygame.draw.circle(display, Color("white"), (379, 573), 3)
        pygame.draw.circle(display, Color("white"), (77, 637), 3)
        pygame.draw.line(display, Color("0xB82727"), (80, 633), (95, 619))
        pygame.draw.line(display, Color("0xB82727"), (95, 619), (117, 619))
        pygame.draw.line(display, Color("0xB82727"), (117, 619), (125, 626))
        pygame.draw.line(display, Color("0xB82727"), (125, 626), (210, 626))
        pygame.draw.line(display, Color("0xBB2727"), (210, 626), (222, 640))
        pygame.draw.line(display, Color("0xB82727"), (88, 640), (93, 634))
        pygame.draw.line(display, Color("0xBB2727"), (93, 634), (199, 634))
        pygame.draw.line(display, Color("0xBB2727"), (199, 634), (202, 640))
        pygame.draw.line(display, Color("0xBB2727"), (358, 639), (397, 599))
        pygame.draw.line(display, Color("0xBB2727"), (397, 599), (438, 599))
        pygame.draw.line(display, Color("0xBB2727"), (438, 599), (470, 568))
        pygame.draw.circle(display, Color("white"), (472, 565), 3)
        pygame.draw.line(display, Color("0xBB2727"), (379, 639), (398, 619))
        pygame.draw.line(display, Color("0xBB2727"), (398, 619), (420, 619))
        pygame.draw.circle(display, Color("white"), (423, 619), 3)
        pygame.draw.circle(display, Color("white"), (426, 568), 3)
        pygame.draw.line(display, Color("0xBB2727"), (429, 565), (480, 516))
        pygame.draw.line(display, Color("0xBB2727"), (458, 638), (467, 630))
        pygame.draw.line(display, Color("0xBB2727"), (467, 630), (480, 630))
        pygame.draw.line(display, Color("0xBB2727"), (0, 184), (26, 210))
        pygame.draw.line(display, Color("0xBB2727"), (26, 210), (26, 369))
        pygame.draw.line(display, Color("0xBB2727"), (26, 369), (0, 393))
        pygame.draw.line(display, Color("0xBB2727"), (0, 205), (7, 211))
        pygame.draw.line(display, Color("0xBB2727"), (7, 211), (7, 270))
        pygame.draw.circle(display, Color("white"), (7, 273), 3)
        pygame.draw.line(display, Color("0xBB2727"), (0, 463), (5, 457))
        pygame.draw.line(display, Color("0xBB2727"), (5, 457), (5, 430))
        pygame.draw.line(display, Color("0xBB2727"), (5, 430), (51, 383))
        pygame.draw.line(display, Color("0xBB2727"), (51, 174), (40, 163))
        pygame.draw.line(display, Color("0xBB2727"), (40, 163), (40, 16))
        pygame.draw.circle(display, Color("white"), (40, 13), 3)
        pygame.draw.line(display, Color("0xBB2727"), (52, 0), (69, 18))
        pygame.draw.line(display, Color("0xBB2727"), (69, 18), (69, 52))
        pygame.draw.circle(display, Color("white"), (69, 55), 3)
        pygame.draw.line(display, Color("0xBB2727"), (257, 0), (144, 111))
        pygame.draw.line(display, Color("0xBB2727"), (144, 111), (144, 120))
        pygame.draw.line(display, Color("0xBB2727"), (310, 0), (190, 120))
        pygame.draw.line(display, Color("0xBB2727"), (238, 120), (263, 94))
        pygame.draw.line(display, Color("0xBB2727"), (263, 94), (329, 94))
        pygame.draw.line(display, Color("0xBB2727"), (329, 94), (424, 0))
        pygame.draw.line(display, Color("0xBB2727"), (423, 461), (423, 421))
        pygame.draw.line(display, Color("0xBB2727"), (423, 421), (445, 397))
        pygame.draw.circle(display, Color("white"), (451, 392), 3)
        pygame.draw.line(display, Color("0xBB2727"), (420, 358), (480, 358))
        pygame.draw.line(display, Color("0xBB2727"), (420, 136), (480, 74))
        pygame.draw.line(display, Color("0xBB2727"), (420, 186), (443, 186))
        pygame.draw.line(display, Color("0xBB2727"), (443, 186), (480, 147))
        pygame.draw.line(display, Color("0xBB2727"), (420, 207), (450, 206))
        pygame.draw.line(display, Color("0xBB2727"), (450, 206), (480, 179))
        pygame.draw.line(display, Color("0xBB2727"), (420, 254), (480, 254))
        pygame.draw.line(display, Color("0xBB2727"), (420, 261), (480, 261))

        pygame.draw.line(display, Color("0xBB2727"), (70, 120), (70, 107), 4)
        pygame.draw.line(display, Color("0xBB2727"), (70, 107), (138, 40), 4)
        pygame.draw.line(display, Color("0xBB2727"), (138, 40), (138, 0), 4)
        pygame.draw.line(display, Color("0xBB2727"), (133, 120), (133, 95), 4)
        pygame.draw.line(display, Color("0xBB2727"), (212, 120), (331, 0), 4)
        pygame.draw.line(display, Color("0xBB2727"), (420, 168), (429, 168), 4)
        pygame.draw.line(display, Color("0xBB2727"), (429, 168), (480, 117), 4)
        pygame.draw.line(display, Color("0xBB2727"), (420, 227), (462, 227), 4)
        pygame.draw.line(display, Color("0xBB2727"), (462, 227), (480, 208), 4)
        pygame.draw.line(display, Color("0xBB2727"), (0, 145), (45, 190), 4)
        pygame.draw.line(display, Color("0xBB2727"), (45, 190), (45, 368), 4)
        pygame.draw.line(display, Color("0xBB2727"), (45, 368), (0, 412), 4)
        pygame.draw.line(display, Color("0xBB2727"), (133, 95), (227, 0), 4)
        pygame.draw.line(display, Color("0xBB2727"), (344, 120), (460, 0), 4)
        pygame.draw.line(display, Color("0xBB2727"), (119, 486), (0, 605), 4)
        pygame.draw.line(display, Color("0xBB2727"), (420, 268), (480, 268), 4)
        pygame.draw.line(display, Color("0xBB2727"), (48, 471), (0, 520), 4)
        pygame.draw.circle(display, Color("white"), (464, 612), 3)
        pygame.draw.line(display, Color("0xBB2727"), (467, 609), (480, 597), 4)

    def output(self, display):
        """将数独显示在界面上

        :param display:
        :return:
        """
        for i in range(1, 10):
            for j in range(1, 10):
                text, color = self.select_color(i, j)
                num = self.font.render(str(text), True, color)
                x = 60 + (j - 1) * 40 + 12
                y = 120 + (i - 1) * 40 + 2
                display.blit(num, (x, y))

    def play(self):
        """处理用户对界面进行键盘鼠标事件操控，完成相应功能

        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    # event.pos[1] is vertical and event.pos[0] is horizon
                    # 鼠标点击确认输入框
                    if 120 <= event.pos[1] <= 480 and 60 <= event.pos[0] <= 420:
                        i, j = int((event.pos[1] - 120) / 40) + 1, int((event.pos[0] - 60) / 40) + 1
                        self.choose = [i, j]
                    # 选择显示答案
                    elif 400 <= event.pos[0] <= 470 and 10 <= event.pos[1] <= 45:
                        if not self.show_answer:
                            if not self.dfs_done_flag:
                                self.dfs(1, 1)
                                self.dfs_done_flag = True
                            else:
                                self.show_answer = True
                        else:
                            self.show_answer = False
                    elif 300 <= event.pos[0] <= 370 and 10 <= event.pos[1] <= 45:
                        self.clear()
                    # 选择播放上一首音乐
                    elif 150 <= event.pos[0] <= (150 + self.music.get_button_size()) and \
                            490 <= event.pos[1] <= (490 + self.music.get_button_size()):
                        self.music.set_music_offset(0)
                        self.music.prev_music()
                    # 选择暂停当前音乐的播放
                    elif (150 + self.music.get_button_size()) <= event.pos[0] <= (150 + 2 * self.music.button_size) and \
                            490 <= event.pos[1] <= (490 + self.music.get_button_size()):
                        if self.music.check_playing():
                            self.music.set_playing_or_pause(False)
                            pygame.mixer.music.pause()
                        else:
                            self.music.set_playing_or_pause(True)
                            pygame.mixer.music.unpause()
                    # 选择播放下一首音乐
                    elif (150 + 2 * self.music.get_button_size()) <= event.pos[0] <= (
                            150 + 3 * self.music.button_size) and \
                            490 <= event.pos[1] <= (490 + self.music.get_button_size()):
                        self.music.set_music_offset(0)
                        self.music.next_music()
                    # 选择音乐播放的模式
                    elif (150 + 3 * self.music.get_button_size()) <= event.pos[0] <= (
                            150 + 4 * self.music.button_size) and \
                            490 <= event.pos[1] <= (490 + self.music.get_button_size()):
                        self.music.set_loop_mode()
                    # 拖动播放音乐的进度条
                    elif 20 <= event.pos[0] <= 220 and 570 <= event.pos[1] <= 590:
                        music_pos = ((event.pos[0] - 20) / 200) * self.music.get_music_total_time()
                        pygame.mixer.music.play(0, music_pos)
                        self.music.set_music_offset((event.pos[0] - 20) / 200)
                    # 拖动播放声音的进度条
                    elif 260 <= event.pos[0] <= 460 and 570 <= event.pos[1] <= 590:
                        volume_pos = (event.pos[0] - 260) / 200
                        self.music.set_volume(volume_pos)
                        pygame.mixer.music.set_volume(volume_pos)
                elif event.button == 4:  # 滚轮向上，提高声音
                    if self.music.get_volume() <= 0.95:
                        self.music.set_volume(self.music.get_volume() + 0.05)
                    else:
                        self.music.set_volume(1)
                    pygame.mixer.music.set_volume(self.music.get_volume())
                elif event.button == 5:  # 滚轮向下，降低声音
                    if self.music.get_volume() >= 0.05:
                        self.music.set_volume(self.music.get_volume() - 0.05)
                    else:
                        self.music.set_volume(0)
                    pygame.mixer.music.set_volume(self.music.get_volume())
            elif event.type == pygame.KEYDOWN:
                # 对输入框进行上下左右移动
                if event.key == K_w or event.key == K_UP:
                    if self.choose[0] != 1:
                        self.choose[0] = self.choose[0] - 1
                elif event.key == K_s or event.key == K_DOWN:
                    if self.choose[0] != 9:
                        self.choose[0] = self.choose[0] + 1
                elif event.key == K_a or event.key == K_LEFT:
                    if self.choose[1] != 1:
                        self.choose[1] = self.choose[1] - 1
                elif event.key == K_d or event.key == K_RIGHT:
                    if self.choose[1] != 9:
                        self.choose[1] = self.choose[1] + 1
                # 用户输入数字
                elif event.key in [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0]:
                    num = int(chr(event.key))
                    if self.check_number(num, self.choose[0], self.choose[1]):
                        self.sudoku[self.choose[0]][self.choose[1]] = num
                # # 用户输入<-
                elif event.key == K_BACKSPACE:
                    if self.check_number(0, self.choose[0], self.choose[1]):
                        self.sudoku[self.choose[0]][self.choose[1]] = 0

    def rand_sudoku(self, file_number=None):
        """随机地选择一个文件生成初始数独

        :param file_number: 若不填或为None则随机选取，否则选取对应编号文件
        :return:
        """
        path_root = os.path.split(sys.argv[0])[0]  # 当前的父目录
        if path_root == "":
            path_root = os.getcwd()
        if file_number is None:
            file_number = random.randint(1, 4)
        filename = path_root + "/sudoku/sudoku" + str(file_number) + ".txt"
        # print(filename)
        with open(filename, "r") as file:
            for i, line in enumerate(file.read().splitlines()):
                content = line.split(" ")
                content.insert(0, "0")
                num = list(map(int, content))  # 将读到的 str 类型转化为 int 类型
                self.sudoku[i + 1] = num
                self.dfs_sudoku[i + 1] = copy.deepcopy(num)
            self.set_flag()

    def select_color(self, i, j):
        """根据给出的 i 和 j 选择得到sudoku[i][j]和对应数字的颜色

        :param i: 数独的列
        :param j: 数独的行
        :return: sudoku[i][j] 和对应的颜色
        """
        current = (i - 1) * 9 + j
        # 选择显示答案还是用户数独
        if not self.show_answer:
            num = self.sudoku[i][j]
        else:
            num = self.dfs_answer[i][j]
        # 将初始化的数独和用户填入的数独的颜色区分开
        if num == 0:
            if not self.init_flag[current]:
                return "", Color("0xFFFFFF")
            else:
                return "", Color("0xFFFFFF")
        elif num == 1:
            if not self.init_flag[current]:
                return "1", Color("0xEFFFFE")
            else:
                return "1", Color("0xE1111E")
        elif num == 2:
            if not self.init_flag[current]:
                return "2", Color("0xDFFFFD")
            else:
                return "2", Color("0xD1111D")
        elif num == 3:
            if not self.init_flag[current]:
                return "3", Color("0xCFFFFC")
            else:
                return "3", Color("0xC1111C")
        elif num == 4:
            if not self.init_flag[current]:
                return "4", Color("0xBFFFFB")
            else:
                return "4", Color("0xB1111B")
        elif num == 5:
            if not self.init_flag[current]:
                return "5", Color("0xAFFFFA")
            else:
                return "5", Color("0xA1111A")
        elif num == 6:
            if not self.init_flag[current]:
                return "6", Color("0x9FFFF9")
            else:
                return "6", Color("0x911119")
        elif num == 7:
            if not self.init_flag[current]:
                return "7", Color("0x8FFFF8")
            else:
                return "7", Color("0x811118")
        elif num == 8:
            if not self.init_flag[current]:
                return "8", Color("0x7FFFF7")
            else:
                return "8", Color("0x711117")
        else:
            if not self.init_flag[current]:
                return "9", Color("0x6FFFF6")
            else:
                return "9", Color("0x611116")

    def set_flag(self):
        """为填入的数字设置 flag 记录，即设置数字重复的信息

        :return:
        """
        for i in range(1, 10):
            for j in range(1, 10):
                if self.sudoku[i][j] != 0:
                    current = (i - 1) * 9 + j  # 当前位置，对应 flag 的 1 到 81
                    # 行位置，对应 flag 的 82 到 162
                    row = (i - 1) * 9 + self.sudoku[i][j] + 81
                    # 列位置，对应 flag 的 163 到 243
                    col = (j - 1) * 9 + self.sudoku[i][j] + 162
                    # 九宫格位置，对应 flag 的 244 到 324
                    house = (int((i - 1) / 3) * 3 + int((j - 1) / 3)) * 9 + self.sudoku[i][j] + 243
                    self.flag[current] = self.flag[row] = self.flag[col] = self.flag[house] = True
                    self.dfs_flag[current] = self.dfs_flag[row] = True
                    self.dfs_flag[col] = self.dfs_flag[house] = True
                    self.init_flag[current] = True

    def win(self):
        """判断游戏是否结束

        :return: 判断结果
        """
        for i in range(1, 82):
            if not self.flag[i]:
                return False
        print("Win")
        return True
