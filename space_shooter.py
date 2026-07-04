import pygame
from os.path import join
from random import *

pygame.init()

class Player(pygame.sprite.Sprite):
    def __init__(self,groups):

        super().__init__(groups)
        self.image = pygame.image.load(join("images","player.png")).convert_alpha()
        self.rect = self.image.get_frect(center=(WIDTH/2,HEIGHT/2))
        self.direction = pygame.math.Vector2()
        self.speed=300

        #cooldown timer

        self.can_shoot=True
        self.laser_time=0
        self.cooldown=400

    def laser_timer(self):
        if not self.can_shoot:
            current_time=pygame.time.get_ticks()
            if current_time - self.laser_time >= self.cooldown:
                self.can_shoot=True


    def update(self,dt):

        keys=pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction*self.speed*dt


        recent_keys=pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot :
            Laser(laser_surf,player.rect.midtop,(all_sprites,laser_sprites))
            self.can_shoot=False
            self.laser_time = pygame.time.get_ticks()
            laser_sound.play()
        self.laser_timer()

class Star(pygame.sprite.Sprite):

    def __init__(self, groups,surf):
        super().__init__(groups)

        self.image=surf
        self.rect= self.image.get_frect(center=(randint(0,WIDTH),randint(0,HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)

        self.image=surf
        self.rect=self.image.get_frect(midbottom=pos)

    def update(self,dt):
        self.rect.centery -= 400*dt

        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self , surf, pos, groups):
        super().__init__(groups)
        self.original_surf=surf
        self.image=surf
        self.rect=self.image.get_frect(center=pos)
        self.direction=pygame.math.Vector2(uniform(0.5,-0.5),1)
        self.speed=300
        self.rotation_Speed=randint(40,80)
        self.rotation_angle=0

    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt 
        if self.rect.top > HEIGHT:
            self.kill()
        
        self.rotation_angle += self.rotation_Speed * dt
        self.image=pygame.transform.rotate(self.original_surf,self.rotation_angle)
        self.rect=self.image.get_frect(center=self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames , pos , groups):
        super().__init__(groups)
        self.frames=frames
        self.frame_index= 0
        self.image = self.frames[self.frame_index]
        self.rect=self.image.get_frect(center=pos)        
                      
    def update(self,dt):
        self.frame_index += 100 * dt 

        if self.frame_index < len(self.frames):

            self.image=self.frames[int(self.frame_index)]
        
        else:
            self.kill()


def collisions():
    global running

    metor_collision=pygame.sprite.spritecollide(player,meteor_sprites,True,pygame.sprite.collide_mask)
    
    if metor_collision:
        running=False

    for laser in laser_sprites:
        laser_collision =pygame.sprite.spritecollide(laser,meteor_sprites,True)
        if laser_collision:
            laser.kill()
            AnimatedExplosion(explosion_frames,laser.rect.midtop,all_sprites)
            explosion_sound.play()

def score_display():
    current_time=pygame.time.get_ticks() //100
    font_surf=font.render(str(current_time),True,(240,240,240))
    font_rect=font_surf.get_frect(midbottom=(WIDTH//2,HEIGHT-50))
    display_surface.blit(font_surf,font_rect)

    pygame.draw.rect(display_surface,(240,240,240),font_rect.inflate(20,10).move(0,-10),5,10)

 #General setup

WIDTH,HEIGHT=1280,720
display_surface=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("SPACE SHOOTER")
clock=pygame.time.Clock()

#IMPORTS

meteor_surf=pygame.image.load(join("images","meteor.png")).convert_alpha()

laser_surf=pygame.image.load(join("images","laser.png")).convert_alpha()

star_surf=pygame.image.load(join("images",'star.png'))

font=pygame.font.Font(join("images","Oxanium-Bold.ttf"),40)

explosion_frames = [pygame.image.load(join("images","explosion",f"{i}.png")).convert_alpha() for i in range(21)]

# Sounds imports
laser_sound=pygame.mixer.Sound(join("audio","laser.wav"))
laser_sound.set_volume(0.5)

explosion_sound=pygame.mixer.Sound(join("audio","explosion.wav"))

game_sound=pygame.mixer.Sound(join("audio","game_music.wav"))
game_sound.play()

#groups and objects

all_sprites=pygame.sprite.Group()

meteor_sprites=pygame.sprite.Group()

laser_sprites=pygame.sprite.Group()

for i in range(20):
    star=Star(all_sprites,star_surf)

player= Player(all_sprites)

# custom event
meteor_event=pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)

running=True
while running:
    dt=clock.tick()/1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running= False
        
        if event.type == meteor_event:
            x,y=randint(0,WIDTH),randint(-200,-100)
            Meteor(meteor_surf,(x,y),(all_sprites,meteor_sprites))

    #draw the game

    all_sprites.update(dt)
    collisions()

    display_surface.fill("#3a2e3f")
    score_display()
    all_sprites.draw(display_surface)
    
    pygame.display.update()
pygame.quit()
