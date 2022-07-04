import socket
import queue
import random
import threading
import os
import sys
import json
from config import *
from protocol import package
import struct
import copy

cooperate_waiting_queue = queue.Queue(maxsize=20)
battle_waiting_queue = queue.Queue(maxsize=20)
socket_send_queue = queue.Queue()
g_users = []
mutex = threading.Lock()


class User:
    def __init__(self, id, addr, sock: socket.socket):
        self.id = id
        self.addr = addr
        self.sock = sock
        self.status = None
        self.other = None
        self.alive = True
        self.game = None
        self.u1_or_u2 = None

    def change_status(self, status):
        self.status = status

    def get_into_game(self, game, u1_or_u2):
        self.game = game
        self.u1_or_u2 = u1_or_u2

    def operation(self, type: str, args: str):
        args_list = args.split(',')
        if type == 'choose':
            if self.u1_or_u2 == 1:
                self.game.u1_choose[0] = int(args_list[0])
                self.game.u1_choose[1] = int(args_list[1])
            elif self.u1_or_u2 == 2:
                self.game.u2_choose[0] = int(args_list[0])
                self.game.u2_choose[1] = int(args_list[1])
        elif type == 'set':
            self.game.mutex.acquire()
            self.game.sudoku[int(args_list[0])][int(args_list[1])] = int(args_list[2])
            self.game.mutex.release()
        send_dict = {'type': 'update', 'sudoku': self.game.sudoku}
        if self.u1_or_u2 == 1:
            send_dict['self choose'] = self.game.u1_choose
            send_dict['oppo choose'] = self.game.u2_choose
        elif self.u1_or_u2 == 2:
            send_dict['self choose'] = self.game.u2_choose
            send_dict['oppo choose'] = self.game.u1_choose
        if DEBUG:
            print(self.game.u1_choose)
        try:
            self.sock.send(package(send_dict))
            tmp = send_dict['self choose']
            send_dict['self choose'] = send_dict['oppo choose']
            send_dict['oppo choose'] = tmp
            self.other.sock.send(package(send_dict))
        except:
            pass

    def leave(self):
        self.sock.close()
        g_users.remove(self)
        self.alive = False
        if self.status == 'gaming':
            send_dict = {'type': 'oppo leave'}
            send_bytes = package(send_dict)
            try:
                self.other.sock.send(send_bytes)
            except:
                pass


class Game:
    def __init__(self, file_num, u1: User, u2: User):
        self.file_num = file_num
        self.sudoku = []
        for i in range(0, 10):
            self.sudoku.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.mutex = threading.Lock()
        self.user1 = u1
        self.user2 = u2
        self.u1_choose = [1, 1]
        self.u2_choose = [1, 1]
        self.load_sudoku()
        self.origin_sudoku = copy.deepcopy(self.sudoku)

    def load_sudoku(self):
        path_root = os.path.split(sys.argv[0])[0]  # 当前的父目录
        if path_root == "":
            path_root = os.getcwd()
        filename = path_root + "/sudoku/sudoku" + str(self.file_num) + ".txt"
        with open(filename, "r") as file:
            for i, line in enumerate(file.read().splitlines()):
                content = line.split(" ")
                content.insert(0, "0")
                num = list(map(int, content))  # 将读到的 str 类型转化为 int 类型
                self.sudoku[i + 1] = num


