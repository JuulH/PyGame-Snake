from math import sqrt, acos, sin
import pygame
from sys import exit
import random
#import asyncio

# Some functions and classes are imported for clarity
from utils import *

# Save highscores
# https://www.youtube.com/watch?v=AY9MnQ4x3zk Tutorial used for PyGame

# Window setup
width = 1280
height = 720
margin = 75 # Border where items can't spawn

pygame.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Snake')
clock = pygame.time.Clock()

global player_dead
player_dead = False

global scale
scale = 3    # Global sprite scaling

sfx = True
sfx_channel = pygame.mixer.Channel(0)

highscore = 0
try:
    with open('highscore.txt', 'r') as f:
        highscore = int(f.read())
except:
    print('No highscores saved')
    with open('highscore.txt', 'w') as f:
        f.write('0')

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.originalImage = pygame.image.load('sprites/snake_head.png').convert_alpha()
        self.size = self.originalImage.get_size()
        self.originalImage = pygame.transform.scale(self.originalImage, (self.size[0]*scale, self.size[1]*scale))
        self.image = self.originalImage
        self.rect = self.image.get_rect(center = (width/2,height/2))
        self.pos = Vector2(self.rect.x, self.rect.y)
        self.oldPos = Vector2(self.pos.x - 1, self.pos.y)
        self.dir = Vector2.Zero()
        self.newDir = Vector2.Zero()
        self.mvmtSpeed = 6
        self.mouseInfluence = .11
        self.bodyParts = []
        self.partDistance = 14 * scale # Distance between two BodyPieces
        self.dead = False
        self.followMouse = True
        self.radius = self.rect.width / 2
        
        self.deathSound = pygame.mixer.Sound('audio/death3.wav')
        self.deathSound.set_volume(0.25)
    
    def reset(self):
        self.followMouse = False
        self.bodyParts = []
        playerBody.empty()
        self.rect = self.image.get_rect(center = (width/2,height/2))
        self.pos = Vector2(self.rect.x, self.rect.y)
        self.oldPos = Vector2(self.pos.x - 1, self.pos.y)
        self.dir = Vector2.Zero()
        self.newDir = Vector2.Zero()
        self.dead = False
        self.mvmtSpeed = 6

    def menu(self):
        self.followMouse = True
        self.rect = self.image.get_rect(center = (width/2,height/2))
        self.pos = Vector2(self.rect.x, self.rect.y)
        self.oldPos = Vector2(self.pos.x - 1, self.pos.y)
        self.dir = Vector2.Zero()
        self.newDir = Vector2.Zero()
        self.bodyParts = []
        playerBody.empty()
        for i in range(6):
            self.addPart()

    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center = (width/2,height/2))
    
    def addPart(self):
        part = self.BodyPiece() # New body instance
        self.bodyParts.append(part)
        playerBody.add(part, layer= 90 - len(self.bodyParts)) # Assign instance to spritelayer

        if len(self.bodyParts) > 1:
            prevPart = self.bodyParts[len(self.bodyParts) - 2]
            prevPart2 = self.bodyParts[len(self.bodyParts) - 3] if len(self.bodyParts) > 2 else self
            dir = (prevPart2.pos - prevPart.pos).normalize()
            part.pos = prevPart.pos - dir * self.partDistance
        else:
            part.pos = self.pos - self.dir * self.partDistance * 1.25

        self.mvmtSpeed += .2

    def onDeath(self):
        if not self.dead:
            self.mvmtSpeed = 0
            pygame.mixer.Channel(0).play(self.deathSound)
            #self.deathSound.play()
            pygame.mixer.music.fadeout(200)
            self.dead = True
    
    # Calculate position for each BodyPiece
    def simulateBody(self):
        for i, part in enumerate(self.bodyParts):
            prevPart = self.bodyParts[i - 1] if i > 0 else self
            dir = (prevPart.pos - part.pos).normalize() if prevPart is not self else (prevPart.pos - part.pos).normalize() * 1.25
            part.pos = prevPart.pos - dir * self.partDistance
            part.update()

    def update(self):
        x,y = pygame.mouse.get_pos()
        # if(pygame.mouse.get_pressed()[0]):
        #     self.addPart()
        # if(pygame.mouse.get_pressed()[2]):
        #     self.mvmtSpeed += .1
        mousePos = Vector2(x,y)
        mouseDir = (self.pos - mousePos).normalize()
        self.dir = (self.pos - self.oldPos).normalize() # Normalized direction between previous and current frame
        self.oldPos = self.pos
        self.newDir = Vector2.Lerp(self.dir,-mouseDir,self.mouseInfluence) * self.mvmtSpeed
        self.pos = self.pos + self.newDir if not self.followMouse else mousePos - Vector2(self.rect.width / 2, self.rect.height / 2)
        #self.pos += self.dir
        #self.pos += -mouseDir + self.dir
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        #self.image = pygame.transform.rotate(self.originalImage, Rad2Deg(Vector2.Angle(self.pos,self.dir)))
        #self.rect = self.image.get_rect(center=self.rect.center)
        #print(Rad2Deg(Vector2.Angle(self.pos,self.dir)))
        
        self.simulateBody()
    
    class BodyPiece(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.image.load('sprites/snake_body.png').convert_alpha()
            self.size = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (self.size[0]*scale, self.size[1]*scale))
            self.rect = self.image.get_rect(center = (width/2,height/2))
            self.pos = Vector2.Zero()
            self.radius = self.rect.width / 2
        
        def resize(self, r_scale):
            self.size = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
            self.rect = self.image.get_rect(center = (width/2,height/2))
        
        def update(self):
            self.rect.x = self.pos.x
            self.rect.y = self.pos.y

