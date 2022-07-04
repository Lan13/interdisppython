import pygame
from pygame.locals import *
from sudoku import Sudoku
import socket
import sys
import time
import threading
from coop_sudoku import Coop_Sudoku
from config import *
import json
from protocol import package
import struct

mutex = threading.Lock()
find_flag = False
Opponent = None
win = False
lose = False
file_num = None
Matching = False
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def handle(body: bytes):
    global find_flag
    global file_num
    global win
    global lose
    msg = json.loads(body.decode(encoding='utf-8'))
    type = msg['type']
    if type == 'finish match':
        mutex.acquire()
        find_flag = True
        file_num = msg['file_num']
        mutex.release()
        return 1
    elif type == 'win' or type == 'oppo leave':
        mutex.acquire()
        win = True
        mutex.release()
        return 3
    elif type == 'lose':
        mutex.acquire()
        lose = True
        mutex.release()
        return 3
    return 0


def socket_recv(coop_mode=False):
    global find_flag
    global Opponent
    global win
    global lose
    global file_num
    data_buffer = bytes()
    while True:
        try:
            data = sock.recv(512)
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
                    status = handle(body)
                    if status == 3:
                        return
                    if coop_mode and status & 1 == 1:
                        return
                    data_buffer = data_buffer[HEADER_SIZE + body_size:]
        except:
            break


class Div:
    display = None
    font = None

    def __init__(self, display, font, name: str, x0: str, y0: str, x1: str, y1: str):
        self.display = display
        self.font = font
        self.x0 = int(x0)
        self.x1 = int(x1)
        self.y0 = int(y0)
        self.y1 = int(y1)
        self.name = name

    def draw(self):
        left = self.x0
        right = self.x1
        top = self.y0
        bottom = self.y1
        pygame.draw.line(self.display, Color("black"), (left, top), (right, top))
        pygame.draw.line(self.display, Color("black"), (right, top), (right, bottom))
        pygame.draw.line(self.display, Color("black"), (right, bottom), (left, bottom))
        pygame.draw.line(self.display, Color("black"), (left, bottom), (left, top))
        text = self.font.render(str(self.name), True, Color("0x63c666"))
        self.display.blit(text, (left, top))


