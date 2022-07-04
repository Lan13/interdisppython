import pygame
import sys
import random
from pygame.locals import *
from snake import Snake


class Snake2:
    def __init__(self):
        self.snake1 = Snake(200, 300, "DOWN")
        self.snake2 = Snake(600, 300, "DOWN")

    def draw_food(self, display):
        pygame.draw.rect(display, Color("blue"), Rect(self.snake1.food[0], self.snake1.food[1], 20, 20))
        pygame.draw.rect(display, Color("green"), Rect(self.snake2.food[0], self.snake2.food[1], 20, 20))

    def draw_snake(self, display):
        self.snake1.draw_snake(display)
        self.snake2.draw_snake(display)

    def eat_food(self, display):
        if self.snake1.head == self.snake1.food:  # 如果头部碰到食物，说明吃到了食物
            self.snake1.score = self.snake1.score + 1  # 得分加1，实际上得分就是已经吃的食物的个数
            print("Currently user1 score is {}".format(self.snake1.score))
            self.snake1.eaten = True  # 更新食物状态，并且删除食物的显示
            pygame.draw.rect(display, self.snake1.White, Rect(self.snake1.food[0], self.snake1.food[1], 20, 20))
        if self.snake2.head == self.snake2.food:  # 如果头部碰到食物，说明吃到了食物
            self.snake2.score = self.snake2.score + 1  # 得分加1，实际上得分就是已经吃的食物的个数
            print("Currently user2 score is {}".format(self.snake2.score))
            self.snake2.eaten = True  # 更新食物状态，并且删除食物的显示
            pygame.draw.rect(display, self.snake2.White, Rect(self.snake2.food[0], self.snake2.food[1], 20, 20))

    def game_over(self):
        if self.snake1.head in self.snake1.body or self.snake1.head in self.snake2.body:
            return True, "user1"  # 如果移动后的头部碰到蛇的身体，游戏结束
        elif self.snake1.head[0] < 0 or self.snake1.head[1] < 0:
            return True, "user1"  # 如果移动后的头部碰到上界和左界，游戏结束
        elif self.snake1.head[0] > 780 or self.snake1.head[1] > 580:
            return True, "user1"  # 如果移动后的头部碰到下界和右界，游戏结束

        if self.snake2.head in self.snake1.body or self.snake2.head in self.snake2.body:
            return True, "user2"  # 如果移动后的头部碰到蛇的身体，游戏结束
        elif self.snake2.head[0] < 0 or self.snake2.head[1] < 0:
            return True, "user2"  # 如果移动后的头部碰到上界和左界，游戏结束
        elif self.snake2.head[0] > 780 or self.snake2.head[1] > 580:
            return True, "user2"  # 如果移动后的头部碰到下界和右界，游戏结束
        return False, ""

    def generate_food(self):
        if self.snake1.eaten:  # 如果当前食物被吃了，则生成一个新的食物
            self.snake1.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
            # 食物的位置，确保不会在两只蛇的身体内
            while self.snake1.food in self.snake1.body or self.snake1.food in self.snake2.body:
                self.snake1.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
            self.snake1.eaten = False  # 更新食物状态
        if self.snake2.eaten:  # 如果当前食物被吃了，则生成一个新的食物
            self.snake2.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
            # 食物的位置，确保不会在两只蛇的身体内
            while self.snake2.food in self.snake1.body or self.snake2.food in self.snake2.body:
                self.snake2.food = [random.randint(1, 39) * 20, random.randint(1, 29) * 20]
            self.snake2.eaten = False  # 更新食物状态

    def move_two_snake(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # 修改了 free-python-game 中蛇反向移动的问题
                if event.key == K_w and self.snake1.direction != "DOWN":
                    self.snake1.direction = "UP"  # 只有在蛇不在向下移动时才能改变方向为向上
                elif event.key == K_s and self.snake1.direction != "UP":
                    self.snake1.direction = "DOWN"  # 只有在蛇不在向上移动时才能改变方向为向下
                elif event.key == K_a and self.snake1.direction != "RIGHT":
                    self.snake1.direction = "LEFT"  # 只有在蛇不在向右移动时才能改变方向为向左
                elif event.key == K_d and self.snake1.direction != "LEFT":
                    self.snake1.direction = "RIGHT"  # 只有在蛇不在向左移动时才能改变方向为向右
                elif event.key == K_UP and self.snake2.direction != "DOWN":
                    self.snake2.direction = "UP"  # 只有在蛇不在向下移动时才能改变方向为向上
                elif event.key == K_DOWN and self.snake2.direction != "UP":
                    self.snake2.direction = "DOWN"  # 只有在蛇不在向上移动时才能改变方向为向下
                elif event.key == K_LEFT and self.snake2.direction != "RIGHT":
                    self.snake2.direction = "LEFT"  # 只有在蛇不在向右移动时才能改变方向为向左
                elif event.key == K_RIGHT and self.snake2.direction != "LEFT":
                    self.snake2.direction = "RIGHT"  # 只有在蛇不在向左移动时才能改变方向为向右
        if self.snake1.direction == "UP":  # 向上移动头部
            self.snake1.head = [self.snake1.head[0], self.snake1.head[1] - 20]
        elif self.snake1.direction == "DOWN":  # 向下移动头部
            self.snake1.head = [self.snake1.head[0], self.snake1.head[1] + 20]
        elif self.snake1.direction == "LEFT":  # 向左移动头部
            self.snake1.head = [self.snake1.head[0] - 20, self.snake1.head[1]]
        else:  # 向右移动头部
            self.snake1.head = [self.snake1.head[0] + 20, self.snake1.head[1]]
        if self.snake2.direction == "UP":  # 向上移动头部
            self.snake2.head = [self.snake2.head[0], self.snake2.head[1] - 20]
        elif self.snake2.direction == "DOWN":  # 向下移动头部
            self.snake2.head = [self.snake2.head[0], self.snake2.head[1] + 20]
        elif self.snake2.direction == "LEFT":  # 向左移动头部
            self.snake2.head = [self.snake2.head[0] - 20, self.snake2.head[1]]
        else:  # 向右移动头部
            self.snake2.head = [self.snake2.head[0] + 20, self.snake2.head[1]]


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Greedy Snake by PB20111689")
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    snake = Snake2()
    while True:
        screen.fill(Color("white"))
        snake.draw_food(screen)
        snake.move_two_snake()
        pygame.display.flip()
        result, user = snake.game_over()
        if result:
            print("Greedy Snake Game Over!")
            if user == "user1":
                print("user2 win the game")
            else:
                print("user1 win the game")
            break
        snake.eat_food(screen)
        snake.draw_snake(screen)
        snake.generate_food()
        pygame.display.flip()
        clock.tick(10)  # 控制速率，感觉这个速率比较适中
