import pygame
import os
import sys
from pygame.locals import *
from mutagen.mp3 import MP3
import random


class Music:
    def __init__(self, display):
        self.display = display
        self.font = pygame.font.SysFont("SimHei", 18)
        self.PATH_ROOT = os.path.split(sys.argv[0])[0]
        if self.PATH_ROOT == "":
            self.PATH_ROOT = os.getcwd()
        self.PAUSE_IMG_PATH = "/".join([self.PATH_ROOT, "img/pause.png"])
        self.PLAY_IMG_PATH = "/".join([self.PATH_ROOT, "img/play.png"])
        self.NEXT_IMG_PATH = "/".join([self.PATH_ROOT, "img/next.png"])
        self.PREV_IMG_PATH = "/".join([self.PATH_ROOT, "img/prev.png"])
        self.LOOP_ALL_IMG_PATH = "/".join([self.PATH_ROOT, "img/loop_all.png"])
        self.LOOP_OFF_IMG_PATH = "/".join([self.PATH_ROOT, "img/loop_off.png"])
        self.LOOP_ONE_IMG_PATH = "/".join([self.PATH_ROOT, "img/loop_one.png"])
        self.MUSIC_PATH = "/".join([self.PATH_ROOT, "music"])

        self.music_count = 0  # img 文件夹内总歌曲的数量
        self.music_list = self.get_all_music()
        self.random_list = [i for i in range(0, self.music_count)]  # 随机播放的序列
        self.random_index = 0  # 随机播放音乐的索引，通过这个来确认当前播放音乐的索引
        self.current_index = 0  # 当前播放音乐的索引
        self.music_offset = 0  # 音乐播放的进度条位置
        self.play_music(self.current_index)
        self.volume = 0.5  # 音乐的播放声音
        pygame.mixer.music.set_volume(self.volume)  # 设置音量
        self.playing = True  # 当前是否正在播放
        self.loop_mode = 0  # 0 -> loop_all 顺序循环; 1 -> loop_off 随机循环; 2 -> loop_one 单曲循环

        self.button_size = 60  # 设置播放按键的大小
        self.pause_img = pygame.image.load(self.PAUSE_IMG_PATH).convert_alpha()
        self.play_img = pygame.image.load(self.PLAY_IMG_PATH).convert_alpha()
        self.next_img = pygame.image.load(self.NEXT_IMG_PATH).convert_alpha()
        self.prev_img = pygame.image.load(self.PREV_IMG_PATH).convert_alpha()
        self.loop_all_img = pygame.image.load(self.LOOP_ALL_IMG_PATH).convert_alpha()
        self.loop_off_img = pygame.image.load(self.LOOP_OFF_IMG_PATH).convert_alpha()
        self.loop_one_img = pygame.image.load(self.LOOP_ONE_IMG_PATH).convert_alpha()
        self.pause_img = pygame.transform.scale(self.pause_img, (self.button_size, self.button_size))
        self.play_img = pygame.transform.scale(self.play_img, (self.button_size, self.button_size))
        self.next_img = pygame.transform.scale(self.next_img, (self.button_size, self.button_size))
        self.prev_img = pygame.transform.scale(self.prev_img, (self.button_size, self.button_size))
        self.loop_all_img = pygame.transform.scale(self.loop_all_img, (self.button_size, self.button_size))
        self.loop_off_img = pygame.transform.scale(self.loop_off_img, (self.button_size, self.button_size))
        self.loop_one_img = pygame.transform.scale(self.loop_one_img, (self.button_size, self.button_size))

    def check_playing(self):
        """判断当前音乐是否正在播放

        :return: 是否正在播放
        """
        return self.playing

    def draw_buttons(self):
        """绘制上一首歌曲、播放与暂停、下一首歌曲、歌曲播放模式的按钮

        :return:
        """
        self.display.blit(self.prev_img, (150, 490))
        if self.playing:
            self.display.blit(self.pause_img, (150 + self.button_size, 490))
        else:
            self.display.blit(self.play_img, (150 + self.button_size, 490))
        self.display.blit(self.next_img, (150 + self.button_size * 2, 490))
        if self.loop_mode == 0:
            self.display.blit(self.loop_all_img, (150 + self.button_size * 3, 490))
        elif self.loop_mode == 1:
            self.display.blit(self.loop_off_img, (150 + self.button_size * 3, 490))
        else:
            self.display.blit(self.loop_one_img, (150 + self.button_size * 3, 490))

    def draw_music_progress(self, val=0):
        """绘制当前播放音乐的进度条

        :param val: 当前音乐已播放的百分比
        :return:
        """
        rect_progress_all = pygame.Rect(20, 570, 200, 20)
        rect_progress_music = pygame.Rect(20, 570, int(200 * val), 20)
        pygame.draw.rect(self.display, Color("grey"), rect_progress_all)
        pygame.draw.rect(self.display, Color("pink"), rect_progress_music)

    def draw_song_name(self):
        """显示当前播放音乐的名称

        :return:
        """
        name = self.font.render(self.music_list[self.current_index][0].split(".mp3")[0], True, Color("0x63c666"))
        self.display.blit(name, (20, 550))

    def draw_volume_progress(self, val):
        """绘制当前播放音量的音量条

        :param val: 当前音乐的音量百分比
        :return:
        """
        rect_progress_all = pygame.Rect(260, 570, 200, 20)
        rect_progress_volume = pygame.Rect(260, 570, int(200 * val), 20)
        pygame.draw.rect(self.display, Color("grey"), rect_progress_all)
        pygame.draw.rect(self.display, Color("pink"), rect_progress_volume)

    def get_all_music(self):
        """从 img 文件夹内读取所有音乐的名称以及时长

        :return: 音乐的列表
        """
        music_list = []
        for root, dirs, files in os.walk(self.MUSIC_PATH):
            for file in files:
                name, ext_name = os.path.splitext(file)
                if ext_name == ".mp3":
                    self.music_count = self.music_count + 1
                    audio = MP3(self.MUSIC_PATH + "/" + file)
                    music_list.append((file, audio.info.length))
                    # print(audio.info.length)
        return music_list

    def get_button_size(self):
        """返回按钮大小

        :return: 按钮大小
        """
        return self.button_size

    def get_volume(self):
        """返回播放音乐的音量

        :return: 播放音量
        """
        return self.volume

    def get_music_total_time(self):
        """获取当前播放音乐的总时长

        :return: 音乐的总时长
        """
        return self.music_list[self.current_index][1]

    def get_music_time(self):
        """获取当前音乐播放的进度时间百分比

        :return: 当前音乐播放的进度时间百分比
        """
        music_time = self.music_list[self.current_index][1]
        current_time = ((pygame.mixer.music.get_pos() // 1000) / music_time) + self.music_offset
        return current_time

    def new_song(self, current_time):
        """当一首歌播放完成时，播放新的音乐

        :return:
        """
        if current_time < self.music_offset:  # 播放完毕
            self.music_offset = 0
            if self.loop_mode == 0:
                self.current_index = (self.current_index + 1) % self.music_count
            elif self.loop_mode == 1:
                self.random_index = (self.random_index + 1) % self.music_count
                self.current_index = self.random_list[self.random_index]
            elif self.loop_mode == 2:
                self.current_index = self.current_index
            self.play_music(self.current_index)

    def next_music(self):
        """播放下一首歌曲，如果是随机模式，则随机播放

        :return:
        """
        if self.loop_mode == 0 or self.loop_mode == 2:
            self.current_index = (self.current_index + 1) % self.music_count
        else:
            self.random_index = (self.random_index + 1) % self.music_count
            self.current_index = self.random_list[self.random_index]
        self.play_music(self.current_index)
        self.set_playing_or_pause(True)

    def play_music(self, index):
        """播放 index 索引对应的音乐

        :param index: 播放音乐的索引
        :return:
        """
        pygame.mixer.music.load(self.MUSIC_PATH + "/" + self.music_list[index][0])
        pygame.mixer.music.play()

    def prev_music(self):
        """播放上一首歌曲，如果是随机模式，则随机播放

        :return:
        """
        if self.loop_mode == 0 or self.loop_mode == 2:
            self.current_index = (self.current_index - 1) % self.music_count
        else:
            self.random_index = (self.random_index - 1) % self.music_count
            self.current_index = self.random_list[self.random_index]
        self.play_music(self.current_index)
        self.set_playing_or_pause(True)

    def set_loop_mode(self):
        """设置音乐播放的模式，0 为顺序播放，1 为随机播放，2 为单曲循环

        :return:
        """
        self.loop_mode = (self.loop_mode + 1) % 3
        if self.loop_mode == 1:
            random.shuffle(self.random_list)

    def set_music_offset(self, val):
        """修改当前音乐进度条的偏移量

        :param val: 预期修改的值
        :return:
        """
        self.music_offset = val

    def set_playing_or_pause(self, val):
        """设置当前音乐播放状态为播放或暂停

        :param val: 设置状态，True 为播放，False 为暂停
        :return:
        """
        self.playing = val

    def set_volume(self, val):
        """修改当前的播放音量

        :param val: 预期修改的值
        :return:
        """
        self.volume = val
