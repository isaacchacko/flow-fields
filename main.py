#!/usr/bin/env python2

import os 
import math
import pygame
import random
from perlin_noise import PerlinNoise

WIDTH = 1600
HEIGHT = 900
FPS = 0
BALL_COUNT = 1
HEADLESS = True
VISUALIZATION = 'TRACE_PATH' # TRACE_PATH
SHOW_VECTOR_FIELD = False
VECTOR_SCALE = 10
MAX_SPEED = 5
BALL_DESPAWN_TOLERANCE = 0

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# set vector field 
noise = PerlinNoise(octaves = 10, seed = random.random()*1000)
# noise = lambda a: random.random() * 2 * math.pi
points = [[x * 20, y * 20] for x in range(WIDTH//20) for y in range(HEIGHT//20)]
vectors = [[math.cos(noise([x/WIDTH, y/HEIGHT]) * 2 * math.pi), math.sin(noise([x/WIDTH, y/HEIGHT]) * 2 * math.pi)] for [x, y] in points]
vector_lines = [[[x, y], [x + VECTOR_SCALE * dx, y + VECTOR_SCALE * dy]] for ([x, y], [dx, dy]) in zip(points, vectors)]

dxsum = sum([v[0] for v in vectors])
dysum = sum([v[1] for v in vectors])
print(f'Average Vector: <{dxsum / len(vectors)}, {dysum / len(vectors)}>')
next_ball_id = 0
balls = [[0, random.random() * HEIGHT, 0, 0, next_ball_id + i] for i in range(BALL_COUNT)]
next_ball_id += BALL_COUNT

if VISUALIZATION in ['HEATMAP', 'TRACE_PATH']: ball_paths = [[] for _ in range(BALL_COUNT)]

if VISUALIZATION == 'HEATMAP': 
    max_heat = 0
    heatmap = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]
    trace_window = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    trace_window.set_colorkey((0, 0, 0))

## group all the sprites together for ease of update
all_sprites = pygame.sprite.Group()

## Game loop
running = True
while running:
    pygame.display.set_caption(f"flow fields - {clock.get_fps()}")
    
    #1 Process input/events
    MAX_SPEED = 1 * clock.tick(FPS)     ## will make the loop run at the same speed all the time
    for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False


    #2 Update
    all_sprites.update()
    for ball in balls:
        if VISUALIZATION == "TRACE_PATH": ball_paths[ball[-1]].append(ball[:2])

        dx = ball[0] - points[0][0]
        dy = ball[1] - points[0][1]
        closest_vector_dist = dx*dx + dy*dy
        closest_vector = vectors[0]
        closest_vector_index = 0
        for index, point in enumerate(points[1:]):
            dx = ball[0] - point[0]
            dy = ball[1] - point[1]
            dist = dx*dx + dy*dy
            if closest_vector_dist > dist:
                closest_vector_dist = dist
                closest_vector = vectors[index + 1]
                closest_vector_index = index + 1
 
        ball[2] += (closest_vector[0] * VECTOR_SCALE)
        ball[3] += (closest_vector[1] * VECTOR_SCALE)
        
        
        ball[2] = -MAX_SPEED if ball[2] < -MAX_SPEED else MAX_SPEED if ball[2] > MAX_SPEED else ball[2]
        ball[3] = -MAX_SPEED if ball[3] < -MAX_SPEED else MAX_SPEED if ball[3] > MAX_SPEED else ball[3]
 
        ball[0] += ball[2]
        ball[1] += ball[3]

    for i in range(len(balls)):
        ball = balls[i]
        if ball[0] < -BALL_DESPAWN_TOLERANCE or ball[0] > WIDTH + BALL_DESPAWN_TOLERANCE or ball[1] < -BALL_DESPAWN_TOLERANCE or ball[1] > HEIGHT + BALL_DESPAWN_TOLERANCE:
            balls[i] = [0, random.random() * HEIGHT, 0, 0, next_ball_id]
            if VISUALIZATION == "TRACE_PATH": ball_paths.append([])
            next_ball_id += 1

    #3 Draw/render
    screen.fill(BLACK)

    

    all_sprites.draw(screen)
    if SHOW_VECTOR_FIELD:
        for line in vector_lines:
            pygame.draw.line(screen, (255, 255, 255), line[0], line[1])
            pygame.draw.circle(screen, (0, 255, 0), line[1], 1)


    if VISUALIZATION == 'TRACE_PATH':
        for path in ball_paths:
            path_length = len(path)
            if path_length >= 2:
                for start, end in zip(path[:-1], path[1:]):
                    pygame.draw.line(screen, (start[1]/HEIGHT * 255, 0, (HEIGHT - start[1])/HEIGHT * 255), start, end)

    if next_ball_id > 200:
        pygame.image.save(screen, 'product.png')
        running = False
    
    else:
        for ball in balls:
            pygame.draw.circle(screen, (255, 255, 0), ball[:2], 3)
        
    if not HEADLESS:
        pygame.display.flip()       

pygame.quit()
os.system("notify-send FieldDraw Complete!")