# https://www.youtube.com/watch?v=AY9MnQ4x3zk Tutorial used for PyGame

from math import sin
import pygame
from sys import exit
import random

# Some functions and classes are seperated into a different file for readability
from vectors import *

# Window setup
width = 1280
height = 720
margin = 75 # Border where items can't spawn

pygame.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Snake')
clock = pygame.time.Clock()

# Game variables
global player_dead
player_dead = False

global scale
scale = 3 # Global sprite scaling

# Load highscore from save
highscore = 0
try:
    with open('highscore.txt', 'r') as f:
        highscore = int(f.read())
        print(f'Previous highscore: {highscore}')
except:
    print('No highscores saved.')
    with open('highscore.txt', 'w') as f:
        f.write('0')

global score
score = 0

global dt
global player_invulnerability
elapsedTime = 0
player_invulnerability = 0 # Was used to fix collision bug

# region Sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame = 0
        self.animating = False
        self.spritesheet = pygame.image.load('sprites/headspritesheet.png').convert_alpha()
        self.size = self.spritesheet.get_size()
        self.spritesheet = pygame.transform.scale(self.spritesheet, (self.size[0]*scale, self.size[1]*scale))
        self.image = self.spritesheet.subsurface((0, 0, 16 * scale, 16 * scale))

        self.rect = self.image.get_rect(center=(width/2, height/2))
        self.pos = Vector2(self.rect.x, self.rect.y)
        self.oldPos = Vector2(self.pos.x - 1, self.pos.y)
        self.dir = Vector2.Zero()
        self.newDir = Vector2.Zero()
        self.mvmtSpeed = 285
        self.mouseInfluence = .11

        self.bodyParts = []
        self.partDistance = 14 * scale # Distance between two BodyPieces
        self.radius = self.rect.width / 2 # Collision radius

        self.dead = False
        self.followMouse = True
        self.timeOfDeath = 0

        self.deathSound = pygame.mixer.Sound('audio/death.wav')
        self.deathSound.set_volume(0.25)

    def reset(self):
        self.followMouse = False
        self.dead = False
        self.animating = False

        self.bodyParts = []
        playerBody.empty()

        self.rect = self.image.get_rect(center=(width/2, height/2))
        self.pos = Vector2(self.rect.x, self.rect.y)
        self.oldPos = Vector2(self.pos.x - 1, self.pos.y)
        self.dir = Vector2.Zero()
        self.newDir = Vector2.Zero()
        self.mvmtSpeed = 285

        self.frame = 0
        self.image = self.spritesheet.subsurface(
            (int(self.frame) * 16 * scale, 0, 16 * scale, 16 * scale))

    def explode(self):
        self.animating = True
        for part in self.bodyParts:
            part.explode()

    def animate(self, dt):
        if self.frame < 7:
            self.frame += dt * 10
        self.frame = min(self.frame, 7)
        self.image = self.spritesheet.subsurface((int(self.frame) * 16 * scale, 0, 16 * scale, 16 * scale)) # Find correct frame in spritesheet

    def menu(self):
        self.reset()
        self.followMouse = True
        for i in range(6):
            self.addPart()

    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center=(width/2, height/2))

    def addPart(self):
        part = self.BodyPiece(len(self.bodyParts) + 1) # New body instance
        self.bodyParts.append(part)
        # Assign instance to spritelayer with layer sorting
        playerBody.add(part, layer=90 - len(self.bodyParts))

        # Calculate position for new BodyPiece
        if len(self.bodyParts) > 1:
            prevPart = self.bodyParts[len(self.bodyParts) - 2]
            prevPart2 = self.bodyParts[len(
                self.bodyParts) - 3] if len(self.bodyParts) > 2 else self
            dir = (prevPart2.pos - prevPart.pos).normalize()
            part.pos = prevPart.pos - dir * self.partDistance
        else:
            part.pos = self.pos - self.dir * self.partDistance * 1.25

        self.mvmtSpeed += 20 # Increase speed after each body part

    def onDeath(self, elapsedTime):
        if not self.dead:
            self.mvmtSpeed = 0
            self.dead = True
            self.timeOfDeath = elapsedTime
            pygame.mixer.Channel(0).play(self.deathSound)
            pygame.mixer.music.fadeout(200)

            print(f'You died! Score: {score}')

    # Calculate position for each BodyPiece
    def simulateBody(self):
        for i, part in enumerate(self.bodyParts):
            prevPart = self.bodyParts[i - 1] if i > 0 else self
            dir = (prevPart.pos - part.pos).normalize() if prevPart is not self else (
                prevPart.pos - part.pos).normalize() * 1.25
            part.pos = prevPart.pos - dir * self.partDistance
            part.update()

    def update(self, dt):
        if self.animating:
            self.animate(dt)

        x, y = pygame.mouse.get_pos()
        mousePos = Vector2(x, y) - Vector2(self.rect.width / 2, self.rect.height / 2)
        mouseDir = (self.pos - mousePos).normalize() # Normalized direction between previous and current frame
        self.dir = (self.pos - self.oldPos).normalize()
        self.oldPos = self.pos
        self.newDir = Vector2.Lerp(self.dir, -mouseDir, self.mouseInfluence) * self.mvmtSpeed
        self.pos = self.pos + self.newDir * dt if not self.followMouse else mousePos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        self.simulateBody()

    class BodyPiece(pygame.sprite.Sprite):
        def __init__(self, animOffset=0):
            super().__init__()
            self.frame = -animOffset / 2
            self.animating = False
            self.spritesheet = pygame.image.load('sprites/bodyspritesheet.png').convert_alpha()
            self.size = self.spritesheet.get_size()
            self.spritesheet = pygame.transform.scale(self.spritesheet, (self.size[0]*scale, self.size[1]*scale))
            self.image = self.spritesheet.subsurface((0, 0, 16 * scale, 16 * scale))

            self.rect = self.image.get_rect(center=(width/2, height/2))
            self.pos = Vector2.Zero()
            self.radius = self.rect.width / 2

        def explode(self):
            self.animating = True

        def animate(self, dt):
            if self.frame < 7:
                self.frame += dt * 10
            self.frame = min(self.frame, 7)
            self.image = self.spritesheet.subsurface((int(max(self.frame, 0)) * 16 * scale, 0, 16 * scale, 16 * scale)) # Find correct frame in spritesheet

        def resize(self, r_scale):
            self.size = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
            self.rect = self.image.get_rect(center=(width/2, height/2))

        def update(self):
            self.rect.x = self.pos.x
            self.rect.y = self.pos.y

            if self.animating:
                self.animate(dt)