class Apple(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('sprites/apple.png').convert_alpha()
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*scale, self.size[1]*scale))
        self.rect = self.image.get_rect(center = (random.uniform(0 + margin, width - margin),random.uniform(0 + margin, height - margin)))
        self.newX, self.newY = self.rect.x, self.rect.y

        self.getSound = pygame.mixer.Sound('audio/appleGet.wav')
        self.getSound.set_volume(0.15)
    
    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center = (width/2,height/2))
    
    def replace(self):
        self.rect = self.image.get_rect(center = (random.uniform(0 + margin, width - margin),random.uniform(0 + margin, height - margin)))
        self.newX, self.newY = self.rect.x, self.rect.y
        pygame.mixer.Channel(0).play(self.getSound)
    
    def update(self, time):
        self.rect.y = self.newY + sin(time * 5) * 4


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
        self.image = self.spritesheet.subsurface((int(self.frame) * 16 * scale, 0, 16 * scale, 16 * scale))

    def explode(self):
        self.animating = True

    def replace(self):
        while True:
            self.rect = self.image.get_rect(center=(random.uniform(0 + margin, width - margin), random.uniform(0 + margin, height - margin)))
            if (abs(self.rect.x - player.sprite.rect.x) > 100 and abs(self.rect.y - player.sprite.rect.y) > 100) and (abs(self.rect.x - apple.sprite.rect.x) > 64 and abs(self.rect.y - apple.sprite.rect.y) > 64): break
        self.newX, self.newY = self.rect.x, self.rect.y

    def update(self, time, dt):
        
        if self.animating:
            self.animate(dt)
        else:
            self.rect.y = self.newY + sin(time * 5) * 4  # Sine wave animation

menu_switch_ignore = False

