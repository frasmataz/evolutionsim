import pygame
import logging
import random
import string
import math
import copy
import pickle
from concurrent.futures import ThreadPoolExecutor
from style import style
from pprint import pprint
import brain

# Configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Program parameters
generationspersave = 10
target_population = 60
killed_per_gen = 10
ticks_per_gen = 300
auto_gen = True
frameskip = 1
max_fitness_per_tick = 500
filename = 'creatures.pkl'

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
    max_rspeed = 0.3

    def __init__(self, name):
        random.seed(name)
        self.reset()
        self.name = name
        self.number = 0
        color = pygame.Color(0,0,0)
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
                bounding_rect.top + (bounding_rect.height)
            ),
        )
        self.speed = 0.0
        self.rspeed = 0.0
        self.angle = math.pi/2
        self.fitness = 0.0
        self.start_pos = self.pos

    def tick(self):
        output = self.brain.tick(
            self.speed / self.max_speed,
            math.sin(self.angle),
            math.cos(self.angle),
            self.rspeed / self.max_rspeed,
            (self.pos[0]-target[0])/style['sim_panel'].width,
            (self.pos[1]-target[1])/style['sim_panel'].height
        )

        progress = (dist(self.start_pos[0], self.start_pos[1], target[0], target[1]) /
            dist(self.pos[0], self.pos[1], target[0], target[1]) - 1)

        progress_sign = 1 if progress >= 0.0 else -1

        self.fitness = self.fitness + min((math.pow(progress,2)*progress_sign),max_fitness_per_tick)

        self.speed = max(0.0,output['speed']) * self.max_speed
        self.rspeed = output['rspeed'] * self.max_rspeed
        rgb = tuple([math.floor((x*128)+128) for x in output['rgb']])
        self.color = pygame.Color(rgb[0],rgb[1],rgb[2])

    def mutate(self):
        self.number  = self.number + 1
        self.brain.mutate()

def get_name():
    name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(2)])
    return name

def get_clicked_object(pos):
    for creature in generations[-1]:
        x = dist(pos[0],pos[1],creature.pos[0],creature.pos[1])

        if dist(pos[0],pos[1],creature.pos[0],creature.pos[1]) < style['creature']['radius']:
            return creature

def savecreatures(filename, creatures):
    with open(filename, 'wb') as output:
        pickle.dump(creatures, output, pickle.HIGHEST_PROTOCOL)