class Apple(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame = 1
        self.animating = False
        self.spritesheet = pygame.image.load('sprites/applespritesheetshort.png').convert_alpha()
        self.size = self.spritesheet.get_size()
        self.spritesheet = pygame.transform.scale(self.spritesheet, (self.size[0]*scale, self.size[1]*scale))
        self.image = self.spritesheet.subsurface((0, 0, 16 * scale, 16 * scale))

        self.rect = self.image.get_rect(center=(random.uniform(0 + margin, width - margin), random.uniform(0 + margin, height - margin)))
        self.newX, self.newY = self.rect.x, self.rect.y

        self.sounds = [
            pygame.mixer.Sound('audio/munch1.wav'),
            pygame.mixer.Sound('audio/munch2.wav'),
            pygame.mixer.Sound('audio/munch3.wav'),
            pygame.mixer.Sound('audio/munch4.wav')]
        self.eatSound = random.choice(self.sounds)
        self.eatSound.set_volume(.2)
        self.getSound = pygame.mixer.Sound('audio/appleGet.wav')
        self.getSound.set_volume(.2)

    def animate(self, dt):
        global bombs

        if self.frame < 3:
            self.frame += dt * 15
        self.frame = min(self.frame, 7)
        self.image = self.spritesheet.subsurface((int(self.frame) * 16 * scale, 0, 16 * scale, 16 * scale))

        if self.frame >= 3:
            self.replace()
            self.animating = False
            self.frame = 1
            self.image = self.spritesheet.subsurface((0, 0, 16 * scale, 16 * scale))

            for bomb in bombs.sprites():
                bomb.replace()

    def eat(self):
        self.eatSound = random.choice(self.sounds)
        self.eatSound.set_volume(0.2)
        pygame.mixer.Channel(0).play(self.eatSound)
        self.getSound.play()

        self.animating = True

    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(
        self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center=(width/2, height/2))

    def replace(self):
        self.rect = self.image.get_rect(center=(random.uniform(0 + margin, width - margin), random.uniform(0 + margin, height - margin))) # Random position within screen margins
        self.newX, self.newY = self.rect.x, self.rect.y

    def update(self, dt, time):
        if self.animating:
            self.animate(dt)
        else:
            self.rect.y = self.newY + sin(time * 5) * 4 # Sine wave animation

class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame = 1
        self.animating = False
        self.spritesheet = pygame.image.load('sprites/bombsprites.png').convert_alpha()
        self.size = self.spritesheet.get_size()
        self.spritesheet = pygame.transform.scale(self.spritesheet, (self.size[0]*scale, self.size[1]*scale))
        self.image = self.spritesheet.subsurface((0, 0, 16 * scale, 16 * scale))

        self.rect = self.image.get_rect(center=(random.uniform(0 + margin, width - margin), random.uniform(0 + margin, height - margin)))
        self.newX, self.newY = self.rect.x, self.rect.y

        self.getSound = pygame.mixer.Sound('audio/bomb.wav')
        self.getSound.set_volume(0.15)
        self.radius = self.rect.width / 2

        self.replace()

    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center=(width/2, height/2))

    def animate(self, dt):
        if self.frame < 7:
            self.frame += dt * 10
        self.frame = min(self.frame, 7)
        self.image = self.spritesheet.subsurface((int(self.frame) * 16 * scale, 0, 16 * scale, 16 * scale))

    def explode(self):
        self.animating = True

    def replace(self):
        while True:
            newPos = self.image.get_rect(center=(random.uniform(0 + margin, width - margin), random.uniform(0 + margin, height - margin)))
            if (abs(newPos.x - player.sprite.rect.x) > 100 and abs(newPos.y - player.sprite.rect.y) > 100) and (abs(newPos.x - apple.sprite.rect.x) > 64 and abs(newPos.y - apple.sprite.rect.y) > 64):
                break
        self.rect = newPos
        self.newX, self.newY = self.rect.x, self.rect.y

    def update(self, time, dt):
        if self.animating:
            self.animate(dt)
        else:
            self.rect.y = self.newY + sin(time * 5) * 4 # Sine wave animation

