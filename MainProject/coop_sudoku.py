from sudoku import Sudoku
import socket
import pygame
from pygame.locals import *
import sys
from queue import Queue
import threading
import json
from protocol import package
from config import *
import struct


class Coop_Sudoku(Sudoku):
    def __init__(self, display, file_num=None, sock: socket.socket = None):
        super().__init__(display, file_num)
        self.display = display
        self.sock = sock
        self.oppo_choose = [1, 1]
        self.send_queue = Queue(maxsize=30)
        self.recv_queue = Queue(maxsize=30)
        self.win_flag = False
        self.lose_flag = False
        self.oppo_leave_flag = False

    def play(self):         # 重写合作模式下的同步操作
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    # event.pos[1] is vertical and event.pos[0] is horizon
                    # 鼠标点击确认输入框
                    if 120 <= event.pos[1] <= 480 and 60 <= event.pos[0] <= 420:
                        i, j = int((event.pos[1] - 120) / 40) + 1, int((event.pos[0] - 60) / 40) + 1
                        send_dict = {'type': 'choose', 'args': '{},{},0'.format(i, j)}
                        self.send_queue.put(package(send_dict))
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
                        send_dict = {'type': 'clear', 'args': '0,0,0'}
                        self.send_queue.put(package(send_dict))
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
                i = self.choose[0]
                j = self.choose[1]
                if event.key == K_w or event.key == K_UP:
                    if self.choose[0] != 1:
                        i = self.choose[0] - 1
                elif event.key == K_s or event.key == K_DOWN:
                    if self.choose[0] != 9:
                        i = self.choose[0] + 1
                elif event.key == K_a or event.key == K_LEFT:
                    if self.choose[1] != 1:
                        j = self.choose[1] - 1
                elif event.key == K_d or event.key == K_RIGHT:
                    if self.choose[1] != 9:
                        j = self.choose[1] + 1
                # 用户输入数字
                elif event.key in [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0]:
                    num = int(chr(event.key))
                    if self.check_number(num, self.choose[0], self.choose[1]):
                        send_dict = {'type': 'set', 'args': '{},{},{}'.format(self.choose[0], self.choose[1], num)}
                        self.send_queue.put(package(send_dict))
                # 用户输入 BACKSPACE
                elif event.key == K_BACKSPACE:
                    if self.check_number(0, self.choose[0], self.choose[1]):
                        send_dict = {'type': 'set', 'args': '{},{},{}'.format(self.choose[0], self.choose[1], 0)}
                        self.send_queue.put(package(send_dict))
                if i != self.choose[0] or j != self.choose[1]:
                    send_dict = {'type': 'choose', 'args': '{},{},0'.format(i, j)}
                    self.send_queue.put(package(send_dict))

    def send(self):
        while True:
            if self.send_queue.qsize() > 0:
                data = self.send_queue.get()
                self.sock.send(data)

    def handle(self, body: bytes):
        msg = json.loads(body.decode(encoding='utf-8'))
        type = msg['type']
        if type == 'win':
            self.win_flag = True
            return 1
        elif type == 'oppo leave':
            self.oppo_leave_flag = True
            return 1
        elif type == 'lose':
            self.lose_flag = True
            return 1
        elif type == 'update':
            self.choose = msg['self choose']
            self.oppo_choose = msg['oppo choose']
            if DEBUG:
                print(self.choose)
                print(self.oppo_choose)
            self.sudoku = msg['sudoku']
        elif type == 'clear':
            self.clear()
        return 0

    def recv(self):
        data_buffer = bytes()
        while True:
            data = self.sock.recv(512)
            if data:
                data_buffer += data
                while True:
                    if HEADER_SIZE > len(data_buffer):
                        break
                    header = struct.unpack('1I', data_buffer[:HEADER_SIZE])
                    body_size = header[0]
                    if HEADER_SIZE + body_size > len(data_buffer):
                        break
                    body = data_buffer[HEADER_SIZE:HEADER_SIZE + body_size]
                    status = self.handle(body)
                    if status == 1:
                        return
                    data_buffer = data_buffer[HEADER_SIZE + body_size:]

    def draw_oppo_choose(self):
        x, y = 60, 120
        left_up = (x + (self.oppo_choose[1] - 1) * 40, y + (self.oppo_choose[0] - 1) * 40)
        right_up = (x + self.oppo_choose[1] * 40, y + (self.oppo_choose[0] - 1) * 40)
        left_down = (x + (self.oppo_choose[1] - 1) * 40, y + self.oppo_choose[0] * 40)
        right_down = (x + self.oppo_choose[1] * 40, y + self.oppo_choose[0] * 40)
        pygame.draw.line(self.display, Color("black"), left_up, right_up)
        pygame.draw.line(self.display, Color("black"), right_up, right_down)
        pygame.draw.line(self.display, Color("black"), right_down, left_down)
        pygame.draw.line(self.display, Color("black"), left_down, left_up)

    def draw(self):
        screen = self.display
        self.draw_background(screen)
        self.draw_choose(screen)
        self.draw_oppo_choose()
        self.output(screen)
        self.music.draw_buttons()

        current_time = self.music.get_music_time()
        self.music.draw_song_name()
        self.music.draw_music_progress(current_time)
        self.music.draw_volume_progress(self.music.volume)
        self.music.new_song(current_time)
        pygame.display.flip()

    def run(self):
        sending_th = threading.Thread(target=Coop_Sudoku.send, args=(self,))
        sending_th.setDaemon(True)
        # sending_th.daemon=True  # for python3.10
        sending_th.start()
        recv_th = threading.Thread(target=Coop_Sudoku.recv, args=(self,))
        recv_th.setDaemon(True)
        recv_th.start()
        while True:
            self.play()
            self.draw()
            if self.win():
                send_dict = {'type': 'cooperate finish'}
                self.send_queue.put(package(send_dict))
            if self.win_flag:
                return COOPERATE_WIN
            if self.oppo_leave_flag:
                return OPPO_LEAVE
