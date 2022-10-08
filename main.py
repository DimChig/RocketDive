import pygame
import time
import random

pygame.init()
screen = pygame.display.set_mode((600, 900));

dis = pygame.display
# Title
dis.set_caption("Ракета 2Д")

# variables
mx = dis.get_window_size()[0]
my = dis.get_window_size()[1]
playerX = 0
playerY = 0
player_trail = []
tiles = []
tile_size = 10  # editable
tile_gap = mx
tile_gap_start = mx/2 # editable
tile_path_dir = 1
tile_offset = 0
tile_start_path_frequency = 15 # editable

# Player relerele куду
sprite_player = pygame.transform.scale(pygame.image.load("img/ship1.png"), (40,65))  # size 80x129
playerX = 0
playerY = 0
player_speed = 0
player_speed_y = 0
player_speed_y_cof = 1
player_acceleration = 0
player_acceleration_speed = 0
player_max_speed = 10
print("Player: ", playerX, playerY)


class Obstacle:
    def __init__(self, y, arr, idx):
        self.y = y
        self.arr = arr
        self.idx = idx
        self.isPlayerPassed = False


class Tile:
    def __init__(self, x1, x2):
        self.x1 = x1
        self.x2 = x2

def controlPlayerSpeed():
    global player_acceleration_speed
    global player_max_speed
    global player_speed_y, tile_gap

    cof = 0.0015
    player_acceleration_speed += cof/5
    player_max_speed += cof
    player_speed_y += cof
    tile_gap -= cof * 8
    #print(player_acceleration_speed," and ",player_max_speed," and ",player_speed_y)

tile_idx = 0
def generateTile(y):
    arr = []
    global tile_size
    global tile_gap
    global tile_gap_start
    global tile_idx

    #print(mx)
    if tile_gap > tile_gap_start:
        tile_gap -= 3

    gap_count = (int)(tile_gap / tile_size)
    total_count = (int)(mx / tile_size)
    left_count = (int)((total_count - gap_count) / 2)
    right_count = left_count

    # offset random
    global tile_path_dir
    global tile_offset
    controlPlayerSpeed()

    tile_offset += tile_path_dir
    if random.randint(0, 20) == 0:
        tile_path_dir *= -1
    if right_count + gap_count + tile_offset >= total_count and tile_path_dir > 0:
        tile_path_dir *= -1
        tile_offset -= 1
    elif left_count + gap_count - tile_offset >= total_count and tile_offset < 0:
        tile_path_dir *= -1
        tile_offset += 1

    left_count -= tile_offset
    right_count += tile_offset
    #print(tile_offset)

    arr.append(Tile(0, (left_count + 0.5) * tile_size))
    arr.append(Tile(mx - (right_count + 0.5) * tile_size, mx + tile_size))

    tile_idx += 1
    obstacle = Obstacle(y, arr, tile_idx)
    global tiles
    tiles.append(obstacle)

def generateNextTile():
    global tiles
    y = my/2
    if (len(tiles) != 0):
        y = tiles[len(tiles) - 1].y - tile_size
    generateTile(y)

def generateTiles():
    global tiles
    for i in range(0, 100):
        generateNextTile()

        if (tiles[len(tiles) - 1].y > 0):
            drawGame()
            dis.update()
            time.sleep(0.01)


def restartGame():
    global playerX, playerY, player_acceleration, tiles, tile_gap, tile_offset, player_score, player_trail, player_speed, player_speed_y, player_acceleration_speed, player_max_speed
    playerX = mx / 2 - sprite_player.get_width() / 2
    playerY = int(my * 0.9) - sprite_player.get_height() / 2
    player_acceleration = 0

    player_speed = 0  # editable
    player_speed_y = 5  # editable
    player_acceleration_speed = 0.5  # editable
    player_max_speed = 7  # editable

    tile_path_frequency = tile_start_path_frequency
    tile_gap = mx
    tile_offset = 0
    player_score = 0
    player_trail = []
    tiles = []
    generateTiles()
    global running
    running = True
    drawGame()
    dis.update()


def blitRotate(surf, image, pos, originPos, angle):
    angle = 360 - angle
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)


def drawPlayer(x, y):
    angle = player_acceleration * 2
    blitRotate(screen, sprite_player, (x, y),
               (sprite_player.get_width() / 2, sprite_player.get_height() / 2), angle)