playerBody = pygame.sprite.LayeredUpdates()

player = pygame.sprite.GroupSingle()
player.add(Player())

apple = pygame.sprite.GroupSingle()
apple.add(Apple())

bombs = pygame.sprite.Group()
#endregion

# UI Text
font = 'sprites/Fonts/Square.ttf'
score_font = pygame.font.Font(font, 275)
score_text = score_font.render(str(score), True, 'White')

game_over_font = pygame.font.Font(font, 200)
game_over_text = game_over_font.render('Game Over', True, 'White')

score_details_font = pygame.font.Font(font, 50)
score_details_text = score_details_font.render(f"Score: {score} - Highscore: {highscore}", True, 'White')

paused_text = game_over_font.render('Paused', True, 'White')

bg = pygame.image.load("sprites/tilebgbig.png")
logoimg = pygame.image.load("sprites/UI/snakelogo.png")
logoimg = pygame.transform.scale(logoimg, (logoimg.get_width()*3, logoimg.get_height()*3))
logo = pygame.Surface(logoimg.get_size())

# Scene management
inGame = False
transitioning = False
transitionForward = True
transitionRadius = 0

# Game initialization
pygame.mixer.music.load('audio/music.wav')
pygame.mixer.music.set_volume(0.08)
pygame.mixer.music.play(-1)
pygame.mixer.Channel(0).set_volume(1)

for i in range(6):
    player.sprite.addPart()

#region Custom button implementation
menu_switch_ignore = False # Prevents looping through menus

class Button():
    def __init__(self, x, y, inactive_image, active_image, scale, onClick, key=None):
        self.size = inactive_image.get_size()
        self.inactive_image = pygame.transform.scale(inactive_image, (self.size[0]*scale, self.size[1]*scale)).convert_alpha()
        self.active_image = pygame.transform.scale(active_image, (self.size[0]*scale, self.size[1]*scale)).convert_alpha()
        self.inactive_image.set_alpha(225)
        self.active_image.set_alpha(225)
        self.image = pygame.transform.scale(self.inactive_image, self.inactive_image.get_size()).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        self.btnOverlay = pygame.Surface((self.size[0]*scale, self.size[1]*scale))
        self.btnOverlay.set_alpha(0)
        self.btnOverlay.fill((0, 0, 0))

        self.hover = False
        self.mouseDown = False
        self.toggleActive = False
        self.ignoreMouse = False

        self.onClick = onClick
        self.key = key

        self.clickSound = pygame.mixer.Sound('audio/click.wav')
        self.hoverSound = pygame.mixer.Sound('audio/hover.wav')
        self.clickSound.set_volume(0.35)
        self.hoverSound.set_volume(0.35)

    def setActive(self, active):
        self.toggleActive = active
        self.image = self.active_image if active else self.inactive_image

    def update(self):
        global menu_switch_ignore

        mousePos = pygame.mouse.get_pos()

        # Hover effect
        if self.rect.collidepoint(mousePos):
            self.btnOverlay.set_alpha(30)
            if not self.hover:
                self.hover = True
                pygame.mixer.Channel(0).play(self.hoverSound)
        else:
            self.btnOverlay.set_alpha(0)
            self.hover = False

        # Ignore mouse if mousedown started outside of button
        if pygame.mouse.get_pressed()[0]:
            if not self.rect.collidepoint(mousePos) or menu_switch_ignore:
                self.ignoreMouse = True
        else:
            self.ignoreMouse = False

        # Button clicked
        if ((self.rect.collidepoint(mousePos) and pygame.mouse.get_pressed()[0]) or (pygame.key.get_pressed()[self.key] if self.key else False)) and not self.ignoreMouse:
            self.btnOverlay.set_alpha(60) # Click effect

            if not self.mouseDown:
                self.onClick()
                self.mouseDown = True
                self.toggleActive = not self.toggleActive
                self.image = self.active_image if self.toggleActive else self.inactive_image
                pygame.mixer.Channel(0).play(self.clickSound)
        else:
            if self.mouseDown:
                self.mouseDown = False
                self.btnOverlay.set_alpha(0)

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.btnOverlay, self.rect)

