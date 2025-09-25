def get_level_data(level_width, height):
    platforms = []
    # ground
    platforms.append((0, height - 40, level_width, 40))

    # Harder: higher platforms and tighter sequences requiring precise timing
    platforms += [
        (220, height - 180, 120, 20),
        (420, height - 240, 120, 20),
        (640, height - 200, 120, 20),
        (840, height - 280, 140, 20),
        (1040, height - 220, 120, 20),
        (1260, height - 160, 160, 20),
        (1500, height - 260, 140, 20),
        (1720, height - 320, 120, 20),
        (1940, height - 200, 160, 20),
        (2160, height - 160, 140, 20),
        (2380, height - 240, 180, 20),
        (2600, height - 180, 220, 20),
    ]

    enemies = [
        (460, height - 240 - 32, 420, 680),
        (1280, height - 160 - 32, 1260, 1460),
        (1740, height - 320 - 32, 1720, 1880),
        (2360, height - 240 - 32, 2320, 2520),
    ]

    powerups = [
        (260, height - 180 - 28, "tree"),
        (1080, height - 220 - 28, "faucet"),
        (2000, height - 200 - 28, "solar"),
        (2650, height - 180 - 28, "recycle"),
    ]

    return {
        "platforms": platforms,
        "enemies": enemies,
        "powerups": powerups,
        "door_x": level_width - 120,
        "player_spawn": (64, height - 200),
    }