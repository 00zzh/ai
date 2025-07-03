import pygame as pg
import pymunk as pm
import pymunk.pygame_util as pu
import sys
import math
from pymunk import Vec2d

screen = pg.display.set_mode((600, 600))

space = pm.Space()

space.gravity = (0, 600)

points = [(-8,-8),(-8,8),(8,8),(8,-8)]

def new(pos):
    body = pm.Body(1,2000)
    body.position = (pos)
    rect = pm.Poly(body,points)
    rect.friction = 1
    space.add(body,rect)
 
def main():
    global draw_options
    ground = pm.Segment(space.static_body, (0, 500), (600, 500), 3)
    ground.friction = 1
    space.add(ground)
    draw_options = pu.DrawOptions(screen)
    for i in range(50,450,17):
        for j in range(150,250,17):
            new((i,j))

def draw():
    screen.fill((0,0,0))
    space.debug_draw(draw_options)
    space.step(1/60)
    pg.display.update()

def dis(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
 
def click():
    if pg.mouse.get_pressed()[0]:
        mPos = pg.mouse.get_pos()
        new(mPos)

fps = pg.time.Clock()

main()
while True:
    fps.tick(69)
    event = pg.event.poll()
    if event.type==pg.QUIT:
        pg.quit()
        sys.exit()

    if pg.mouse.get_pressed()[2]:
        space.remove(*space.bodies)
        space.remove(*space.shapes)
        main()

    kk=pg.key.get_pressed()
    if kk[pg.K_RIGHT]:
        space.gravity.remove()
    if kk[pg.K_LEFT]:
        space.gravity={-300,600}

    draw()
    click()