music = True

def ToggleMusic():
    global music
    music = not music
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(100)
    else:
        pygame.mixer.music.play(-1, 0, 100)

sfx = True
sfx_channel = pygame.mixer.Channel(0)

def ToggleSfx():
    global sfx
    sfx = not sfx
    if sfx:
        pygame.mixer.Channel(0).set_volume(1)
    else:
        pygame.mixer.Channel(0).set_volume(0)

paused = False
def TogglePause(): 
    global paused
    paused = not paused

def AddBomb():
    global bombs
    bombs.add(Bomb())

def OnPlay():
    global transitioning, transitionForward
    transitionForward = True
    transitioning = True

def StartGame():
    global inGame, score, player_invulnerability, elapsedTime, score_text, paused, score_details_text, transitioning

    player.sprite.reset()
    bombs.empty()

    if music and not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1, 0, 100)

    score = 0
    player_invulnerability = 0
    elapsedTime = 0
    score_text = score_font.render(str(score), True, 'White')
    score_details_text = score_details_font.render(f"Score: {score} - Highscore: {highscore}", True, 'White')

    pause_button.setActive(False)
    music_button.setActive(not music)
    sound_button.setActive(not sfx)

    paused = False
    inGame = True

def QuitGame():
    pygame.quit()
    exit()

def OnMenu():
    global transitioning, transitionForward, paused
    transitionForward = False
    transitioning = True
    paused = True

def ToMenu():
    global inGame, menu_switch_ignore, transitioning, transitionForward

    player.sprite.menu()
    if not pygame.mixer.music.get_busy() and music:
        pygame.mixer.music.play(-1, 0, 100)

    menu_switch_ignore = True
    inGame = False

music_button = Button(width - 50, height - 50, pygame.image.load('sprites/UI/musicbtn.png'), pygame.image.load('sprites/UI/disabledbtn.png'), 4, ToggleMusic, pygame.K_m)
sound_button = Button(width - 125, height - 50, pygame.image.load('sprites/UI/soundbtn.png'), pygame.image.load('sprites/UI/disabledbtn.png'), 4, ToggleSfx, pygame.K_n)
pause_button = Button(width - 200, height - 50, pygame.image.load('sprites/UI/pausebtn.png'), pygame.image.load('sprites/UI/resumebtn.png'), 4, TogglePause, pygame.K_SPACE)

gameButtons = [music_button, sound_button, pause_button] # In-game buttons

play_button = Button(width/2, height/2 + 125, pygame.image.load('sprites/UI/playbtn.png'), pygame.image.load('sprites/UI/playbtn.png'), 5, OnPlay, pygame.K_RETURN)
quit_button = Button(width/2, height/2 + 250, pygame.image.load('sprites/UI/quitbtn.png'), pygame.image.load('sprites/UI/quitbtn.png'), 5, QuitGame, pygame.K_q)

menuButtons = [play_button, quit_button] # Main menu buttons

restart_button = Button(width/2, height/2 + 50, pygame.image.load('sprites/UI/playbtn.png'), pygame.image.load('sprites/UI/playbtn.png'), 5, StartGame, pygame.K_r)
menu_button = Button(width/2, height/2 + 150, pygame.image.load('sprites/UI/menubtn.png'), pygame.image.load('sprites/UI/menubtn.png'), 5, OnMenu, pygame.K_t)

gameOverButtons = [restart_button, menu_button, quit_button] # Game over & pause buttons

#endregion