def loadcreatures(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

def update_creature(creature):
    # Update creature positions
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
    return creature.fitness


def create_generation():
    global sim_time
    global sim_state
    global target


    last_gen = generations[-1]

    last_gen.sort(key=lambda c: c.fitness, reverse=True)

    new_gen = []

    for i in range(0, killed_per_gen):
        parent = copy.deepcopy(last_gen[i])
        parent.mutate()
        parent.reset()
        new_gen.append(parent)

    for i in range(0, target_population - killed_per_gen):
        creature = copy.deepcopy(last_gen[i])
        creature.reset()
        new_gen.append(creature)

    generations.append(new_gen)

    if len(generations) % generationspersave == 0:
        savecreatures(filename,generations)

    target = (
        random.randint(
            bounding_rect.left,
            bounding_rect.left + bounding_rect.width
        ),
        random.randint(
            bounding_rect.top,
            bounding_rect.top + bounding_rect.height
        )
    )

    target = (bounding_rect.left + bounding_rect.width/2,bounding_rect.top + bounding_rect.height/2)

    sim_time = 0
    sim_state = 'RUNNING'

def interp(left_min, left_max, right_min, right_max):
    # Figure out how 'wide' each range is
    leftSpan = left_max - left_min
    rightSpan = right_max - right_min

    # Compute the scale factor between left and right values
    scaleFactor = float(rightSpan) / float(leftSpan)

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        if value > 0:
            value = math.sqrt(value)
        elif value < 0:
            value = -(math.sqrt(-value))
        return right_min + (value-left_min)*scaleFactor

    return interp_fn

def setup():
    global bounding_rect
    global target
    global selected_creature
    global info_text
    global generations
    global sim_time
    global sim_state
    global thread_pool
    global max_fitness

    selected_creature = None
    info_text = ''
    generations = []
    max_fitness = 0.0

    bounding_rect = pygame.Rect(
        style['sim_panel'].left + style['creature']['radius'],
        style['sim_panel'].top + style['creature']['radius'],
        style['sim_panel'].width - (style['creature']['radius'] * 2),
        style['sim_panel'].height - (style['creature']['radius'] * 2)
    )

    try:
        generations = loadcreatures(filename)
    except:
        creatures = []
        for i in range(0,target_population):
            new_creature_name = get_name()
            creatures.append(Creature(new_creature_name))

        generations.append(creatures)

    target = (0,0)

    thread_pool = ThreadPoolExecutor(max_workers=8)

    sim_time = 0
    sim_state = 'RUNNING'

def logic():
    global sim_time
    global sim_state
    global prev_state
    global max_fitness

    if sim_state == 'GEN_DONE':
        create_generation()

    elif sim_state == 'RUNNING':
        futures = []
        for creature in generations[-1]:
            futures.append(thread_pool.submit(update_creature, creature))
        for f in futures:
            fit = f.result(5.0)
            if fit > max_fitness:
                max_fitness = fit

        sim_time = sim_time + 1

        if sim_time > ticks_per_gen:
            if auto_gen:
                sim_state = 'GEN_DONE'
            else:
                prev_state = 'GEN_DONE'
                sim_state = 'PAUSED'

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

    # Draw trend_graph
    screen.fill(
        style['white'],
        style['trend_graph']
    )

    lastmax = (style['trend_graph'].left,style['trend_graph'].top+style['trend_graph'].height)
    lastmed = lastmax
    lastmin = lastmax

    i = 0

    scale = interp(0.0, math.sqrt(max(0.1,max_fitness)), 0.0, style['trend_graph'].height)

    for g in generations:
        g.sort(key=lambda c: c.fitness, reverse=True)
        maxfit = g[0].fitness
        medfit = g[math.floor(target_population/2)].fitness
        minfit = g[target_population-1].fitness

        xpos = style['trend_graph'].left + (
            (style['trend_graph'].width / len(generations)) * (i+1)
        )
        ypos = style['trend_graph'].top + style['trend_graph'].height

        maxpos = (xpos,ypos-scale(maxfit))
        medpos = (xpos,ypos-scale(medfit))
        minpos = (xpos,ypos-scale(minfit))


        pygame.draw.line(
            screen,
            style['black'],
            maxpos,
            lastmax,
            1
        )
        pygame.draw.line(
            screen,
            style['black'],
            medpos,
            lastmed,
            1
        )
        pygame.draw.line(
            screen,
            style['black'],
            minpos,
            lastmin,
            1
        )
        lastmax = maxpos
        lastmed = medpos
        lastmin = minpos
        i=i+1




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

        value_text_surface = style['creature']['name_font'].render('sin(a)', True, style['black'])
        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*2))
        )
        value_text_surface = style['creature']['name_font'].render('cos(a)', True, style['black'])
        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*3))
        )
        value_text_surface = style['creature']['name_font'].render('RSpeed', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*4))
        )
        value_text_surface = style['creature']['name_font'].render('XDiff', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*5))
        )
        value_text_surface = style['creature']['name_font'].render('YDiff', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*6))
        )
        value_text_surface = style['creature']['name_font'].render('0', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*7))
        )
        value_text_surface = style['creature']['name_font'].render('1', True, style['black'])

        screen.blit(
            value_text_surface,
            (labelxpos,(value_text_surface.get_height()/2) + style['net_display_area'].top + (style['net_node_spacing'][1]*8))
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

        try:
            border_color.hsva = hsv
        except:
            print(hsv)

        pygame.draw.circle(
            screen,
            border_color,
            (int(creature.pos[0]), int(creature.pos[1])),
            style['creature']['radius'],
            2
        )


        pygame.draw.circle(
            screen,
            border_color,
            (int(creature.pos[0]+(math.cos(creature.angle)*style['creature']['radius'])),
            int(creature.pos[1]+(math.sin(creature.angle)*style['creature']['radius']))),
            math.floor(style['creature']['radius']/2)
        )

        name_text_surface = style['creature']['name_font'].render(
            '{} #{}: {}'.format(creature.name, creature.number,'%.0f' % creature.fitness),
            True, style['black']
        )

        screen.blit(
            name_text_surface,
            (creature.pos[0] - (name_text_surface.get_width() / 2),
            creature.pos[1] - (name_text_surface.get_height() / 2) + style['creature']['name_font_spacing'])
        )

    # Draw log text
    log_text = ('Generation: {} || Sim ticks: {} / {} || Sim state: {} || Population: {} || Autogen: {} || Skip: {} || Maxfit: {}'.format(
        len(generations),
        sim_time,
        ticks_per_gen,
        sim_state,
        len(generations[-1]),
        auto_gen,
        frameskip,
        max_fitness
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
                    else:
                        sim_state = prev_state
                if event.key == pygame.K_a:
                    if auto_gen:
                        auto_gen = False
                    else:
                        auto_gen = True
                if event.key == pygame.K_w:
                    frameskip = frameskip * 2
                if event.key == pygame.K_q:
                    frameskip = max(math.floor(frameskip / 2), 1)

    except:
        log.debug('Can\'t get events, video system not initialised')

    for i in range(frameskip):
        logic()

    draw()

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()
