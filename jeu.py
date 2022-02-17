import math
import random

import neat
import numpy as np
import pygame

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
MAXFPS = 30
SCREEN_WIDTH, SCREEN_HEIGHT, FPS = 1500, 600, 120
pygame.display.set_caption('Car Racing')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# ----------------------------------------------------------------------------------------------------------------------

roadcenter_img = pygame.image.load('sprites/road.png').convert_alpha()
roadcenter_img = pygame.transform.scale(roadcenter_img, (600, 600))

roadside_img = pygame.image.load('sprites/side.png').convert_alpha()
roadside_img = pygame.transform.scale(roadside_img, (600, 600))

policecar_img = pygame.image.load('sprites/car.png')
policecar_img = pygame.transform.scale(policecar_img, (37, 73))

redcar_img = pygame.image.load('sprites/car1.png')
redcar_img = pygame.transform.scale(redcar_img, (37, 73))

bluecar_img = pygame.image.load('sprites/car2.png')
bluecar_img = pygame.transform.scale(bluecar_img, (37, 73))

yellowcar_img = pygame.image.load('sprites/car3.png')
yellowcar_img = pygame.transform.scale(yellowcar_img, (37, 73))


class Background:
    def __init__(self, x, speed=15):
        self.bg = roadcenter_img
        self.side = roadside_img
        self.PosY, self.speed = 0, speed
        self.x = x

    def drawRoad(self):
        self.PosY += self.speed
        if self.PosY < SCREEN_HEIGHT:
            screen.blit(self.bg, (self.x, int(self.PosY)))
            screen.blit(self.bg, (self.x, int(self.PosY) - SCREEN_HEIGHT))
        else:
            self.PosY = 0
            screen.blit(self.bg, (self.x, int(self.PosY)))

    def drawSide(self):
        if self.PosY < SCREEN_HEIGHT:
            screen.blit(self.side, (self.x, int(self.PosY)))
            screen.blit(self.side, (self.x, int(self.PosY) - SCREEN_HEIGHT))
        else:
            self.PosY = 0
            screen.blit(self.side, (self.x, int(self.PosY)))


# ----------------------------------------------------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.image = policecar_img
        self.PosX, self.PosY, self.speed, self.carSpeed = 1200, 500 - 32, 7, -5
        self.trace = (0, 0, 0, 0)
        self.moving_left, self.moving_right, self.forward = False, False, False

        self.mask = pygame.mask.from_surface(self.image)

        self.rotation = 0
        self.maxrot = 50
        self.score = 0
        self.rect = pygame.Rect(self.trace)

        self.old_score = 0

    def update(self, events):
        for event in events:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.moving_left = True
                elif event.key == pygame.K_RIGHT:
                    self.moving_right = True
                elif event.key == pygame.K_UP:
                    self.forward = True
                elif event.key == pygame.K_ESCAPE:
                    exit()
                    return

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.moving_left = False
                elif event.key == pygame.K_RIGHT:
                    self.moving_right = False
                elif event.key == pygame.K_UP:
                    self.forward = False

        self.speed *= 0.9
        self.speed += 0.7
        self.PosX -= self.speed * math.sin(math.radians(self.rotation))

        if self.moving_left and not self.PosX - 2.5 <= 1000:
            self.rotation += (self.speed / 2)

        if self.moving_right and not self.PosX + 2.5 >= 1375:
            self.rotation -= (self.speed / 2)

        if self.forward:
            if self.rotation > 0:
                self.rotation -= (self.speed / 2)
                if self.rotation < self.speed / 2:
                    self.rotation = 0
            elif self.rotation < 0:
                self.rotation += (self.speed / 2)
                if self.rotation > self.speed / 2:
                    self.rotation = 0

        if self.rotation < -self.maxrot:
            self.rotation = -self.maxrot
        elif self.rotation > self.maxrot:
            self.rotation = self.maxrot

        if self.PosX - 2.5 <= 1000:
            self.PosX = 1000
        elif self.PosX + 2.5 >= 1375:
            self.PosX = 1375

    def draw(self):
        image = pygame.transform.rotate(self.image, self.rotation)
        self.mask = pygame.mask.from_surface(image)
        rect = self.image.get_rect(topleft=(self.PosX, self.PosY))
        rot_rect = image.get_rect(center=rect.center)
        self.trace = screen.blit(image, rot_rect)
        self.trace = (self.trace[0] + 5, self.trace[1] + 5, self.trace[2] - 10, self.trace[3] - 10)
        self.rect = pygame.Rect(self.trace)

    def addscore(self, score):
        self.score += score