class Button():
    def __init__(self, x, y, inactive_image, active_image, scale, onClick, key = None):
        width = inactive_image.get_width()
        height = inactive_image.get_height()
        self.inactive_image = pygame.transform.scale(inactive_image, (width*scale, height*scale)).convert_alpha()
        self.active_image = pygame.transform.scale(active_image, (width*scale, height*scale)).convert_alpha()
        self.inactive_image.set_alpha(225)
        self.active_image.set_alpha(225)
        self.image = pygame.transform.scale(self.inactive_image, self.inactive_image.get_size()).convert_alpha()
        self.rect = self.image.get_rect(center = (x,y))
        self.mouseDown = False
        self.hover = False
        self.onClick = onClick
        self.btnOverlay = pygame.Surface((width*scale, height*scale))
        self.btnOverlay.set_alpha(0)
        self.btnOverlay.fill((0, 0, 0))
        self.toggleActive = False
        self.key = key
        self.ignoreMouse = False

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

        if pygame.mouse.get_pressed()[0]:
            if not self.rect.collidepoint(mousePos) or menu_switch_ignore:
                self.ignoreMouse = True
        else:
            self.ignoreMouse = False

        if ((self.rect.collidepoint(mousePos) and pygame.mouse.get_pressed()[0]) or (pygame.key.get_pressed()[self.key] if self.key else False)) and not self.ignoreMouse:
            self.btnOverlay.set_alpha(60) # Click effect
            if not self.mouseDown:
                pygame.mixer.Channel(0).play(self.clickSound)
                self.onClick()
                self.toggleActive = not self.toggleActive
                self.image = self.active_image if self.toggleActive else self.inactive_image
                self.mouseDown = True
        else:
            if self.mouseDown:
                self.mouseDown = False
                self.btnOverlay.set_alpha(0)
    
    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.btnOverlay, self.rect)

#player = pygame.sprite.Group()
#player = pygame.sprite.LayeredUpdates()
#player.add(Player(), layer = 99)
playerBody = pygame.sprite.LayeredUpdates()

player = pygame.sprite.GroupSingle()
player.add(Player())

apple = pygame.sprite.GroupSingle()
apple.add(Apple())

bombs = pygame.sprite.Group()

background = pygame.Surface((width,height))
background.fill('Gray')

font = 'sprites/Fonts/Square.ttf'

global score
score = 0
score_font = pygame.font.Font(font, 275)
score_text = score_font.render(str(score), True, 'White')

game_over_font = pygame.font.Font(font, 200)
game_over_text = game_over_font.render('Game Over', True, 'White')

score_details_font = pygame.font.Font(font, 50)
score_details_text = score_details_font.render(f"Score: {score} - Highscore: {highscore}", True, 'White')

paused_text = game_over_font.render('Paused', True, 'White')

bg = pygame.image.load("sprites/tilebgbig.png")
logoimg = pygame.image.load("sprites/snakelogo.png")
logoimg = pygame.transform.scale(logoimg, (logoimg.get_width()*3, logoimg.get_height()*3))
logo = pygame.Surface(logoimg.get_size())

global dt
global player_invulnerability
elapsedTime = 0
player_invulnerability = 0

#region Button controls
def ToggleMusic():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(100)
    else:
        pygame.mixer.music.play(-1, 0, 100)

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

music_button = Button(width - 50, height - 50, pygame.image.load('sprites/UI/musicbtn.png'), pygame.image.load('sprites/UI/disabledbtn.png'), 4, ToggleMusic, pygame.K_m)
sound_button = Button(width - 125, height - 50, pygame.image.load('sprites/UI/soundbtn.png'), pygame.image.load('sprites/UI/disabledbtn.png'), 4, ToggleSfx, pygame.K_n)
pause_button = Button(width - 200, height - 50, pygame.image.load('sprites/UI/pausebtn.png'), pygame.image.load('sprites/UI/resumebtn.png'), 4, TogglePause, pygame.K_SPACE)

gameButtons = [music_button, sound_button, pause_button]

inGame = False
transitioning = False
transitionForward = True

def OnPlay():
    global transitioning, transitionForward
    transitionForward = True
    transitioning = True

