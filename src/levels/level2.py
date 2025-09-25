def get_level_data(level_width, height):
    platforms = []
    # ground
    platforms.append((0, height - 40, level_width, 40))

    # Medium difficulty: alternating gaps, a small "stair" section and a wide gap requiring a running jump
    platforms += [
        (180, height - 170, 140, 20),
        (360, height - 200, 140, 20),
        (540, height - 230, 140, 20),
        (760, height - 180, 120, 20),
        (940, height - 140, 120, 20),
        (1160, height - 200, 160, 20),
        # Wide gap section (encourage sprint + jump)
        (1500, height - 160, 160, 20),
        (1760, height - 160, 120, 20),
        (1980, height - 220, 180, 20),
        (2200, height - 140, 160, 20),
        (2420, height - 200, 220, 20),
    ]

    enemies = [
        (400, height - 200 - 32, 360, 520),   # early enemy on small platform
        (1220, height - 200 - 32, 1160, 1320),# patrol near mid cluster
        (2000, height - 220 - 32, 1980, 2160),# later platform patrol
    ]

    return {
        "platforms": platforms,
        "enemies": enemies,
        "door_x": level_width - 120,
        "player_spawn": (64, height - 200),
    }