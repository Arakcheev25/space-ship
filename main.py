import pygame as py
from math import *
from pygame.locals import *
import random
import sys
import os


# Функция для получения путей к ресурсам
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


py.init()
clock = py.time.Clock()

# Параметры экрана
FPS = 40
width = 1000
height = 750

# Загрузка изображений
name_game = 'Space Ship'
name_icon = resource_path("images/gaming.png")
name_background = resource_path("images/background.png")
name_ship = resource_path("images/ship.png")
name_earth = resource_path("images/earth.png")
name_bullet = resource_path('images/bullet.png')
images_sprite_enemy_left_1 = resource_path('images/left_1.png')
images_sprite_enemy_left_3 = resource_path('images/left_3.png')
images_sprite_enemy_right_1 = resource_path('images/right_1.png')
images_sprite_enemy_right_3 = resource_path('images/right_3.png')

# Настройка экрана
screen = py.display.set_mode((width, height))
background = py.transform.scale(py.image.load(name_background), (width, height))
py.display.set_caption(name_game)
icon = py.image.load(name_icon)
py.display.set_icon(icon)

# Загрузка шрифтов
font = py.font.Font(None, 35)
font_win = py.font.Font(None, 75)
font_wonder = py.font.Font(None, 45)
font_record = py.font.Font(None, 20)

# Загрузка музыки
py.mixer.init()
background_sound = py.mixer.Sound(resource_path("sound/sound_back.mp3"))
game_over_sound = py.mixer.Sound(resource_path("sound/Game_over.mp3"))
attack_ship_sound = py.mixer.Sound(resource_path("sound/attack_blaster.mp3"))
game_over_sound.set_volume(0.3)
background_sound.set_volume(0.4)
attack_ship_sound.set_volume(0.03)

background_sound.play(loops=-1)
score = 0
lose = 0
record = 0
by_Arakcheev = font_record.render('by_Arakcheev', True, (3, 135, 113))


