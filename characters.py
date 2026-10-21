"""
The Character class. Every Clocktower role can be a subclass of it.

A subclass only sets the class attributes it needs, for example:

    class Doubter(Character):
        category = "Outsider"
        ability = "..."

Anything it leaves out falls back to the defaults below.
"""


class Character:
    # Class-level defaults, shared by every role unless a subclass changes them
    name = None
    category = None      # "Townsfolk", "Outsider", "Minion" or "Demon"
    ability = None
    triggers = None      # when the ability happens, e.g. "Each night"
    state = "alive"      # "alive" or "dead"
    deadvote = True      # dead players get one vote for the rest of the game

    def __init__(self, name=None, category=None, ability=None,
                 triggers=None, state=None, deadvote=None):
        # Use the value passed in, or fall back to the class default.
        # "is not None" (instead of "or") so values like False still count.
        self.name = name if name is not None else self.name
        self.category = category if category is not None else self.category
        self.ability = ability if ability is not None else self.ability
        self.triggers = triggers if triggers is not None else self.triggers
        self.state = state if state is not None else self.state
        self.deadvote = deadvote if deadvote is not None else self.deadvote

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # A subclass without a name gets its class name, e.g. "Doubter"
        if not cls.__dict__.get("name"):
            cls.name = cls.__name__

    def printinfo(self):
        """Print this character's info."""
        print(f"| Name: {self.name} | Category: {self.category} "
              f"| Ability: {self.ability} | Triggers: {self.triggers} "
              f"| State: {self.state} | DeadVote: {self.deadvote} |")
