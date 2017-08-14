import pygame
import logging
import random
import string
import math
import copy
from style import style
from pprint import pprint
import brain

# Configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Program parameters
target_population = 100
killed_per_gen = 10
ticks_per_gen = 900
auto_gen = True
frameskip = 1

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode(style['main_window_size'])
pygame.display.set_caption('Evolution Simulator')

# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
sim_state = 'RESET'

def dist(x1,y1,x2,y2):
    return math.hypot(x2-x1,y2-y1)

class Creature:
    max_speed = 4
    max_rspeed = 1

    def __init__(self, name):
        self.reset()
        self.name = name
        color = pygame.Color(0,0,0)
        color.hsva = (
            (random.randint(0,240)+180)%360,
            random.randint(20,99),
            random.randint(40,99)
        )
        self.color = color
        self.brain = brain.Brain(self.name)

    def reset(self):
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
        self.speed = 0.0
        self.rspeed = 0.0
        self.angle = 0.0
        self.fitness = 0.0
        self.start_pos = self.pos

    def tick(self):
        output = self.brain.tick(
            self.speed / self.max_speed,
            self.angle / (math.pi*2),
            self.rspeed / self.max_rspeed,
            (self.pos[0]-target[0])/style['sim_panel'].width,
            (self.pos[1]-target[1])/style['sim_panel'].height
        )

        self.fitness = max(self.fitness,
            dist(self.start_pos[0], self.start_pos[1], target[0], target[1]) /
            dist(self.pos[0], self.pos[1], target[0], target[1])
        )

        self.speed = output['speed'] * self.max_speed
        self.rspeed = output['rspeed'] * self.max_rspeed

    def mutate(self):
        self.brain.mutate()

def get_name():
    name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
    return name

def get_clicked_object(pos):
    for creature in generations[-1]:
        x = dist(pos[0],pos[1],creature.pos[0],creature.pos[1])

        if dist(pos[0],pos[1],creature.pos[0],creature.pos[1]) < style['creature']['radius']:
            return creature

def sim_tick():
    global sim_time
    global sim_state
    global prev_state
    # Update creature positions
    for creature in generations[-1]:
        creature.tick()
        creature.angle = creature.angle + creature.rspeed
        while creature.angle > (math.pi * 2):
            creature.angle = creature.angle - (math.pi * 2)

        while creature.angle < -(math.pi * 2):
            creature.angle = creature.angle + (math.pi * 2)

        newpos = (
            min(
                max(
                    creature.pos[0] + (creature.speed * math.cos(creature.angle)),
                    bounding_rect.left
                ),
                bounding_rect.left + bounding_rect.width
            ),
            min(
                max(
                    creature.pos[1] + (creature.speed * math.sin(creature.angle)),
                    bounding_rect.top
                ),
                bounding_rect.top + bounding_rect.height
            )
        )

        creature.pos = newpos

    sim_time = sim_time + 1

    if sim_time > ticks_per_gen:
        if auto_gen:
            sim_state = 'GEN_DONE'
        else:
            prev_state = 'GEN_DONE'
            sim_state = 'PAUSED'

def create_generation():
    global sim_time
    global sim_state

    last_gen = generations[-1]

    for c in last_gen:
        if dist(c.pos[0],c.pos[1],c.start_pos[0],c.start_pos[1]) < 100:
            c.fitness = 0.0

    last_gen.sort(key=lambda c: c.fitness, reverse=True)

    new_gen = []

    for i in range(0, killed_per_gen):
        parent = last_gen[i]
        parent.mutate()
        parent.reset()
        new_gen.append(copy.deepcopy(parent))

    for i in range(0, target_population - killed_per_gen):
        creature = last_gen[i]
        creature.reset()
        new_gen.append(copy.deepcopy(creature))

    generations.append(new_gen)

    sim_time = 0
    sim_state = 'RUNNING'

def setup():
    global bounding_rect
    global target
    global selected_creature
    global info_text
    global generations
    global sim_time
    global sim_state

    selected_creature = None
    info_text = ''
    generations = []

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

    generations.append(creatures)

    # target = (
    #     random.randint(
    #         bounding_rect.left,
    #         bounding_rect.left + bounding_rect.width
    #     ),
    #     random.randint(
    #         bounding_rect.top,
    #         bounding_rect.top + bounding_rect.height
    #     )
    # )

    target = (((style['sim_panel'].left * 2) + style['sim_panel'].width) / 2,
        ((style['sim_panel'].left * 2) + style['sim_panel'].width) / 2)

    sim_time = 0
    sim_state = 'RUNNING'

