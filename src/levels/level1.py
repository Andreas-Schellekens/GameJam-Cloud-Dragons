def get_level_data(level_width, height):
    platforms = []
    # ground
    platforms.append((0, height - 40, level_width, 40))

    # Gentle intro: a clear ascending / descending sequence of platforms
    platforms += [
        (200, height - 160, 120, 20),
        (380, height - 190, 120, 20),
        (560, height - 220, 120, 20),
        (740, height - 190, 120, 20),
        (920, height - 160, 120, 20),
        (1100, height - 220, 140, 20),
        (1300, height - 180, 140, 20),
        (1500, height - 140, 120, 20),
        (1700, height - 200, 160, 20),
        (1900, height - 160, 200, 20),
        (2200, height - 180, 180, 20),
        (2500, height - 160, 220, 20),
    ]

    # Enemies placed on practical patrol ranges (on / near platforms)
    enemies = [
        (420, height - 190 - 32, 380, 560),   # on the second platform
        (1120, height - 220 - 32, 1100, 1240),# on the 6th platform
        (1800, height - 140 - 32, 1700, 1900) # near the higher platforms cluster
    ]

    powerups = [
        (250, height - 160 - 28, "tree"),
        (980, height - 160 - 28, "recycle"),
        (1550, height - 140 - 28, "solar"),
    ]

    return {
        "platforms": platforms,
        "enemies": enemies,
        "powerups": powerups,
        "door_x": level_width - 120,
        "player_spawn": (64, height - 200),
    }