class Server:
    def __init__(self):
        self.index = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(10)

    def accept_client(self):
        while True:
            conn, addr = self.sock.accept()
            user = User(self.index, addr, conn)
            self.index += 1
            g_users.append(user)
            client_th = threading.Thread(target=Server.message_recv, args=(self, user))
            client_th.setDaemon(True)
            client_th.start()

    def message_handle(self, u: User, body: bytes):
        msg = json.loads(body.decode(encoding='utf-8'))
        if DEBUG:
            print(msg)
        if msg['type'] == 'match battle':
            oppo = None
            mutex.acquire()  # 这里要加锁  类似test_and_set
            if battle_waiting_queue.qsize() > 0:
                oppo = battle_waiting_queue.get()
                mutex.release()
                flag, _ = self.match(u, oppo)
                if flag == 1:  # user alive oppo not alive
                    u.change_status('waiting battle')
                    battle_waiting_queue.put(u)
                if flag == 2:  # user not alive oppo alive
                    oppo.change_status('waiting battle')
                    battle_waiting_queue.put(u)
            else:
                mutex.release()
                u.change_status('waiting battle')
                battle_waiting_queue.put(u)
            print('user ' + str(u.id) + ' join matching')
        elif msg['type'] == 'battle finish':
            if u.status != 'lose':
                u.change_status('win')
                u.other.change_status('lose')
                win_dict = {'type': 'win'}
                lose_dict = {'type': 'lose'}
                u.sock.send(package(win_dict))
                u.other.sock.send(package(lose_dict))
        elif msg['type'] == 'match cooperate':
            oppo = None
            mutex.acquire()  # 这里要加锁  类似test_and_set
            if cooperate_waiting_queue.qsize() > 0:
                oppo = cooperate_waiting_queue.get()
                mutex.release()
                flag, file_num = self.match(u, oppo)
                if flag == 1:  # user alive oppo not alive
                    u.change_status('waiting cooperate')
                    cooperate_waiting_queue.put(u)
                if flag == 2:  # user not alive oppo alive
                    oppo.change_status('waiting cooperate')
                    cooperate_waiting_queue.put(u)
                new_game = Game(file_num, u, u.other)
                u.get_into_game(new_game, 1)
                u.other.get_into_game(new_game, 2)
            else:
                mutex.release()
                u.change_status('waiting cooperate')
                cooperate_waiting_queue.put(u)
            print('user ' + str(u.id) + ' join matching')
        elif msg['type'] == 'choose' or msg['type'] == 'set':
            type = msg['type']
            args = msg['args']
            u.operation(type, args)
        elif msg['type'] == 'clear':
            u.game.sudoku = copy.deepcopy(u.game.origin_sudoku)
            send_dict = {'type': 'clear'}
            u.sock.send(package(send_dict))
            u.other.sock.send(package(send_dict))
        elif msg['type'] == 'cooperate finish':
            send_dict = {'type': 'win'}
            u.sock.send(package(send_dict))
            u.other.sock.send(package(send_dict))

    def message_recv(self, u: User):
        data_buffer = bytes()
        while True:
            try:
                recv_bytes = u.sock.recv(512)
            except ConnectionResetError:
                print('user {} left'.format(u.id))
                u.leave()
                break
            except:
                print('other problem')
                break
            if recv_bytes == b"":
                print('user {} left'.format(u.id))
                u.leave()
                break
            if recv_bytes:
                data_buffer += recv_bytes
                while True:
                    if len(data_buffer) < HEADER_SIZE:
                        break
                    header = struct.unpack('1I', data_buffer[:HEADER_SIZE])
                    body_size = header[0]
                    if DEBUG:
                        print(body_size)
                    if len(data_buffer) < HEADER_SIZE + body_size:
                        break
                    body = data_buffer[HEADER_SIZE:HEADER_SIZE + body_size]
                    self.message_handle(u, body)
                    data_buffer = data_buffer[HEADER_SIZE + body_size:]

    def match(self, user1: User, user2: User):
        user1.other = user2
        user2.other = user1
        user1.change_status('gaming')
        user2.change_status('gaming')
        file_num = random.randint(1, 4)
        flag = 0
        alive_package = package({'type': 'isalive?'})
        try:
            user1.sock.send(alive_package)
            flag += 1
        except:
            pass
        try:
            user2.sock.send(alive_package)
            flag += 2
        except:
            pass
        if flag == 3:
            send2u1_dict = {'type': 'finish match', 'oppo': user2.id, 'file_num': file_num}
            send2u2_dict = {'type': 'finish match', 'oppo': user1.id, 'file_num': file_num}
            try:
                user1.sock.send(package(send2u1_dict))
                user2.sock.send(package(send2u2_dict))
                print('user {} and user {} match'.format(user1.id, user2.id))
            except:
                pass
        return flag, file_num

    def run(self):
        accept_th = threading.Thread(target=Server.accept_client, args=(self,))
        accept_th.setDaemon(True)
        accept_th.start()
        while True:
            cmd = input("-----------------\n输入check:查看当前在线人数\n输入quit(q):关闭服务端\n")
            if cmd == 'check':
                print('当前在线人数{}人'.format(len(g_users)))
            elif cmd == 'quit' or cmd == 'q':
                exit()


if __name__ == '__main__':
    server_end = Server()
    server_end.run()