# ----------------------------------------------------------------------------------------------------------------------

class IA:
    def __init__(self, x, y, width, height):
        self.x = x - width / 2
        self.y = y - height / 2
        self.height = height
        self.width = width
        self.image = policecar_img
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.blit(self.image, (0, 0))
        self.rotation = 0
        self.speed = 0
        self.sensorsList = []
        self.maxrot = 50
        self.is_alive = True
        self.score = 0
        self.trace = (0, 0, 0, 0)
        self.angles = [[3, 300], [-3, 300], [22, 300], [-22, 300], [90, 300], [-90, 300]]
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        if not self.is_alive: return
        self.rect.topleft = (int(self.x), int(self.y))
        rotated = pygame.transform.rotate(self.surface, self.rotation)
        rotated.set_colorkey((0, 0, 0))
        surface_rect = self.surface.get_rect(topleft=self.rect.topleft)
        new_rect = rotated.get_rect(center=surface_rect.center)
        screen.blit(rotated, new_rect.topleft)

    def update(self):
        if not self.is_alive: return
        self.speed *= 0.9
        self.x -= self.speed * math.sin(math.radians(self.rotation))
        self.speed += 0.7
        self.sensors()

        self.x -= self.speed * math.sin(math.radians(self.rotation))

        if self.rotation < -self.maxrot:
            self.rotation = -self.maxrot
        elif self.rotation > self.maxrot:
            self.rotation = self.maxrot

    def addscore(self, score):
        self.score += score

    def sensors(self):
        list = []
        self.sensorsList = []
        angles = self.angles
        x = self.rect.centerx
        y = self.rect.centery + 15
        screenrect = screen.get_rect()
        for pair in angles:
            angle = pair[0]
            lmax = pair[1]
            rot = math.radians(self.rotation + angle + 90)
            l = 1
            linecolor = pygame.Color('green')
            pointx = int(x + math.cos(rot) * l)
            pointy = int(y - math.sin(rot) * l)
            while not screen.get_at((pointx, pointy)) == pygame.Color(255, 255, 255, 255) and l < lmax:
                l += 1
                pointx = int(x + math.cos(rot) * l)
                pointy = int(y - math.sin(rot) * l)
                if not screenrect.collidepoint(pointx, pointy):
                    l -= 1
                    pointx = int(x + math.cos(rot) * l)
                    pointy = int(y - math.sin(rot) * l)
                    break

            if l < lmax * 75 / 100:
                linecolor = pygame.Color('red')

            self.sensorsList.append([(x, y), (pointx, pointy), linecolor])
            list.append((angle, l, lmax))

        return list

    def draw_sensors(self):
        for start, end, color, in self.sensorsList:
            pygame.draw.line(screen, color, start, end, 1)
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 1)

    def go_right(self):
        self.rotation -= (self.speed / 2)

    def go_left(self):
        self.rotation += (self.speed / 2)

    def go_straight(self):
        if self.rotation > 0:
            self.go_right()
            if self.rotation < self.speed / 2:
                self.rotation = 0
        elif self.rotation < 0:
            self.go_left()
            if self.rotation > self.speed / 2:
                self.rotation = 0

    def get_inputs(self):
        sensors = self.sensors()
        outputs = [0, 0, 0, 0, 0, 0]
        outputs = np.array(outputs)
        for i in range(len(outputs)):
            outputs[i] = sensors[i][1]
        return outputs


class Enemy:
    def __init__(self, x, y, width, height, color, speed=1, image=bluecar_img):
        self.image = image
        self.x = x - width / 2
        self.y = y - height / 2
        self.height = height
        self.width = width
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.blit(self.image, (0, 0))
        self.rotation = 0
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.y -= self.speed
        if self.y > screen.get_height():
            del self
            return False
        return True

    def draw(self):
        self.rect.topleft = (int(self.x), int(self.y))
        rotated = pygame.transform.rotate(self.surface, self.rotation)
        rotated.set_colorkey((0, 0, 0))
        self.image = rotated
        surface_rect = self.surface.get_rect(topleft=self.rect.topleft)
        new_rect = rotated.get_rect(center=surface_rect.center)
        screen.blit(rotated, new_rect.topleft)

    def drawHitboxes(self):
        outline = pygame.mask.from_surface(self.image).outline()
        oline = []
        for x, y in outline:
            a = (x + self.x, y + self.y)
            oline.append(a)
        pygame.draw.polygon(screen, (255, 255, 255), oline, 0)