# Check game collisions
def checkCollisions(elapsedTime):
    global score, score_text, player_invulnerability, highscore, score_details_text
    
    # Collisions with apples
    if pygame.sprite.collide_rect(apple.sprite, player.sprite) and not apple.sprite.animating:
        apple.sprite.eat()
        player.sprite.addPart()
        score += 1
        score_text = score_font.render(str(score), True, 'White')

        player_invulnerability = 0

        if score > highscore:
            highscore = score
            with open("highscore.txt", "w") as f:
                f.write(str(highscore))

        score_details_text = score_details_font.render(f"Score: {score} - Highscore: {highscore}", True, 'White')

        # Every 4 apples, add a bomb
        if(score % 4 == 0):
            AddBomb()
    
    # Collisions with bombs
    collidedBomb = pygame.sprite.spritecollideany(player.sprite, bombs, collided=pygame.sprite.collide_circle)
    if bombs and collidedBomb:
        player.sprite.onDeath(elapsedTime)
        player.sprite.explode()
        collidedBomb.explode()

    # Collisions with body
    elif pygame.sprite.spritecollideany(player.sprite, playerBody, collided=pygame.sprite.collide_circle) and player_invulnerability < 0:
        player.sprite.onDeath(0)

    # Collisions with window borders
    if(player.sprite.pos.x > width - 10 or player.sprite.pos.x < -10 or player.sprite.pos.y > height - 10 or player.sprite.pos.y < -10):
        player.sprite.onDeath(0)

# Game loop
def game(elapsedTime, dt):
    global player_invulnerability, paused, transitioning, transitionRadius, transitionForward, player

    if transitioning:
        screen.blit(bg, (0, 0))
        screen.blit(score_text, score_text.get_rect(center = (width/2,height/2 + sin(elapsedTime * 30) * 8 + 30)))
        apple.draw(screen)
        player.draw(screen)

        for button in gameButtons:
            button.update()
            button.draw()

        # Transition from and to menu
        transitionRadius -= 1500 * dt if transitionForward else -2000 * dt
        if transitionRadius <= 0:
            transitioning = False
            transitionRadius = 0
        elif transitionRadius >= width * 1.1:
            transitionRadius = width
            ToMenu()
        pygame.draw.circle(screen, '#5fd038', (player.sprite.pos.x, player.sprite.pos.y), transitionRadius, 0)

    else:
        if not paused:
            player_invulnerability -= dt
            
            screen.blit(bg, (0,0))

            player.update(dt)
            if not player.sprite.dead:
                checkCollisions(elapsedTime)
                screen.blit(score_text, score_text.get_rect(center = (width/2,height/2 + sin(elapsedTime * 5) * 8 + 30)))

            apple.update(dt, elapsedTime)
            apple.draw(screen)

            bombs.update(elapsedTime, dt)
            bombs.draw(screen)

            playerBody.draw(screen)
            player.draw(screen)

            if player.sprite.dead and (elapsedTime - player.sprite.timeOfDeath >= 1):
                screen.blit(game_over_text, game_over_text.get_rect(center = (width/2,height/2 - 150)))
                screen.blit(score_details_text, score_details_text.get_rect(center = (width/2,height/2 - 40)))

                for button in gameOverButtons:
                    button.update()
                    button.draw()

        if not player.sprite.dead:
            for button in gameButtons:
                button.update()
                button.draw()
            
            if paused:
                screen.blit(paused_text, paused_text.get_rect(center = (width/2,height/2 - 150)))

                for button in gameOverButtons:
                    button.update()
                    button.draw()

# Menu loop
def menu(elapsedTime, dt):
    global transitionRadius, transitioning, inGame, menu_switch_ignore, transitionForward

    # Scrolling background
    offset = (elapsedTime * -30) % 256 - 256
    screen.blit(bg, (offset, offset))

    screen.blit(logoimg, logo.get_rect(center = (width/2,height/2 - 100)))

    player.update(dt)
    playerBody.draw(screen)
    player.draw(screen)

    for button in menuButtons:
        button.update()
        button.draw()

    # Transition from and to game
    if transitioning:
        pygame.draw.circle(screen, '#5fd038', (player.sprite.pos.x, player.sprite.pos.y), transitionRadius, 0)
        transitionRadius += 2000 * dt if transitionForward else -1500 * dt
        if transitionRadius > width * 1.1:
            transitionRadius = width
            StartGame()
        elif transitionRadius < 0:
            transitionRadius = 0
            transitioning = False
            menu_switch_ignore = False

# Main loop
while True:
    dt = clock.get_time() / 1000  # Delta-time since last update
    elapsedTime += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            QuitGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                QuitGame()

    if inGame:
        game(elapsedTime, dt)
    else:
        menu(elapsedTime, dt)
    
    pygame.display.update()
    clock.tick(60)