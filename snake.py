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
            prevPart2 = self.bodyParts[len(self.bodyParts) - 3]
            dir = (prevPart2.pos - prevPart.pos).normalize()
            part.pos = prevPart.pos - dir * self.partDistance
        else:
            part.pos = self.pos - self.dir * self.partDistance * 1.75

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
            #dir = (prevPart.pos - part.pos).normalize()
            #dir = (prevPart.pos - part.pos).normalize() if prevPart is not self else Vector2.Lerp(self.dir,-mouseDir,self.mouseInfluence) * self.partDistance# is dit beter?
            #dir = (prevPart.pos - part.pos).normalize() if prevPart is not self else (self.pos - self.oldPos).normalize() * self.partDistance # is dit beter?
            #dir = (prevPart.pos - part.pos).normalize() if prevPart is not self else self.dir * 2 # is dit beter?
            dir = (prevPart.pos - part.pos).normalize() if prevPart is not self else (prevPart.pos - part.pos).normalize() * 1.75
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
        self.rect.y = self.newY + sin(time * 30) * 4


class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame = 0
        self.animating = False
        self.spritesheet = pygame.image.load('sprites/bombsprites.png').convert_alpha()
        self.size = self.spritesheet.get_size()
        self.spritesheet = pygame.transform.scale(self.spritesheet, (self.size[0]*scale, self.size[1]*scale))
        self.image = self.spritesheet.subsurface((0, 0, 16 * scale, 16 * scale))
        self.rect = self.image.get_rect(center=(random.uniform(0 + margin, width - margin), random.uniform(0 + margin, height - margin)))
        self.newX, self.newY = self.rect.x, self.rect.y
        self.getSound = pygame.mixer.Sound('audio/bomb.wav')
        self.getSound.set_volume(0.15)
        self.replace()

    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center=(width/2, height/2))

    def animate(self, dt):
        if self.frame < 7:
            self.frame += dt * 100
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
            self.rect.y = self.newY + sin(time * 30) * 4  # Sine wave animation

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

        self.clickSound = pygame.mixer.Sound('audio/click.wav')
        self.hoverSound = pygame.mixer.Sound('audio/hover.wav')
        self.clickSound.set_volume(0.35)
        self.hoverSound.set_volume(0.35)
    
    def update(self):
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

        if (self.rect.collidepoint(mousePos) and pygame.mouse.get_pressed()[0]) or (pygame.key.get_pressed()[self.key] if self.key else False):
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

global score
score = 0
score_font = pygame.font.Font(None, 300)
score_text = score_font.render(str(score), False, 'White')

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

def StartGame():
    global inGame

    player.sprite.reset()

    inGame = True

def QuitGame():
    pygame.quit()
    exit()

play_button = Button(width/2, height/2 + 100, pygame.image.load('sprites/UI/playbtn.png'), pygame.image.load('sprites/UI/playbtn.png'), 5, StartGame)
quit_button = Button(width/2, height/2 + 250, pygame.image.load('sprites/UI/quitbtn.png'), pygame.image.load('sprites/UI/quitbtn.png'), 5, QuitGame)

menuButtons = [play_button, quit_button]

#endregion

# Check game collisions
def checkCollisions():
    global score, score_text, player_invulnerability, highscore
    
    # Collisions with apples
    if pygame.sprite.collide_rect(apple.sprite, player.sprite): # collide_circle?
        apple.sprite.replace()
        player.sprite.addPart()
        for bomb in bombs.sprites():
            bomb.replace()
        score += 1
        score_text = score_font.render(str(score), True, 'White')
        print(str(score))
        player_invulnerability = .1

        if score > highscore:
            highscore = score
            with open("highscore.txt", "w") as f:
                f.write(str(highscore))

        if(score % 5 == 0):
            AddBomb()
    
    # Collisions with bombs
    collidedBomb = pygame.sprite.spritecollideany(player.sprite, bombs)
    if bombs and collidedBomb:
        player.sprite.onDeath()
        collidedBomb.explode()

    # Collisions with body
    elif pygame.sprite.spritecollideany(player.sprite, playerBody) and player_invulnerability < 0:
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
    global player_invulnerability

    if not paused:
        player_invulnerability -= dt
        
        #screen.blit(background, (0,0))
        screen.blit(bg, (0,0))

        player.update()

        if player.sprite.alive:
            checkCollisions()

        screen.blit(score_text, score_text.get_rect(center = (width/2,height/2 + sin(elapsedTime * 30) * 8 + 30)))

        apple.update(elapsedTime)
        apple.draw(screen)

        bombs.update(elapsedTime, dt)
        bombs.draw(screen)

        player.draw(screen)
        playerBody.draw(screen)
    
    for button in gameButtons:
        button.update()
        button.draw()

for i in range(8):
    player.sprite.addPart()

# Menu loop
def menu(elapsedTime):

    offset = (elapsedTime * -100) % 256 - 256 # Scrolling background
    screen.blit(bg, (offset, offset))

    screen.blit(logoimg, logo.get_rect(center = (width/2,height/2 - 100)))

    player.update()
    player.draw(screen)
    playerBody.draw(screen)

    for button in menuButtons:
        button.update()
        button.draw()

# Main loop
while True:
    dt = clock.get_rawtime() / 1000  # Delta-time since last update
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
        menu(elapsedTime)
    
    pygame.display.update()
    clock.tick(60)
    