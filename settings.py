tile_size = 64
screen_width = 1000
screen_height = 600

tower_pos = (200, 480)
bar_pos = ((500, 480), (750, 480))
bait_pos = ((860, 480), (450, 165))
bait_range = (75, 20)

ply_gun_pos = (129, 130)
tower_gun_pos = ((48, 38), (62, 434))

guns = {
    #(wait_timer, reload_timer, ammo, vel, dmg)
    'Estilingue': (0.1, 1, 1, 12, 3),                        # max_dmg = 3
    'Bow': (0.5, 0.6, 1, 15, 5),                             # max_dmg = 5
    'Pistol': (0.3, 1, 7, 18, 2),                            # max_dmg = 14
    'Submetralhadora': (0.2, 1.5, 20, 18, 1.5),              # max_dmg = 30
    'Metralhadora': (0.1, 2, 30, 15, 1.5),                   # max_dmg = 45
    'Laser': (0, 3, 200, 25, 0.35)}                          # max_dmg = 70

all_guns = ('', 'Estilingue', 'Bow', 'Pistol', 'Submetralhadora', 'Metralhadora', 'Laser')

projectiles = {
    'Estilingue': 'Stone',
    'Bow': 'Arrow',
    'Pistol': 'Bullet',
    'Submetralhadora': 'Bullet',
    'Metralhadora':  'Bullet',
    'Laser': 'Feixe'}

guns_volsound = {
    #(vol_shot, vol_reload)
    'Estilingue': (0.03, 0.03),
    'Bow': (0.05, 0.08),
    'Pistol': (0.008, 0.04),
    'Submetralhadora': (0.05, 0.1),
    'Metralhadora':  (0.025, 0.02),
    'Laser': (0.008, 0.07)}

sum_buttons_pos = ((40, 30), (54, 422), (121, 122), (172, 180), (180, 350), (420, 425), (700, 425), (880, 425), (720, 70), (20, 550), (93, 550))
buy_stand_pos = ((90, 10), (104, 402), (171, 102), (222, 160), (230, 330), (330, 340), (610, 340), (790, 340), (630, 110), (5, 460), (150, 520))

buy_stand = {
    '0': {
        '': ('Estilingue', 1, 2000),
        'Estilingue': ('Bow', 1, 5000),
        'Bow': ('Pistol', 1, 8000),
        'Pistol': ('Submetralhadora', 1, 12000),
        'Submetralhadora': ('Metralhadora', 1, 15000),
        'Metralhadora': ('Laser', 1, 20000)
        },
    '1': {
        '': ('Estilingue', 1, 3500),
        'Estilingue': ('Bow', 1, 7000),
        'Bow': ('Pistol', 1 , 10000),
        'Pistol': ('Submetralhadora', 1, 15000),
        'Submetralhadora': ('Metralhadora', 1, 20000),
        'Metralhadora': ('Laser', 1, 25000)
        },
    '2': {
        'Estilingue': ('Bow', 1, 1000),
        'Bow': ('Pistol', 1, 4000),
        'Pistol': ('Submetralhadora', 1, 7000),
        'Submetralhadora': ('Metralhadora', 1, 9000),
        'Metralhadora': ('Laser', 1 , 14000)
        },
    '3': ('Life', 1, 5),
    '4': ('Shield', 1, 10),
    '5': {'Build': ('Barrier', 1, 2800), 'Repair': ('Barrier', 1, 2500)},
    '6': {'Build': ('Barrier', 1, 4500), 'Repair': ('Barrier', 1, 4000)},
    '7': ('Bait', 1, 2500),
    '8': ('Bait', 1, 3000),
    '9': ('Missile', 1, 2000),
    '10': ('Heal_Invul', 1, 10000)
}