def drawNetwork(network, net_id=0):
    nodes = {netio: (0, 0) for netio in network.input_nodes + network.output_nodes}
    font = pygame.font.SysFont(None, 18)
    x = 660
    y = 50
    dy = -10
    dy2 = -10
    dy3 = -10
    for i, value in network.values.items():  # dictionnaire, les i negatifs sont les entrées et les positifs les sorties
        if i >= 0:
            color = pygame.Color((0, int(255 * value), 0))
        else:
            color = pygame.Color((255 - int(255 * value / 300), 0, 0))

        if i in network.input_nodes + network.output_nodes:
            if i < 0:  # inputs
                pygame.draw.circle(screen, color, (x, y + dy), 15)
                nodes[i] = (x, y + dy)
                txt = font.render(str(i) + ' : ' + str(value), True, pygame.Color((0, 0, 0)))
                screen.blit(txt, (x - 60, y + dy))
                dy += 50
            else:  # outputs
                pygame.draw.circle(screen, color, (x + 170, y + 75 + dy2), 15)
                nodes[i] = (x + 170, y + 75 + dy2)
                val = np.format_float_scientific(value, precision=2, exp_digits=3)
                txt = font.render(str(i) + ' : ' + str(val), True, pygame.Color((0, 0, 0)))
                screen.blit(txt, (x + 190, y + 75 + dy2))
                dy2 += 50
        else:  # hidden layer
            color = pygame.Color((0, 0, 255 * value))
            pygame.draw.circle(screen, color, (x + 85, y + 90 + dy3), 7)
            nodes[i] = (x + 85, y + 90 + dy3)
            dy3 += 50

    for node_id, act_func, agg_func, bias, response, links in network.node_evals:
        nodepos = nodes[node_id]
        for i, weight in links:
            endpos = nodes[i]
            color = pygame.Color(127, 127, 127)
            pygame.draw.line(screen, color, nodepos, endpos, 1)

    txt = font.render('fitness = ' + str(round(carList[net_id].score, 2)), True, pygame.Color((0, 0, 0)))
    screen.blit(txt, (x + 70, y - 25))


def makeSpawnList():
    spawnlist = [(300, 5, bluecar_img), (130, 4, yellowcar_img),
                 (470, 4, yellowcar_img)]  # x entre 130 et 470, speed entre 2 et 5

    previous_rx = [130, 470]
    for i in range(200):
        enemieimg = np.random.choice([yellowcar_img, bluecar_img, redcar_img])
        rx = random.randint(130, 470)
        while (previous_rx[0] - 37 < rx < previous_rx[0] + 37) or (previous_rx[1] - 37 < rx < previous_rx[1] + 37):
            rx = random.randint(130, 470)

        previous_rx[1] = previous_rx[0]
        previous_rx[0] = rx

        rspeed = int(random.uniform(30, 60) / 8)
        spawnlist.append((rx, rspeed, enemieimg))
    return spawnlist


def enemyCollision(car, enemy):
    offset_x = enemy.x - car.rect.left
    offset_y = enemy.y - car.rect.top
    if car.mask.overlap(enemy.mask, (int(offset_x), int(offset_y))):
        return True
    return False


borders = []  # bordure de la route
borders.append(pygame.Rect(0, 0, 100, 600))
borders.append(pygame.Rect(510, 0, 400, 600))


def WallCollision(car):
    for border in borders:
        if car.rect.colliderect(border):
            return True


gamespeed = 1
generation = 0
IAbestScore = 0

bgPlayer = Background(900)
bgIA = Background(0)
player = Player()

spawnlist = makeSpawnList()
enemiesJoueur = []
enemiesIA = []
spawncounterJoueur = 0

carList = []
drawALL = False

GameoverHumain = False


