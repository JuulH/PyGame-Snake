from math import sqrt, acos
from turtle import back
import pygame
from sys import exit
import random
import asyncio

from utils import *

# https://www.youtube.com/watch?v=AY9MnQ4x3zk Tutorial gebruikt voor PyGame

# Instellingen voor scherm
width = 1280
height = 720
margin = 50 # Rand waar geen upgrades kunnen spawnen

pygame.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Snake')
clock = pygame.time.Clock()

global player_dead
player_dead = False

global scale
scale = 2

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
        self.mvmtSpeed = 5
        self.mouseInfluence = .1
    def resize(self, r_scale):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (self.size[0]*r_scale, self.size[1]*r_scale))
        self.rect = self.image.get_rect(center = (width/2,height/2))
    def update(self):
        x,y = pygame.mouse.get_pos()
        mousePos = Vector2(x,y)
        mouseDir = (self.pos - mousePos).normalize()
        self.dir = (self.pos - self.oldPos).normalize() # Verschil tussen oude en nieuwe positie genormaliseerd
        self.newDir = Vector2.lerp(self.dir,-mouseDir,self.mouseInfluence) * self.mvmtSpeed
        #self.pos += self.dir
        #self.pos += -mouseDir + self.dir
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        #self.image = pygame.transform.rotate(self.originalImage, Vector2.Angle(self.pos,mousePos))
        #self.rect = self.image.get_rect(center=self.rect.center)
        #print(str(self.pos) + ' - ' + str(mousePos) + ' - ' + str((Vector2.Angle(Vector2(0,1),mousePos))))
        
        #v1 = pygame.math.Vector2(20, 20)
        #v2 = pygame.math.Vector2(mousePos.x, mousePos.y)
        #print(v1.angle_to(v2))

playerBody = pygame.sprite.LayeredUpdates()

player = pygame.sprite.GroupSingle()
player.add(Player())



background = pygame.Surface((width,height))
background.fill('Gray')

global score
score = 0
score_font = pygame.font.Font(None, 200)
score_text = score_font.render(str(score), False, 'Dark Gray')

global dt
global player_invulnerability
player_invulnerability = 0



while True:
    dt = clock.get_rawtime() / 100
    player_invulnerability -= dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    screen.blit(background, (0,0))
    
    screen.blit(score_text, score_text.get_rect(center = (width/2,height/2)))
    player.draw(screen)
    player.update()
    pygame.display.update()
    clock.tick(60)