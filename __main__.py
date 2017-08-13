import pygame
import logging
import random
import string
from style import style
from pprint import pprint

# Configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Program parameters
target_population = 100

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode(style['main_window_size'])
pygame.display.set_caption('Evolution Simulator')

# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

class Creature:
    def __init__(self, name):
        self.pos = {'x':0,'y':0}
        self.name = name

def get_name():
    name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
    return name

def print_creatures():
    for creature in creatures:
        pprint(vars(creature))

def setup():
    global creatures

    creatures = []
    for i in range(0,target_population):
        new_creature_name = get_name()
        creatures.append(Creature(new_creature_name))

    print_creatures()

def logic():
    pass

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
