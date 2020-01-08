import pygame
from random import choice
from func import load_image
from coords import create_borders_coords

pygame.init()
pygame.font.init()

WIDTH = 800
HEIGHT = 400
X = - WIDTH // 2
Y = - HEIGHT // 2
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Deadline')
screen.fill((0, 0, 0))

running = True
MOVEEVENT = 30
GOEVENT = 31

pygame.time.set_timer(GOEVENT, 15)
pygame.time.set_timer(MOVEEVENT, 100)
clock = pygame.time.Clock()
millisec = 0

FPS = 20
all_sprites = pygame.sprite.Group()
tasks = pygame.sprite.Group()
character = pygame.sprite.Group()
enemies = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

collected_tasks = 0


def time_left(time):
    left_millisec = 1440 - time
    return (left_millisec % 60, left_millisec // 60)


def show_time(time):  # ДОПИСАТЬ БЛЯ
    minutes, hours = time_left(time)
    line = f'{hours}:{minutes}'
    font = pygame.font.SysFont(None, 30)
    text_coord = 600

    fon = pygame.transform.scale(load_image('data\\fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    # font = pygame.font.Font(None, 30)
    # text_coord = 50

    string_rendered = font.render(line, 1, pygame.Color('black'))
    intro_rect = string_rendered.get_rect()
    text_coord += 10
    intro_rect.top = text_coord
    intro_rect.x = 10
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)


class Map(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)

        self.image = pygame.Surface([0, 0])
        self.image = load_image('data\\map\\map.png')
        self.image = pygame.transform.scale(load_image('data\\map\\map.png'), (3000, 506))

        self.rect = self.image.get_rect()
        self.rect.x = - WIDTH // 2
        self.rect.y = - HEIGHT // 2 - 20


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(character)
        self.x = x
        self.y = y
        self.frames = 11
        self.vx = 0
        self.vy = 0

        self.direction = 0
        self.cur_frame = 0
        self.images_standing = [[], [], [], []]
        self.images_walking = [[], [], [], []]
        # forward - 0, left - 1, back - 2, right - 3

        for direction in range(4):
            for number_file in range(11):
                name = ['data', 'character', 'standing', str(direction), f'{number_file + 1}.png']
                self.images_standing[direction].append(pygame.transform.scale(
                    load_image('\\'.join(name)), (96, 128)))
        for direction in range(4):
            for number_file in range(11):
                name = ['data', 'character', 'walking', str(direction), f'{number_file + 1}.png']
                self.images_walking[direction].append(pygame.transform.scale(
                    load_image('\\'.join(name)), (96, 128)))

        self.image = self.images_standing[0][self.cur_frame]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.Mask((self.rect.w, self.rect.h), False)
        for x in range(self.rect.w // 4, self.rect.w // 4 * 3):
            for y in range(self.rect.h // 9 * 8, self.rect.h):
                self.mask.set_at((x, y), 1)

    def update(self):
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] ^ keys[pygame.K_RIGHT]:
            self.direction = 1 if keys[pygame.K_LEFT] else 3
            self.vx = -10 if keys[pygame.K_LEFT] else 10
            self.rect.x += self.vx if not pygame.sprite.spritecollideany(self, vertical_borders,
                                                                         collided=pygame.sprite.collide_mask) else 0
            moving = True
        elif keys[pygame.K_UP] ^ keys[pygame.K_DOWN]:
            self.direction = 2 if keys[pygame.K_UP] else 0
            self.vy = 10 if keys[pygame.K_DOWN] else -10
            self.rect.y += self.vy if not pygame.sprite.spritecollideany(self, horizontal_borders,
                                                                         collided=pygame.sprite.collide_mask) else 0
            moving = True

        while pygame.sprite.spritecollideany(self, vertical_borders,
                                             collided=pygame.sprite.collide_mask):
            self.rect.x += 1 if self.vx <= 0 else -1
        while pygame.sprite.spritecollideany(self, horizontal_borders,
                                             collided=pygame.sprite.collide_mask):
            self.rect.y += 1 if self.vy <= 0 else -1

        self.image = self.images_standing[self.direction][self.cur_frame % self.frames] \
            if not moving else self.images_walking[self.direction][self.cur_frame % self.frames]
        self.cur_frame += 1


class Tasks(pygame.sprite.Sprite):
    image = load_image(f"data\\tasks\\{choice(['task_1.png', 'task_2.png', 'task_3.png'])}",
                       (0, 0, 0))

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(tasks)
        self.image = Tasks.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.save_y = self.rect.y
        self.upd = 0

    def update(self):
        global collected_tasks
        if pygame.sprite.spritecollideany(self, character):
            collected_tasks += 1
            self.kill()


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
            self.mask = pygame.mask.Mask((1, y2 - y1), True)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
            self.mask = pygame.mask.Mask((x2 - x1, 1), True)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, width, height, path):
        super().__init__(all_sprites)
        self.add(enemies)
        self.image = pygame.transform.scale(load_image(path), (64, 128))
        self.rect = self.image.get_rect()
        self.rect.x = width
        self.rect.y = height
        self.vx = 3
        self.vy = 3

        self.mask = pygame.mask.Mask((self.rect.w, self.rect.h), False)
        for x in range(self.rect.w):
            for y in range(self.rect.h // 9 * 8, self.rect.h):
                self.mask.set_at((x, y), 1)


class CompilationError(Enemy):
    def __init__(self, width, height):
        super().__init__(width, height, "data\\mobs\\mob_1.png")
        self.vy = 0

    def update(self):
        self.rect = self.rect.move(self.vx, 0)
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx


class RuntimeError(Enemy):
    def __init__(self, width, height):
        super().__init__(width, height, "data\\mobs\\mob_3.png")

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        elif pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx


class WrongAnswer(Enemy):
    def __init__(self, width, height):
        super().__init__(width, height, "data\\mobs\\mob_2.png")
        self.vx = 0

    def update(self):
        self.rect = self.rect.move(0, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy


map_level = Map()
borders_coords = create_borders_coords(map_level.rect.x, map_level.rect.y)
for b in borders_coords:
    Border(*b)

CompilationError(200, 200)
RuntimeError(200, 200)
WrongAnswer(200, 200)

player = Character(388, 268)
camera = Camera()

# create all possible coord
tasks_coords = [(X + 100, Y + 100)]
for t in tasks_coords:
    Tasks(*t)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == MOVEEVENT:
            tasks.update()
        if event.type == GOEVENT:
            enemies.update()

    character.update()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    screen.fill((0, 0, 0))

    all_sprites.draw(screen)
    vertical_borders.draw(screen)
    horizontal_borders.draw(screen)
    character.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)
    millisec += 1
    print(millisec % 60, millisec // 60)

    show_time(millisec)
