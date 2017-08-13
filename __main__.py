import pygame
import logging
import random
import string
import math
from style import style
from pprint import pprint

# Configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Program parameters
target_population = 30

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode(style['main_window_size'])
pygame.display.set_caption('Evolution Simulator')

# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

class Creature:
    max_speed = 4
    max_rspeed = 10

    def __init__(self, name):
        self.pos = (
            random.uniform(
                bounding_rect.left,
                bounding_rect.left + bounding_rect.width
            ),
            random.uniform(
                bounding_rect.top,
                bounding_rect.top + bounding_rect.height
            ),
        )
        self.name = name
        color = pygame.Color(0,0,0)
        color.hsva = (
            (random.randint(0,240)+180)%360,
            random.randint(20,100),
            random.randint(40,100)
        )
        self.color = color

        self.speed = 1.0
        self.rspeed = 0.0
        self.angle = 0.0

def get_name():
    name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
    return name

def print_creatures():
    for creature in creatures:
        pprint(vars(creature))

def setup():
    global creatures
    global bounding_rect

    bounding_rect = pygame.Rect(
        style['sim_panel'].left + style['creature']['radius'],
        style['sim_panel'].top + style['creature']['radius'],
        style['sim_panel'].width - (style['creature']['radius'] * 2),
        style['sim_panel'].height - (style['creature']['radius'] * 2)
    )

    creatures = []
    for i in range(0,target_population):
        new_creature_name = get_name()
        creatures.append(Creature(new_creature_name))

    target_pos = (
        random.randint(
            bounding_rect.left,
            bounding_rect.left + bounding_rect.width
        ),
        random.randint(
            bounding_rect.top,
            bounding_rect.top + bounding_rect.height
        )
    )

    sim_state = 'GEN_DONE'

def logic():
    # Update creature positions
    for creature in creatures:
        creature.angle = creature.angle + (creature.rspeed * creature.max_rspeed)
        creature.angle = creature.angle % (math.pi * 2)



        newpos = (
            min(
                max(
                    creature.pos[0] + (creature.speed * creature.max_speed * math.cos(creature.angle)),
                    bounding_rect.left
                ),
                bounding_rect.left + bounding_rect.width
            ),
            min(
                max(
                    creature.pos[1] + (creature.speed * creature.max_speed * math.sin(creature.angle)),
                    bounding_rect.top
                ),
                bounding_rect.top + bounding_rect.height
            )
        )

        creature.pos = newpos

def draw():
    #Flush background colour
    screen.fill(style['background_color'])

    # Draw sim panel
    screen.fill(
        style['panel_color'],
        style['sim_panel']
    )

    # Draw side panel
    screen.fill(
        style['panel_color'],
        style['side_panel']
    )

    # Draw creatures
    for creature in creatures:
        pygame.draw.circle(
            screen,
            creature.color,
            (int(creature.pos[0]), int(creature.pos[1])),
            style['creature']['radius']
        )

        hsv = (
            creature.color.hsva[0],
            creature.color.hsva[1],
            max(creature.color.hsva[2] - 40,0)
        )

        border_color = pygame.Color(0,0,0,0)
        border_color.hsva = hsv

        pygame.draw.circle(
            screen,
            border_color,
            (int(creature.pos[0]), int(creature.pos[1])),
            style['creature']['radius'],
            2
        )

        name_text_surface = style['creature']['name_font'].render(
            creature.name, True, style['black']
        )

        screen.blit(
            name_text_surface,
            (creature.pos[0] - (name_text_surface.get_width() / 2),
            creature.pos[1] - (name_text_surface.get_height() / 2) + style['creature']['name_font_spacing'])
        )

    pygame.display.flip()
    clock.tick(60)

setup()

# -------- Main Program Loop -----------
while carryOn:
    # --- Main event loop
    try:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                carryOn = False  # Flag that we are done so we exit this loop
    except:
        log.debug('Can\'t get events, video system not initialised')

    logic()
    draw()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()
