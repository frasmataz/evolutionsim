import pygame

style = {}

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

# colours
style['background_color']       = (86, 179, 60)   # green
style['panel_color']            = (166, 228, 146)  # pale green

style['black']                  = (0, 0, 0)
style['white']                  = (255, 255, 255)
style['red']                    = (255, 0, 0)