# class для любых объектов на экране
class Sprite(py.sprite.Sprite):
    def __init__(self, file_name, player_x, player_y, size_x, size_y, speed=5):
        py.sprite.Sprite.__init__(self)

        self.original_image = py.transform.scale(py.image.load(file_name), (size_x, size_y))  # оригинал объекта
        self.image = self.original_image  # текущее изображение объекта

        self.speed = speed
        self.size_x = size_x
        self.size_y = size_y

        self.rect = self.image.get_rect()  # объект теперь прямоугольник
        self.rect.x = player_x
        self.rect.y = player_y
        self.angle = 0

    # обновление экрана
    def reset(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


# главный персонаж - корабль
class Player(Sprite):
    # движение объекта
    def update(self):
        keys = py.key.get_pressed()

        # Поворот корабля
        if keys[K_LEFT]:
            self.angle = (self.angle + 5) % 360  # Поворот влево
        elif keys[K_RIGHT]:
            self.angle = (self.angle - 5) % 360  # Поворот вправо

            # Движение вперед (в сторону носа)
        if keys[K_w]:
            angle_radians = radians(self.angle)
            delta_x = self.speed * cos(angle_radians)
            delta_y = self.speed * sin(angle_radians)

            new_x = self.rect.x + delta_x
            new_y = self.rect.y - delta_y

            # Проверка границ по X
            if new_x < 10:
                new_x = 10  # Ограничиваем по левой границе
            elif new_x > width - self.size_x:
                new_x = width - self.size_x  # Ограничиваем по правой границе

            # Проверка границ по Y
            if new_y < 10:
                new_y = 10  # Ограничиваем по верхней границе
            elif new_y > height - self.size_y:
                new_y = height - self.size_y  # Ограничиваем по нижней границе

            # Обновляем координаты
            self.rect.x = new_x
            self.rect.y = new_y

        self.image = py.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def fire(self):
        # Расчёт координат носа ракеты
        angle_radians = radians(self.angle)
        nose_x = self.rect.centerx + (self.size_y / 2) * cos(angle_radians)
        nose_y = self.rect.centery - (self.size_y / 2) * sin(angle_radians)

        # Создание пули в точке носа
        bullet = Bullet(name_bullet, nose_x, nose_y, 35, 20, self.angle)
        bullets.add(bullet)


class Bullet(Sprite):
    def __init__(self, file_name, x, y, size_x, size_y, angle):
        super().__init__(file_name, x, y, size_x, size_y, speed=20)
        self.angle = angle

    def update(self):
        # Расчёт движения пули в направлении угла
        angle_radians = radians(self.angle)
        self.rect.x += self.speed * cos(angle_radians)
        self.rect.y -= self.speed * sin(angle_radians)

        # Удаление пули при выходе за границы экрана
        if self.rect.x < 0 or self.rect.x > width or self.rect.y < 0 or self.rect.y > height:
            self.kill()


class Enemy(Sprite):
    total_destroyed = 0

    def __init__(self, file_name, player_x, player_y, size_x, size_y, speed=1):
        super().__init__(file_name, player_x, player_y, size_x, size_y, speed)
        self.speed += (Enemy.total_destroyed // 3) / 12

    def update(self):
        # Расчёт направления к центру
        dx = width // 2 - self.rect.centerx
        dy = height // 2 - self.rect.centery
        distance = sqrt(dx ** 2 + dy ** 2)

        if distance > 0:  # Чтобы избежать деления на ноль
            direction_x = dx / distance
            direction_y = dy / distance

            # Обновление позиции
            # Обновление позиции
            self.rect.x += direction_x * min(self.speed, distance)
            self.rect.y += direction_y * min(self.speed, distance)


class Earth(Sprite):
    def __init__(self, file_name, x, y, size_x, size_y):
        super().__init__(file_name, x, y, size_x, size_y, speed=0)
        self.radius = min(size_x, size_y) // 2 + 35


sprite_enemy_right = py.sprite.Group()
sprite_enemy_left = py.sprite.Group()
bullets = py.sprite.Group()
ship = Player(name_ship, 400, 400, 100, 90, 8)
earth = Earth(name_earth, 430, 280, 175, 150)

enemy_left = [images_sprite_enemy_left_1, images_sprite_enemy_left_3, ]
enemy_right = [images_sprite_enemy_right_1, images_sprite_enemy_right_3]

for enem in range(3):
    enemy = Enemy(enemy_right[random.randint(0, 1)],
                  width,
                  random.randint(0, height),
                  100, 100,
                  1)
    sprite_enemy_right.add(enemy)

for enem in range(3):
    enemy = Enemy(enemy_left[random.randint(0, 1)],
                  -100,
                  random.randint(0, height),
                  100, 100, 1)
    sprite_enemy_left.add(enemy)

game_over = True
run = True
for enemy in sprite_enemy_right:
    py.draw.rect(screen, (255, 0, 0), enemy.rect, 2)  # Красный прямоугольник для врагов

py.draw.rect(screen, (0, 255, 0), ship.rect, 2)
while run:
    if score > record:
        record = score

    keys = py.key.get_pressed()
    screen.blit(background, (0, 0))

    if game_over:
        sprite_enemy_right.update()
        sprite_enemy_left.update()

        earth.reset()

        bullets.update()
        ship.update()

        # столкновение спрайтов справа и земли
        for enemy in sprite_enemy_right:
            distance = sqrt(
                (earth.rect.centerx - enemy.rect.centerx) ** 2 + (earth.rect.centery - enemy.rect.centery) ** 2)
            if distance < earth.radius:
                lose += 1
                enemy.kill()
                new_enemy = Enemy(enemy_right[random.randint(0, 1)], random.randint(width, 1100),
                                  random.randint(0, height),
                                  100, 100, 1)
                sprite_enemy_right.add(enemy)

        # Проверка столкновений земли и врагов слева
        for enemy in sprite_enemy_left:
            distance = sqrt(
                (earth.rect.centerx - enemy.rect.centerx) ** 2 + (earth.rect.centery - enemy.rect.centery) ** 2)
            if distance < earth.radius:
                lose += 1
                enemy.kill()
                enemy = Enemy(enemy_left[random.randint(0, 1)], random.randint(-100, 0), random.randint(0, height),
                              100, 100, 1)
                sprite_enemy_left.add(enemy)

    sprite_enemy_right.draw(screen)
    sprite_enemy_left.draw(screen)
    bullets.draw(screen)
    ship.reset()

    # счетчики очков и пропущено монстров
    text_score = font.render(f'Monsters defeated: {score}', True, (135, 245, 237))
    text_lose = font.render(f'Missed monsters: {lose}', True, (135, 245, 237))
    text_record = font_record.render(f'Record: {record}', True, (3, 135, 113))

    screen.blit(text_score, (10, 10))
    screen.blit(text_lose, (10, 40))
    screen.blit(by_Arakcheev, (width - 115, height - 30))
    screen.blit(text_record, (50, height - 30))

    clock.tick(FPS)
    py.display.update()

    # проверка столкновения выстрелов и спрайтов_enemy
    colledes_sprites_1 = py.sprite.groupcollide(bullets, sprite_enemy_right, True, True)
    for i in colledes_sprites_1:
        score += 1
        Enemy.total_destroyed += 1
        i.kill()
        enemy = Enemy(enemy_right[random.randint(0, 1)], random.randint(width, 1100), random.randint(0, height),
                      100, 100, 1)
        sprite_enemy_right.add(enemy)

    colledes_sprites_2 = py.sprite.groupcollide(bullets, sprite_enemy_left, True, True)
    for i in colledes_sprites_2:
        score += 1
        Enemy.total_destroyed += 1
        i.kill()
        enemy = Enemy(enemy_left[random.randint(0, 1)], random.randint(-100, 0), random.randint(0, height),
                      100, 100, 1)
        sprite_enemy_left.add(enemy)

    # Проверка столкновения по расстоянию
    for enemy in sprite_enemy_right:
        distance = sqrt((ship.rect.centerx - enemy.rect.centerx) ** 2 + (ship.rect.centery - enemy.rect.centery) ** 2)
        if distance < 70:  # Пороговое значение для столкновения
            lose += 1
            enemy.kill()
            enemy = Enemy(enemy_right[random.randint(0, 1)], random.randint(width, 1100), random.randint(0, height),
                          100, 100, 1)
            sprite_enemy_right.add(enemy)

    for enemy in sprite_enemy_left:
        distance = sqrt((ship.rect.centerx - enemy.rect.centerx) ** 2 + (ship.rect.centery - enemy.rect.centery) ** 2)
        if distance < 70:  # Пороговое значение для столкновения
            lose += 1
            enemy.kill()
            enemy = Enemy(enemy_left[random.randint(0, 1)], random.randint(-100, 0), random.randint(0, height),
                          100, 100, 1)
            sprite_enemy_left.add(enemy)

    # надпись победы
    text_win = font_win.render('YOU WINNER!', True, (15, 150, 0))
    if score >= 1001:
        wonder_text = font_wonder.render('This has never happened before... You are a winner!', True, (15, 150, 0))
        restart_text = font.render('to restart press "F12" to exit press "escape"', True, (120, 6, 19))
        record_text = font.render(f'Enemies defeated: {score}', True, (135, 245, 237))

        screen.blit(text_win, (350, 300))
        screen.blit(wonder_text, (190, 400))
        screen.blit(record_text, (410, 660))
        screen.blit(restart_text, (280, 700))
        py.display.update()
        game_over = False

    # надпись поражения
    if lose >= 3:
        text_win = font_win.render('YOU LOSE!', True, (189, 11, 32))
        restart_text = font.render('to restart press "F12" to exit press "escape"', True, (120, 6, 19))
        record_text = font.render(f'Enemies defeated: {score}', True, (135, 245, 237))

        screen.blit(text_win, (390, 550))
        screen.blit(record_text, (410, 660))
        screen.blit(restart_text, (280, 700))
        py.display.update()
        background_sound.stop()
        if game_over:
            game_over_sound.play(loops=0)
        game_over = False

    for event in py.event.get():
        if event.type == py.QUIT:
            run = False
            py.quit()
            break
        if event.type == py.KEYDOWN and event.key == py.K_SPACE:
            if game_over:
                attack_ship_sound.play(loops=0)
                ship.fire()
        elif event.type == py.KEYDOWN and event.key == py.K_F12 and not game_over:  # press restart
            Enemy.total_destroyed = 0
            score = 0
            lose = 0
            for i in sprite_enemy_right:
                i.kill()
            for i in sprite_enemy_left:
                i.kill()
            background_sound.play(loops=-1)

            for enem in range(3):
                enemy = Enemy(enemy_right[random.randint(0, 1)],
                              width, random.randint(0, height),
                              100, 100, 1)
                sprite_enemy_right.add(enemy)

            for enem in range(3):
                enemy = Enemy(enemy_left[random.randint(0, 1)],
                              -100,
                              random.randint(0, height),
                              100, 100, 1)
                sprite_enemy_left.add(enemy)
            game_over = True

        elif event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
            run = False
            py.quit()
            break