def StartGame():
    global inGame, score, player_invulnerability, elapsedTime, score_text, paused, score_details_text, transitioning

    player.sprite.reset()
    bombs.empty()

    pygame.mixer.music.play(-1, 0, 100)
    score = 0
    player_invulnerability = 0
    elapsedTime = 0
    score_text = score_font.render(str(score), True, 'White')
    score_details_text = score_details_font.render(f"Score: {score} - Highscore: {highscore}", True, 'White')

    pause_button.setActive(False)

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

    menu_switch_ignore = True
    inGame = False

play_button = Button(width/2, height/2 + 125, pygame.image.load('sprites/UI/playbtn.png'), pygame.image.load('sprites/UI/playbtn.png'), 5, OnPlay, pygame.K_RETURN)
quit_button = Button(width/2, height/2 + 250, pygame.image.load('sprites/UI/quitbtn.png'), pygame.image.load('sprites/UI/quitbtn.png'), 5, QuitGame, pygame.K_q)

menuButtons = [play_button, quit_button]

restart_button = Button(width/2, height/2 + 50, pygame.image.load('sprites/UI/playbtn.png'), pygame.image.load('sprites/UI/playbtn.png'), 5, StartGame, pygame.K_r)
menu_button = Button(width/2, height/2 + 150, pygame.image.load('sprites/UI/menubtn.png'), pygame.image.load('sprites/UI/menubtn.png'), 5, OnMenu, pygame.K_t)

gameOverButtons = [restart_button, menu_button, quit_button]

#endregion

# Check game collisions
def checkCollisions():
    global score, score_text, player_invulnerability, highscore, score_details_text
    
    # Collisions with apples
    if pygame.sprite.collide_rect(apple.sprite, player.sprite):
        apple.sprite.replace()
        player.sprite.addPart()
        for bomb in bombs.sprites():
            bomb.replace()
        score += 1
        score_text = score_font.render(str(score), True, 'White')

        player_invulnerability = 0

        if score > highscore:
            highscore = score
            with open("highscore.txt", "w") as f:
                f.write(str(highscore))

        score_details_text = score_details_font.render(f"Score: {score} - Highscore: {highscore}", True, 'White')

        if(score % 4 == 0):
            AddBomb()
    
    # Collisions with bombs
    collidedBomb = pygame.sprite.spritecollideany(player.sprite, bombs, collided=pygame.sprite.collide_circle)
    if bombs and collidedBomb:
        player.sprite.onDeath()
        collidedBomb.explode()

    # Collisions with body
    elif pygame.sprite.spritecollideany(player.sprite, playerBody, collided=pygame.sprite.collide_circle) and player_invulnerability < 0:
        player.sprite.onDeath()

    # Collisions with window borders
    if(player.sprite.pos.x > width - 10 or player.sprite.pos.x < 10 or player.sprite.pos.y > height - 10 or player.sprite.pos.y < 10):
        player.sprite.onDeath()

pygame.mixer.music.load('audio/music.wav')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)
pygame.mixer.Channel(0).set_volume(0.75)

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
            
            #screen.blit(background, (0,0))
            screen.blit(bg, (0,0))

            player.update()

            if not player.sprite.dead:
                checkCollisions()
                screen.blit(score_text, score_text.get_rect(center = (width/2,height/2 + sin(elapsedTime * 5) * 8 + 30)))

            apple.update(elapsedTime)
            apple.draw(screen)

            bombs.update(elapsedTime, dt)
            bombs.draw(screen)

            player.draw(screen)
            playerBody.draw(screen)

            if player.sprite.dead:
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

for i in range(6):
    player.sprite.addPart()


transitionRadius = 0

# Menu loop
def menu(elapsedTime, dt):
    global transitionRadius, transitioning, inGame, menu_switch_ignore, transitionForward

    offset = (elapsedTime * -40) % 256 - 256 # Scrolling background
    screen.blit(bg, (offset, offset))

    screen.blit(logoimg, logo.get_rect(center = (width/2,height/2 - 100)))

    player.update()
    player.draw(screen)
    playerBody.draw(screen)

    for button in menuButtons:
        button.update()
        button.draw()

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
    