class Button(Div):
    def __init__(self, display, font, name: str, x0: str, y0: str, x1: str, y1: str):
        super().__init__(display, font, name, x0, y0, x1, y1)

    def is_click(self, pos_x, pos_y):
        if self.x0 <= pos_x <= self.x1 and self.y0 <= pos_y <= self.y1:
            return True
        else:
            return False

    def handle(self):
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.name == '单人模式':
            sudoku = Sudoku(self.display)
            while True:
                sudoku.play()
                sudoku.draw_background(self.display)
                sudoku.draw_choose(self.display)
                sudoku.output(self.display)
                if sudoku.win():
                    break
                sudoku.music.draw_buttons()
                current_time = sudoku.music.get_music_time()
                sudoku.music.draw_song_name()
                sudoku.music.draw_music_progress(current_time)
                sudoku.music.draw_volume_progress(sudoku.music.volume)
                sudoku.music.new_song(current_time)
                pygame.display.flip()
        elif self.name == '双人对战':
            global find_flag
            global win
            global lose
            msg = MsgBox(self.display, self.font, '正在匹配', '150', '0', '400', '40')
            try:
                sock.connect((host, port))
            except:
                cnt = 0
                while cnt < 100:
                    client_end.play()
                    client_end.draw()
                    msg.show_msg('连接服务器失败')
                    pygame.display.flip()
                    cnt = cnt + 1
                    time.sleep(0.01)
                return
            socket_th = threading.Thread(target=socket_recv)
            socket_th.setDaemon(True)
            socket_th.start()
            try:
                send_dict = {'type': 'match battle'}
                sock.send(package(send_dict))
                # sock.send('match battle'.encode('utf-8'))
            except:
                print('fail to send')
            t = 0
            while True:
                if not find_flag:
                    client_end.play()
                    client_end.draw()
                    msg.show_msg('正在匹配:{}s'.format(t))
                    pygame.display.flip()
                    t = t + 1
                    time.sleep(1)
                else:
                    break
            sudoku = Sudoku(self.display, file_num)
            send_once = 0
            while True:
                sudoku.play()
                sudoku.draw_background(self.display)
                sudoku.draw_choose(self.display)
                sudoku.output(self.display)
                if win:
                    self.display.fill(Color("0xF0CCFF"))
                    Sudoku.grain(self.display)
                    msg.show_msg('胜利')
                    pygame.display.flip()
                    mutex.acquire()
                    win = False
                    mutex.release()
                    time.sleep(1)
                    break
                elif lose:
                    self.display.fill(Color("0xF0CCFF"))
                    Sudoku.grain(self.display)
                    msg.show_msg('失败')
                    pygame.display.flip()
                    mutex.acquire()
                    lose = False
                    mutex.release()
                    time.sleep(1)
                    break
                if sudoku.win() and send_once != 1:
                    send_dict = {'type': 'battle finish'}
                    sock.send(package(send_dict))
                    send_once = 1
                sudoku.music.draw_buttons()
                current_time = sudoku.music.get_music_time()
                sudoku.music.draw_song_name()
                sudoku.music.draw_music_progress(current_time)
                sudoku.music.draw_volume_progress(sudoku.music.volume)
                sudoku.music.new_song(current_time)
                pygame.display.flip()
            mutex.acquire()
            find_flag = False
            mutex.release()
            sock.close()
        elif self.name == '合作模式':
            msg = MsgBox(self.display, self.font, '正在匹配', '150', '0', '400', '40')
            try:
                sock.connect((host, port))
            except:
                cnt = 0
                while cnt < 100:
                    client_end.play()
                    client_end.draw()
                    msg.show_msg('连接服务器失败')
                    pygame.display.flip()
                    cnt = cnt + 1
                    time.sleep(0.01)
                return
            socket_th = threading.Thread(target=socket_recv, args=(True,))
            socket_th.setDaemon(True)
            socket_th.start()
            try:
                send_dict = {'type': 'match cooperate'}
                sock.send(package(send_dict))
            except:
                print('fail to send')
            t = 0
            while True:
                if not find_flag:
                    client_end.play()
                    client_end.draw()
                    msg.show_msg('正在匹配:{}s'.format(t))
                    pygame.display.flip()
                    t = t + 1
                    time.sleep(1)
                else:
                    break
            socket_th.join()
            co_sudo = Coop_Sudoku(self.display, file_num, sock)
            ret_status = co_sudo.run()
            if ret_status == COOPERATE_WIN:
                msg = MsgBox(self.display, self.font, 'WIN', '150', '0', '400', '40')
                self.display.fill(Color("0xF0CCFF"))
                Sudoku.grain(self.display)
                msg.show_msg('胜利')
                pygame.display.flip()
                time.sleep(1)
            elif ret_status == OPPO_LEAVE:
                msg = MsgBox(self.display, self.font, 'LEAVE', '150', '0', '400', '40')
                self.display.fill(Color("0xF0CCFF"))
                Sudoku.grain(self.display)
                msg.show_msg('对手离开')
                pygame.display.flip()
                time.sleep(1)
            mutex.acquire()
            find_flag = False
            mutex.release()
            sock.close()


class MsgBox(Div):
    def __init__(self, display, font, name, x0, y0, x1, y1):
        super().__init__(display, font, name, x0, y0, x1, y1)

    def show_msg(self, msg):
        self.name = msg
        self.draw()

    def clear_msg(self):
        self.name = ''
        self.draw()


class Client:
    def __init__(self, display):
        self.buttons = []
        self.display = display
        self.font = pygame.font.SysFont("SimHei", 36)
        with open('config.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                name, x0, y0, x1, y1 = line.split(' ')
                self.buttons.append(Button(self.display, self.font, name, x0, y0, x1, y1))

    def play(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.is_click(event.pos[0], event.pos[1]):
                        button.handle()

    def draw(self):
        self.display.fill(Color("0xF0CCFF"))
        for button in self.buttons:
            button.draw()
        Sudoku.grain(self.display)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Sudoku by PB20111689")
    screen = pygame.display.set_mode((480, 640))
    clock = pygame.time.Clock()
    client_end = Client(screen)
    while True:
        client_end.play()
        client_end.draw()
        pygame.display.flip()
