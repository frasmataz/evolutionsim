import pygame

pygame.font.init()

style = {}

# Window colours
style['background_color']       = (86, 179, 60)   # green
style['panel_color']            = (166, 228, 146)  # pale green

style['black']                  = (0, 0, 0)
style['white']                  = (255, 255, 255)
style['red']                    = (255, 0, 0)
style['highlight']              = (159, 54, 127)
style['highlight2']              = (211, 126, 71)

# Main window layout
style['main_window_size'] = (1200, 740)

style['sim_panel'] = pygame.Rect(
    20, 20,
    style['main_window_size'][1] - (20 * 2),
    style['main_window_size'][1] - (20 * 2)
)

style['side_panel'] = pygame.Rect(
    style['sim_panel'].left + style['sim_panel'].width + 20,
    20,
    style['main_window_size'][0] - (style['sim_panel'].left + style['sim_panel'].width + 40),
    style['main_window_size'][1] - (20 * 2)
)

style['trend_graph_height'] = 200
style['trend_graph']= pygame.Rect(
    style['side_panel'].left,
    style['side_panel'].top + style['side_panel'].height - style['trend_graph_height'],
    style['side_panel'].width,
    style['trend_graph_height']
)

style['target_rad'] = 25

style['side_creature_name_height'] = 50
style['side_creature_name_toppad'] = 10
style['side_creature_name_font'] = pygame.font.SysFont('Andale Mono',72)

style['net_display_area'] = pygame.Rect(
    style['side_panel'].left,
    style['side_panel'].top + style['side_creature_name_height'],
    style['side_panel'].width,
    style['side_panel'].height - style['side_creature_name_height']
)

style['net_node_rad'] = 16
style['net_node_hue'] = 324 # Pink
style['net_node_spacing'] = (70,50)
style['net_input_label'] = style['net_display_area'].left + 20

# Creature
style['creature'] = {
    'radius': 10,
    'name_font': pygame.font.SysFont('Andale Mono',18),
    'name_font_spacing': 20
}