def logic():
    if sim_state == 'GEN_DONE':
        create_generation()

    elif sim_state == 'RUNNING':
        sim_tick()

    elif sim_state == 'RESET':
        setup()

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

    # Draw target
    pygame.draw.circle(
        screen,
        style['highlight2'],
        (int(target[0]), int(target[1])),
        style['net_node_rad']
    )

    # Draw neural network display
    if selected_creature:
        sel_creature_name = style['side_creature_name_font'].render(
            selected_creature.name, True, style['black']
        )

        screen.blit(
            sel_creature_name,
            (style['net_display_area'].left+(style['net_display_area'].width/2)
                - (sel_creature_name.get_width()/2),
            style['side_panel'].top + style['side_creature_name_toppad'])
        )

        # Draw synapses
        layern = 0
        for layer in selected_creature.brain.layers:
            xpos = (style['net_display_area'].left
                    + (style['net_display_area'].width/2)
                    + (style['net_node_spacing'][0]*(layern-1)))
            n = 1
            for neuron in layer:
                ypos = style['net_display_area'].top + (style['net_node_spacing'][1]*n)

                m = 1
                for w in neuron.weights:
                    if layern == 0:
                        inputy = ypos
                    else:
                        inputy = style['net_display_area'].top + (style['net_node_spacing'][1]*m)
                    pygame.draw.line(
                        screen,
                        style['white'] if w > 0 else style['black'],
                        (xpos,ypos),
                        (
                            xpos-(style['net_node_spacing'][0]),
                            inputy
                        ),
                        int(abs(w)*2)
                    )
                    m=m+1
                n=n+1
            layern = layern+1

        labelxpos = (style['net_input_label'])

        # Draw labels on input
        value_text_surface = style['creature']['name_font'].render('Speed', True, style['black'])
        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*1))
        )

        value_text_surface = style['creature']['name_font'].render('Angle', True, style['black'])
        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*2))
        )
        value_text_surface = style['creature']['name_font'].render('RSpeed', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*3))
        )
        value_text_surface = style['creature']['name_font'].render('XDiff', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*4))
        )
        value_text_surface = style['creature']['name_font'].render('YDiff', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*5))
        )

        # Draw neurons
        layern = 0
        for layer in selected_creature.brain.layers:
            xpos = (style['net_display_area'].left
                    + (style['net_display_area'].width/2)
                    + (style['net_node_spacing'][0]*(layern-1)))

            n = 1
            for neuron in layer:
                ypos = style['net_display_area'].top + (style['net_node_spacing'][1]*n)
                sat = min(abs(neuron.value) * 100, 100)
                color = pygame.Color(style['highlight'][0], style['highlight'][1], style['highlight'][2])
                color.hsva = (color.hsva[0], sat, color.hsva[2])

                pygame.draw.circle(
                    screen,
                    color,
                    (int(xpos), int(ypos)),
                    style['net_node_rad']
                )

                value_text_surface = style['creature']['name_font'].render(
                    ('%.2f' % neuron.value), True, style['black']
                )

                screen.blit(
                    value_text_surface,
                    (xpos - (value_text_surface.get_width()/2),
                    ypos - (value_text_surface.get_height()/2))
                )

                n=n+1
            layern=layern+1


    # Draw creatures
    for creature in generations[-1]:
        pygame.draw.circle(
            screen,
            creature.color,
            (int(creature.pos[0]), int(creature.pos[1])),
            style['creature']['radius']
        )

        hsv = (
            creature.color.hsva[0],
            creature.color.hsva[1],
            min(max(creature.color.hsva[2] - 40,0),100)
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

    # Draw log text
    log_text = ('Generation: {} || Sim ticks: {} / {} || Sim state: {} || Population: {} || Autogen: {} || Skip: {}'.format(
        len(generations),
        sim_time,
        ticks_per_gen,
        sim_state,
        len(generations[-1]),
        auto_gen,
        frameskip
    ))

    log_text_surface = style['creature']['name_font'].render(
        log_text, True, style['black']
    )

    screen.blit(
        log_text_surface,
        (style['sim_panel'].left,
        style['sim_panel'].top)
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
            if event.type == pygame.MOUSEBUTTONUP:
                obj = get_clicked_object(pygame.mouse.get_pos())
                if obj:
                    selected_creature = obj
                else:
                    selected_creature = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if sim_state != 'PAUSED':
                        prev_state = sim_state
                        sim_state = 'PAUSED'
                        pprint(generations[-1])
                    else:
                        sim_state = prev_state
                if event.key == pygame.K_a:
                    if auto_gen:
                        auto_gen = False
                    else:
                        auto_gen = True
                if event.key == pygame.K_w:
                    frameskip = frameskip + 1
                if event.key == pygame.K_q:
                    frameskip = frameskip - 1

    except:
        log.debug('Can\'t get events, video system not initialised')

    for i in range(frameskip):
        logic()

    draw()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()
