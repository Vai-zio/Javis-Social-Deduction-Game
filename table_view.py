"""
Draw the Blood on the Clocktower table as a PNG.

Players sit around a long rectangular table.
Seat 0 is at the top left, and the seats go clockwise.

Run this file to make two demo pictures:
    table_public.png       (what everyone sees)
    table_storyteller.png  (same table, with roles shown)
"""

from PIL import Image, ImageDraw, ImageFont

from botc_roles import TOWNSFOLK, OUTSIDERS, MINIONS


WIDTH, HEIGHT = 1200, 700   # size of the picture in pixels
CENTER = (WIDTH // 2, HEIGHT // 2)
TABLE = (320, 220, 880, 480)    # the table: left, top, right, bottom
SEATS = (190, 110, 1010, 590)   # the rectangle the seats sit on (a bit bigger)
SEAT_RADIUS = 55                # size of each seat circle

# Seat colours for the Storyteller copy
COLOURS = {
    "Townsfolk": (70, 130, 220),
    "Outsider": (100, 190, 220),
    "Minion": (220, 110, 60),
    "Demon": (190, 30, 30),
}
ALIVE_COLOUR = (230, 230, 230)
DEAD_COLOUR = (90, 90, 90)


# ---------------------------------------------------------------------------
# Seat maths
# ---------------------------------------------------------------------------

def seat_position(seat: int, number_of_players: int) -> tuple[int, int]:
    """Return the (x, y) pixel where a seat goes."""
    left, top, right, bottom = SEATS
    width = right - left
    height = bottom - top

    # Imagine cutting the rectangle's edge open into one straight line.
    # Its length is the perimeter. Space the seats evenly along it.
    # "+ 0.5" moves every seat half a step, so no seat lands on a corner.
    perimeter = 2 * (width + height)
    distance = perimeter * (seat + 0.5) / number_of_players

    # Now fold the line back into a rectangle, one side at a time:
    # top (going right), right side (down), bottom (left), left side (up).
    if distance < width:
        return round(left + distance), top
    distance -= width
    if distance < height:
        return right, round(top + distance)
    distance -= height
    if distance < width:
        return round(right - distance), bottom
    distance -= width
    return left, round(bottom - distance)


def alive_neighbours(players: list[dict], seat: int) -> tuple[int, int]:
    """Return the seats of the closest alive player on each side."""
    n = len(players)

    # Step left until we find someone alive. "% n" wraps around the table.
    left = (seat - 1) % n
    while not players[left]["alive"] and left != seat:
        left = (left - 1) % n

    right = (seat + 1) % n
    while not players[right]["alive"] and right != seat:
        right = (right + 1) % n

    return left, right


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def get_font(size: int):
    """Use Arial if it exists (Windows), otherwise Pillow's built-in font."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def role_category(role: str) -> str:
    if role in TOWNSFOLK:
        return "Townsfolk"
    if role in OUTSIDERS:
        return "Outsider"
    if role in MINIONS:
        return "Minion"
    return "Demon"


def draw_table(players: list[dict], show_roles: bool = False) -> Image.Image:
    """
    Draw the table and return the picture.

    players: one dict per seat, in seat order, like
        {"name": "Vai", "role": "Imp", "alive": True}
    show_roles: True for the Storyteller's private copy.
    """
    image = Image.new("RGB", (WIDTH, HEIGHT), (30, 30, 40))
    draw = ImageDraw.Draw(image)
    name_font = get_font(18)
    role_font = get_font(14)

    # The table itself
    draw.rounded_rectangle(TABLE, radius=25, fill=(90, 60, 40))
    alive_count = sum(player["alive"] for player in players)
    draw.text(CENTER, f"{alive_count} alive",
              font=get_font(28), fill="white", anchor="mm")

    for seat, player in enumerate(players):
        x, y = seat_position(seat, len(players))

        if not player["alive"]:
            colour = DEAD_COLOUR
        elif show_roles:
            colour = COLOURS[role_category(player["role"])]
        else:
            colour = ALIVE_COLOUR

        draw.ellipse(
            (x - SEAT_RADIUS, y - SEAT_RADIUS, x + SEAT_RADIUS, y + SEAT_RADIUS),
            fill=colour, outline="white", width=2,
        )

        text_colour = "black" if colour == ALIVE_COLOUR else "white"
        draw.text((x, y - 8), f"{seat + 1}. {player['name']}",
                  font=name_font, fill=text_colour, anchor="mm")

        if show_roles:
            draw.text((x, y + 12), player["role"],
                      font=role_font, fill=text_colour, anchor="mm")
        elif not player["alive"]:
            draw.text((x, y + 12), "dead",
                      font=role_font, fill=text_colour, anchor="mm")

    return image


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import random
    from botc import generate_roles

    names = ["Vai", "Ann", "Bo", "Cy", "Dee", "Eli", "Fay", "Gus"]
    setup = generate_roles(len(names))
    random.shuffle(setup["roles"])   # roles come out sorted good-then-evil

    players = [
        {"name": name, "role": role, "alive": True}
        for name, role in zip(names, setup["roles"])
    ]
    players[2]["alive"] = False   # pretend seat 3 died

    # Seat 2 (index 1) skips dead seat 3, so its neighbours are seats 1 and 4.
    left, right = alive_neighbours(players, 1)
    print(f"Seat 2's alive neighbours: seats {left + 1} and {right + 1}")

    draw_table(players).save("table_public.png")
    draw_table(players, show_roles=True).save("table_storyteller.png")
    print("Saved table_public.png and table_storyteller.png")