def simulation(genomes, config):
    global clock, MAXFPS, enemiesIA, carList, generation, drawALL, spawnlist, stats, bgPlayer, player, gamespeed, GameoverHumain, enemiesJoueur, enemiesIA, spawncounterJoueur, IAbestScore

    bestfit = [c.fitness for c in stats.most_fit_genomes]
    print('meilleur score par génération:')
    for score in bestfit:
        print('génération ' + str(generation) + ': ', int(score))
    bestfit = [g.fitness for g in stats.most_fit_genomes]

    big_font = pygame.font.Font('Font/Retro.ttf', 30)
    small_font = pygame.font.Font('Font/Retro.ttf', 20)

    networks = []
    enemiesIA = []
    carList = []
    selected = None

    nbAlive = len(genomes)

    for i, genome in genomes:
        carList.append(IA(300, 500, 37, 73))
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(network)
        genome.fitness = 0

    gameover = False
    spawnTimer = 0
    spawncounterIA = 0

    while not gameover:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                gameover = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for car in carList:
                    if car.is_alive:
                        if car.rect.collidepoint(pygame.mouse.get_pos()):
                            selected = carList.index(car)

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]: GameoverHumain = False

        current_fps = clock.get_fps()
        game_speed = (current_fps + 1) / MAXFPS
        spawnTimer += clock.get_time() * game_speed

        if spawnTimer > 1150:
            rx = spawnlist[spawncounterIA % len(spawnlist)][0]
            rspeed = spawnlist[spawncounterIA % len(spawnlist)][1]
            enemieimg = spawnlist[spawncounterIA % len(spawnlist)][2]
            spawncounterIA += 1
            enemie = Enemy(rx, 0, 37, 73, (255, 255, 255), -1 * rspeed, enemieimg)
            enemiesIA.append(enemie)

            rx = spawnlist[spawncounterJoueur % len(spawnlist)][0]
            rspeed = spawnlist[spawncounterJoueur % len(spawnlist)][1]
            enemieimg = spawnlist[spawncounterJoueur % len(spawnlist)][2]
            enemie = Enemy(900 + rx, 0, 37, 73, (255, 255, 255), -1 * rspeed, enemieimg)
            enemiesJoueur.append(enemie)
            spawncounterJoueur += 1

            spawnTimer = 0

        bgPlayer.drawRoad()
        bgIA.drawRoad()
        for border in borders:
            pygame.draw.rect(screen, (255, 255, 255), border)

        for enemy in enemiesIA + enemiesJoueur:
            if not enemy.update():
                del enemy
            else:
                enemy.drawHitboxes()

        for i in range(len(carList)):
            car = carList[i]
            if car.score > IAbestScore: IAbestScore = car.score
            if car.is_alive:
                output = networks[i].activate(car.get_inputs())
                action = output.index(max(output))
                if action == 0:
                    car.go_left()
                elif action == 1:
                    car.go_right()
                elif action == 2:
                    car.go_straight()

                car.update()
                car.addscore(1 / gamespeed)
                car.draw()
                if drawALL: car.draw_sensors()
                if WallCollision(car):
                    nbAlive -= 1
                    genomes[i][1].fitness += car.score
                    car.is_alive = False
                    if i == selected: selected = None
                    continue
                for enemy in enemiesIA:
                    if enemyCollision(car, enemy):
                        nbAlive -= 1
                        genomes[i][1].fitness += car.score
                        car.is_alive = False
                        if i == selected: selected = None
                        break

        if nbAlive <= 0:
            print('generation ', generation, ' dead')
            generation += 1
            break

        for enemy in enemiesIA + enemiesJoueur:
            enemy.draw()
            if enemyCollision(player, enemy):
                spawncounterJoueur = 0
                enemiesJoueur = []
                GameoverHumain = True
                player.moving_left = False
                player.moving_right = False

        if not selected is None:
            drawNetwork(networks[selected], selected)
            carList[selected].draw_sensors()

        bgIA.drawSide()
        bgPlayer.drawSide()

        if not GameoverHumain:
            player.update(events)
            player.addscore(1 / gamespeed)
            player.draw()
            txt_score = small_font.render('Score:' + str(int(player.score)), True, (255, 255, 255))
            screen.blit(txt_score, (910, 540))
            player.old_score = player.score
        else:
            enemiesJoueur = []
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(900, 0, 600, 600))
            txt = big_font.render('Votre score est: ' + str(int(player.old_score)), True, (255, 255, 255))
            screen.blit(txt, (1000, 300))
            txt = small_font.render('Appuyez sur espace pour rejouer', True, (255, 255, 255))
            screen.blit(txt, (1000, 400))
            player.PosX = 1180
            player.rotation = 0
            player.score = 0

        txt = small_font.render('génération: ' + str(generation), True, (0, 0, 0))
        screen.blit(txt, (650, 500))
        txt = small_font.render("meilleure score", True, (0, 0, 0))
        screen.blit(txt, (610, 550))
        txt = small_font.render("obtenu par l'IA:" + str(int(IAbestScore)), True, (0, 0, 0))
        screen.blit(txt, (610, 570))

        clock.tick(MAXFPS)
        pygame.display.flip()


stats = neat.StatisticsReporter()


def main():
    configFile = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, configFile)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(stats)

    population.run(simulation, 1000)


if __name__ == '__main__':
    main()
