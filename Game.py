import pygame
from pygame.math import Vector2
import pytmx
pygame.init()
w=700
h=500
screen=pygame.display.set_mode((w,h))
pygame.display.set_caption("game_1")
clock=pygame.time.Clock()
running=True
class Player (pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.idle=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Idle.png",11)
        self.run=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Run.png",12)
        self.jump=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Jump.png",1)
        self.fall=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Fall.png",1)
        self.hit=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Hit.png",7)
        self.double_jump=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Double_Jump.png",6)
        self.wall_jump=self.load_frames(r"C:\Users\master\Desktop\game\assets\1 Main Characters\2\Wall_Jump.png",5)
        
        self.current_state=self.idle
        self.current_frame=0
        self.image=self.current_state[self.current_frame]
        self.rect=self.image.get_rect(center=(x,y))
        self.animation_speed=20
        self.animation_index=0
        self.facing_right=True
        self.y_velocity=0
        self.gravity=0.5
        self.jump_power=-10
        self.on_ground=False
        self.x_velocity=0
        self.max_speed=7
        self.acceleration=0.5
        self.friction=0.2
    def motion(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_velocity-=self.acceleration
            self.facing_right=False
        elif keys[pygame.K_RIGHT]:
            self.x_velocity+=self.acceleration 
            self.facing_right=True
        else:
            if self.x_velocity>0: #لليمين
                self.x_velocity-=self.friction
                if self.x_velocity<0:
                    self.x_velocity=0
            elif self.x_velocity<0: #للشمال
                self.x_velocity+=self.friction
                if self.x_velocity>0:
                    self.x_velocity=0
        if keys[pygame.K_SPACE] and self.on_ground:
            self.y_velocity=self.jump_power
            self.on_ground=False
        if self.x_velocity>self.max_speed:
            self.x_velocity=self.max_speed
        if self.x_velocity<-self.max_speed:
            self.x_velocity=-self.max_speed
 
    def apply_gravity(self):
        self.y_velocity+=self.gravity
        self.rect.y+= self.y_velocity
    def vertical_collision(self,tiles):
        self.apply_gravity()
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.y_velocity>0:
                   self.rect.bottom=tile.rect.top
                   self.y_velocity=0
                   self.on_ground=True
                elif self.y_velocity<0:
                    self.rect.top=tile.rect.bottom
                    self.y_velocity=0
    def horizontal_collision(self,tiles):
        self.rect.x+=self.x_velocity
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.x_velocity>0:
                    self.rect.right=tile.rect.left
                if self.x_velocity<0:
                    self.rect.left=tile.rect.right    
                self.x_velocity=0
    def load_frames(self,image_path,cols):
        sheet=pygame.image.load(image_path).convert_alpha()   
        sheet_w,sheet_h=sheet.get_size()      
        frame_w=sheet_w//cols
        frame_h=sheet_h
        frames=[]
        for col in range(cols):
            frame=sheet.subsurface(pygame.Rect(col*frame_w,0,frame_w,frame_h)).copy()
            frame=pygame.transform.smoothscale(frame,(60,60))
            frames.append(frame)
        return frames
    def update(self,tiles,dt):
        self.motion()
        self.vertical_collision(tiles)
        self.horizontal_collision(tiles)
        if self.y_velocity>0 and not self.on_ground:
            self.current_state=self.fall
        elif self.y_velocity<0:
            self.current_state=self.jump
        elif self.x_velocity!=0 and self.on_ground :
            self.current_state=self.run
        else:
            self.current_state=self.idle
        self.animation_index +=self.animation_speed*dt
        if self.animation_index>=len(self.current_state):
            self.animation_index=0
        self.current_frame=int(self.animation_index)
        frame=self.current_state[self.current_frame]
        if self.facing_right:
            self.image=frame
        else:
            self.image=pygame.transform.flip(frame,True,False)
class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,image):
        super().__init__()
        self.image=image
        self.rect=self.image.get_rect(center=pos)
class Camera():
    def __init__(self,screen_size,map_size):
        self.sw,self.sh=screen_size
        self.mw,self.mh=map_size
        self.offset=Vector2(0,0)
    def update(self,target_rect):
        desired_x=target_rect.centerx-self.sw//2
        desired_y=target_rect.centery-self.sh//2
        desired_x=max(0,min(desired_x,self.mw-self.sw))
        desired_y=max(0,min(desired_y,self.mh-self.sh))
        self.offset.update(desired_x,desired_y)
    def apply(self,p_r):
        if isinstance(p_r,pygame.Rect):
            return p_r.move(-self.offset.x,-self.offset.y)
        else:
            return(p_r[0]-self.offset.x,p_r[1]-self.offset.y)
data= pytmx.load_pygame(r"C:\Users\master\Desktop\game\map.tmx")
tile_width=data.tilewidth
tile_height=data.tileheight
tile_sprites=pygame.sprite.Group()
Scale=2
map_width=data.width*tile_width*Scale
map_height=data.height*tile_height*Scale
camera=Camera((w,h),(map_width,map_height))
for layer in data.visible_layers:
    if isinstance(layer,pytmx.TiledTileLayer):
        for x,y,tile in layer.tiles():
            image=pygame.transform.scale(tile,(tile_width*Scale,tile_height*Scale))
            pos=(x*tile_width*Scale,y*tile_height*Scale)
            if tile:
                tile_obj=Tile(pos,image)
                tile_sprites.add(tile_obj)
                
pl=Player(80,30)
pl.image
pl_sprites=pygame.sprite.Group(pl)
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    screen.fill("gray")  
    dt=clock.tick(60)/1000
    pl_sprites.update(tile_sprites,dt)
    camera.update(pl.rect)
    for t in tile_sprites:
        screen.blit(t.image,camera.apply(t.rect))
    for p in pl_sprites:
        screen.blit(p.image,camera.apply(p.rect))

    pygame.display.update()
    clock.tick(60)
pygame.quit()
              

              