def drawTiles():
    global tiles
    global tile_size

    for o in tiles:
        for tile in o.arr:
            pygame.draw.rect(screen, (180, 0, 0), (tile.x1 - tile_size/2, o.y - tile_size/2, tile.x2 - tile.x1, tile_size))

def moveTiles():
    global tiles, player_score
    for o in tiles:
        o.y += player_speed_y
        if o.isPlayerPassed == False and playerY < o.y:
             o.isPlayerPassed = True
             player_score += 1
        if o.y - tile_size*2 > my:
            tiles.remove(o)
            generateNextTile()

font = pygame.font.Font("freesansbold.ttf", 40)
def drawScore():
    global font
    text = font.render(str(int(player_score/25)), True, (0, 0, 0))
    screen.blit(text, (mx / 2 - text.get_width() / 2, text.get_height() / 2 + 50))

def map(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

def drawPlayerTrail():
    global player_trail
    max_size = 20
    for i in range(0, len(player_trail)):
        if (len(player_trail) <= i):
            break
        pos = player_trail[i]
        if pos[1] > my + max_size:
            player_trail.remove(pos)
            i -= 1
        else:
            player_trail[i] = (pos[0], pos[1] + player_speed_y)
            size = 0 + map(player_trail[i][1], playerY, my, 0, max_size)

            #get closest tile
            dist = my
            idx = -1
            for j in range(0, len(tiles)):
                d = abs(tiles[j].y - player_trail[i][1])
                if (d < dist):
                    dist = d
                    idx = tiles[j].idx
                elif (d > dist):
                    break
            #print(idx, " -> ", dist)

            color = (180, 0, 0)
            #print(color)
            #pygame.draw.circle(screen, color, player_trail[i], size)

            center = player_trail[i]
            radius = size

            target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
            shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
            pygame.draw.circle(shape_surf, color, (radius, radius), radius)
            screen.blit(shape_surf, target_rect)


def drawGame():
    screen.fill((255, 255, 255))
    #drawPlayerTrail()
    drawPlayer(playerX, playerY)
    drawTiles()
    drawScore()


def checkPlayerDeath(x):
    if (playerX > mx or playerX < 0):
        gameOver()
    global tiles
    for o in tiles:
        for t in o.arr:
            if (playerY > o.y - tile_size/2 and playerY < o.y + tile_size/2):
                if (playerX > t.x1 and playerX < t.x2):
                    gameOver()


running = True


def gameOver():
    time.sleep(0.3)
    screen.fill((255, 255, 255))
    font = pygame.font.Font("freesansbold.ttf", 70)
    text = font.render("Game Over!", True, (227, 39, 32))
    screen.blit(text, (mx / 2 - text.get_width() / 2, my / 2 - text.get_height()*2))
    global player_score;
    text = font.render("Score: " + str(int(player_score/25)), True, (0, 0, 0))
    screen.blit(text, (mx / 2 - text.get_width() / 2, my / 2))



    global running
    running = False
    dis.update()
    time.sleep(0.8)
    restartGame()

def playerHandlerReleasedKeys():
    global player_acceleration
    global player_acceleration_speed

    if player_acceleration > 0:
        player_acceleration -= player_acceleration_speed
        if player_acceleration < player_acceleration_speed:
            player_acceleration = 0
    if player_acceleration < 0:
        player_acceleration += player_acceleration_speed
        if player_acceleration > -player_acceleration_speed:
            player_acceleration = 0

# Game Loop
restartGame()
clock = pygame.time.Clock()
while running:
    clock.tick(60)
    #print(player_acceleration)
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False

    #print(player_acceleration)
    keys = pygame.key.get_pressed()  # checking pressed keys
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_acceleration += player_acceleration_speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_acceleration -= player_acceleration_speed
    if not keys[pygame.K_d] and not keys[pygame.K_RIGHT] and not keys[pygame.K_a] and not keys[pygame.K_LEFT]:
        playerHandlerReleasedKeys()
    if (keys[pygame.K_d] and keys[pygame.K_a]) or (keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]):
        playerHandlerReleasedKeys()

    if player_acceleration > player_max_speed:
        player_acceleration = player_max_speed
    if player_acceleration < -player_max_speed:
        player_acceleration = -player_max_speed

    playerX += player_acceleration

    drawGame()
    checkPlayerDeath(playerX)
    moveTiles()
    dis.update()
