import pygame
import sys
import random
from pygame.locals import *


class Snake(object):
    def __init__(self, x, y, direction):
        self.Red = Color("red")  # 红色 用来表示蛇头部的颜色
        self.Black = Color("black")  # 黑色 用来表示蛇身体的颜色
        self.White = Color("white")  # 白色 背景颜色
        self.Blue = Color("blue")  # 蓝色 用来表示食物的颜色
        self.body = [[x, y]]        # 蛇的整个身体的所有坐标点
        self.head = [x, y]          # 蛇的头部坐标点
        self.direction = direction  # 蛇当前移动的方向
        self.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
        while self.food in self.body:   # 食物的位置，确保不会在蛇的身体内，修改了 free-python-game 中食物出现的位置
            self.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
        self.eaten = False          # 食物是否被吃掉
        self.score = 0              # 当前得分

    def draw_food(self, display):
        pygame.draw.rect(display, self.Blue, Rect(self.food[0], self.food[1], 20, 20))

    def draw_snake(self, display):
        self.body.insert(0, self.head)      # 把蛇移动后的头部加入到蛇的身体
        if not self.eaten:                  # 如果食物没有被吃掉的话
            self.body.pop()                 # 则身体最后一个点要被删除（即移动了）
        head = True                         # 只是用来标记输出头部的变量
        for segment in self.body:           # 对蛇身体每一部分进行绘图
            if head:
                pygame.draw.rect(display, self.Red, Rect(segment[0], segment[1], 20, 20))
                head = False
            else:
                pygame.draw.rect(display, self.Black, Rect(segment[0], segment[1], 20, 20))

    def eat_food(self, display):
        if self.head == self.food:      # 如果头部碰到食物，说明吃到了食物
            self.score = self.score + 1     # 得分加1，实际上得分就是已经吃的食物的个数
            print("Currently your score is {}".format(self.score))
            self.eaten = True           # 更新食物状态，并且删除食物的显示
            pygame.draw.rect(display, self.White, Rect(self.food[0], self.food[1], 20, 20))

    def game_over(self):
        if self.head in self.body:
            return True     # 如果移动后的头部碰到蛇的身体，游戏结束
        elif self.head[0] < 0 or self.head[1] < 0:
            return True     # 如果移动后的头部碰到上界和左界，游戏结束
        elif self.head[0] > 780 or self.head[1] > 580:
            return True     # 如果移动后的头部碰到下界和右界，游戏结束
        return False

    def generate_food(self):
        if self.eaten:      # 如果当前食物被吃了，则生成一个新的食物
            self.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
            while self.food in self.body:   # 食物的位置，确保不会在蛇的身体内
                self.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
            self.eaten = False      # 更新食物状态

    def snake_move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # 修改了 free-python-game 中蛇反向移动的问题
                if (event.key == K_w or event.key == K_UP) and self.direction != "DOWN":
                    self.direction = "UP"       # 只有在蛇不在向下移动时才能改变方向为向上
                elif (event.key == K_s or event.key == K_DOWN) and self.direction != "UP":
                    self.direction = "DOWN"     # 只有在蛇不在向上移动时才能改变方向为向下
                elif (event.key == K_a or event.key == K_LEFT) and self.direction != "RIGHT":
                    self.direction = "LEFT"     # 只有在蛇不在向右移动时才能改变方向为向左
                elif (event.key == K_d or event.key == K_RIGHT) and self.direction != "LEFT":
                    self.direction = "RIGHT"    # 只有在蛇不在向左移动时才能改变方向为向右
        if self.direction == "UP":          # 向上移动头部
            self.head = [self.head[0], self.head[1] - 20]
        elif self.direction == "DOWN":      # 向下移动头部
            self.head = [self.head[0], self.head[1] + 20]
        elif self.direction == "LEFT":      # 向左移动头部
            self.head = [self.head[0] - 20, self.head[1]]
        else:                               # 向右移动头部
            self.head = [self.head[0] + 20, self.head[1]]


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Greedy Snake by PB20111689")
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    snake = Snake(400, 300, "DOWN")
    while True:
        screen.fill(snake.White)
        snake.draw_food(screen)
        snake.snake_move()
        if snake.game_over():
            print("Greedy Snake Game Over!")
            break
        snake.eat_food(screen)
        snake.draw_snake(screen)
        snake.generate_food()
        pygame.display.flip()
        clock.tick(8)   # 控制速率，感觉这个速率比较适中
    # print("Greedy Snake Game Over!")
