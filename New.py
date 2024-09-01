from tkinter import Tk, Frame, IntVar, Label, StringVar, BooleanVar
from tkinter.ttk import Button, Spinbox, Entry, OptionMenu, Style, Checkbutton
from random import choice, shuffle
from webbrowser import open as w_open
from sys import argv
from copy import deepcopy
from types import MappingProxyType
from glob import glob
from os.path import join

from AliasTkFunctions import fix_resolution_issue, resize_window, update_bg, create_tooltip
from AliasGeneralFunctions import superscript

fix_resolution_issue()

main = Tk()


class Triggers:
    SkillButton = -99

    GameStart = 0
    TurnStart = 1
    TurnEnd = 2

    DrawCard = 3
    PlayCard = 4
    DiscardCard = 5
    ExileCard = 6
    RemoveCard = 7

    DamageDealt = 8
    DamageTaken = 9

    BlockGained = 10
    BlockBroken = 11

    EffectGained = 12
    EffectInflicted = 13

    DiscardCleared = 14

    HealthGained = 15
    HealthLost = 16

    DamageCalc = 17
    BlockCalc = 18
    EffectCalc = 19

    Drawn = '0'
    Played = '1'
    Discarded = '2'
    Exiled = '3'
    Removed = '4'


def reset_dictionary():
    return {
        "cards": {
            "Card": {
                "description": "Card description\nDeal 3 damage",
                "cost": 1,
                "target": "opponent",
                "damage": 3,
                "type": "combat"
            },
            "Card 2": {
                "description": "Card 2 description\nGain 5 block\nInflict 1 Effect",
                "cost": 1,
                "target": "opponent",
                "block": 5,
                "effects": (
                    (1, "Effect", "target")
                ),
                "type": "magic"
            },
            "Card 3": {
                "description": "Can't touch this!",
                "cost": 0,
                "type": "Special",
                "unplayable": True,
                Triggers.Drawn: lambda: print("Card 3: I HAVE BEEN DRAWN!!!"),
                Triggers.Discarded: lambda: print("Card 3: I HAVE BEEN DISCARDED!!!")
            }

        },

        "classes": {
            "Class": {
                "description": "Class description",
                "cards": [
                    "Card",
                    "Card",
                    "Card 2",
                    "Card 2",
                    "Card 3",
                    "Card 3",
                ],
                "skills": ["Skill"],
                "hp": 50,
                "energy": 3,
                "hand_size": 5,
                "colour": "#000000"
            }
        },

        "skills": {
            "Skill": {
                "description": "Skill description",
                "trigger_name": "Activate skill",
                Triggers.SkillButton: lambda: print("SkillButton"),
                "colour": "#000000"
            }
        },

        "effects": {
            # Positive: #4b7dc9
            # Negative: #de4765

            "Effect": {
                "description": "Effect description",
                Triggers.TurnStart: lambda: print("Effect triggered"),
                "colour": "#4b7dc9",
                "type": "positive",
                Triggers.BlockCalc: lambda b: exec("b[0] += 100", {"b": b}),
            }
        }
    }


dictionary = reset_dictionary()

players = {}


def reset_non_player():
    return {
        "players": IntVar(value=2),
        "version": ("0.2.1", "Alpha"),
        "splashes": (
            "Alia's turn-based strategy card-game recoded\nRECODED AGAIN",
            "Now with less hardcoding!",
        ),
        "player": 0,
        "opponents": [],
        "max_hand_size": 8,
        "turn": 0,
        "mods_enabled": BooleanVar(value=False)
    }


non_player = reset_non_player()

# noinspection SpellCheckingInspection
main.bind("<Configure>", lambda event: update_bg(main))
main.title(f"New {" - ".join(non_player["version"])}")

card_frame = Frame()
effect_frame = Frame()
ui = Label()
target_frame = Frame()
enemies_frame = Frame()
deck_view = Label()
discard_view = Label()
exile_view = Label()

Style().configure("combat.TButton", foreground="#ff7800")
Style().configure("magic.TButton", foreground="#006fff")
Style().configure("special.TButton", foreground="#00b000")


# noinspection PyPep8Naming
def QFrame(window, **kwargs):
    f = Frame(window)
    f.pack(**kwargs)
    return f


# noinspection SpellCheckingInspection
def setup(stage=0, finished=None):
    global dictionary, non_player

    if finished is None:
        finished = []

    [w.destroy() for w in main.winfo_children()]

    if stage == 0:
        dictionary = reset_dictionary()
        non_player = reset_non_player()

        main.configure(background="#f8bfff")

        resize_window(main, 4, 4, False)

        frame = QFrame(main, expand=True)

        label = Label(frame, text="".join("Library"), font=("Lucida Fax", 20, "italic"))
        label.pack()
        label.bind("<Button-1>", lambda _: w_open("https://github.com/AbnormalNormality/Turn-Based-Strategy-Card-Game/"
                                                  "releases/latest"))
        create_tooltip(label, "Click to open patch notes", wait_time=250, x_offset=1, y_offset=50)

        Label(frame, text=choice(non_player["splashes"])).pack(pady=(5, 0))

        Button(text="Next", command=lambda: setup(1)).pack(side="bottom", pady=(10, 20))

        frame = QFrame(main, side="bottom")
        Label(frame, text="Players:",).pack(side="left", padx=(0, 5))
        Spinbox(frame, from_=2, to=4, width=3, state="readonly",
                textvariable=non_player["players"]).pack(side="left")

        Checkbutton(frame, variable=non_player["mods_enabled"], text="Enable mods").pack(padx=(20, 0))

        if auto >= 1:
            setup(1)

    elif stage == 1:
        if non_player["mods_enabled"].get() and not finished:
            for mod in glob(join("*.json")):

                def merge_dicts(source, updates):
                    for key, value in updates.items():
                        if isinstance(value, dict) and key in source:
                            merge_dicts(source[key], value)
                        else:
                            source[key] = value

                merge_dicts(dictionary, eval(open(mod, "r").read()))

            # Important: Stops editing dictionary (no mods)
            dictionary = MappingProxyType(dictionary)

        for p in range(non_player["players"].get()):
            p += 1

            if p in finished:
                continue

            finished.append(p)

            def valid_name(chars):
                return len(chars) <= 15 and not any(char in " " for char in chars)

            players.update({p: {
                "name": StringVar(),
                "class": StringVar()
            }})

            Label(text=f"Name player {p}:").pack(pady=(5, 0))

            frame = QFrame(main)

            Entry(frame, justify="center", validate="key", validatecommand=(main.register(valid_name), "%P"),
                  width=25, textvariable=players[p]["name"]).pack(pady=(10, 10))

            frame = QFrame(main)
            Label(frame, text="Class:").pack(side="left", padx=(0, 5))

            def update_tooltip():
                tooltip = dictionary["classes"][players[p]["class"].get()]["description"]

                class_skills = dictionary["classes"][players[p]["class"].get()]["skills"]
                class_skills = "\n".join(f"{s}: {dictionary["skills"][s]["description"][:50] + 
                                                 (dictionary["skills"][s]["description"][50:] and "...")}" for s in
                                         class_skills)

                class_cards = dictionary["classes"][players[p]["class"].get()]["cards"]
                class_cards = [f"{c} (x{class_cards.count(c)})" if class_cards.count(c) > 1 else c for c in class_cards]
                class_cards = [c for i, c in enumerate(class_cards) if i == class_cards.index(c)]
                class_cards = [f"{c}: {dictionary["cards"][" ".join(c.split(" ")[:-1])]["description"][:50] + 
                                       (dictionary["cards"][" ".join(c.split(" ")[:-1])]["description"][50:] and 
                                        "...")}" for c in
                               class_cards]

                tooltip = f"{tooltip}\n{class_skills}\n{"-" * 20}\n{"\n".join(class_cards)}"

                create_tooltip(class_menu, tooltip, wait_time=250, x_offset=0, y_offset=33, wraplength=400)

            class_menu = OptionMenu(frame, players[p]["class"], choice(list(dictionary["classes"])),
                                    *dictionary["classes"], command=lambda _: update_tooltip())
            class_menu.pack(side="left")
            update_tooltip()

            break

        if len(finished) != non_player["players"].get():
            button = Button(text="Next", command=lambda: setup(1, finished))
        else:
            button = Button(text="Start", command=lambda: setup(2))
        button.pack(side="bottom", pady=(10, 20))

        if len(finished) != non_player["players"].get() and auto >= 1:
            setup(1, finished)
        elif auto >= 1:
            setup(2)

    elif stage == 2:
        non_player["players"] = non_player["players"].get() if type(non_player["players"]) is IntVar \
            else non_player["players"]

        for p in players:
            players[p]["class"] = players[p]["class"].get()
            players[p] = {
                "name": players[p]["name"].get() if players[p]["name"].get() else f"Player {p}",
                "hp": 0, "max_hp": get_class(get_player(p, "class"), "hp"),
                "energy": 0, "max_energy": get_class(get_player(p, "class"), "energy"),
                "deck": deepcopy(get_class(get_player(p, "class"), "cards")), "hand": [], "discard": [], "exile": [],
                "hand_size": get_class(get_player(p, "class"), "hand_size"),
                "skills": deepcopy(get_class(get_player(p, "class"), "skills")),
                "effects": {}, "block": 0, "colour": get_class(get_player(p, "class"), "colour")
            }

        resize_window(main, 2, 2, False)

        game()


auto = 0

for arg in argv[1:]:
    if arg.startswith("auto="):
        try:
            auto = int(arg.split("=")[1])
        except ValueError:
            print("Invalid value for auto, must be an integer.")


main.after_idle(setup)


def cycle_turn():
    player_list = list(players)

    if not non_player["player"]:
        non_player["player"] = choice(player_list)
    else:
        current_index = player_list.index(non_player["player"])
        next_index = (current_index + 1) % len(player_list)
        non_player["player"] = player_list[next_index]

    non_player["opponents"] = [player for player in player_list if player != non_player["player"]]

    non_player["turn"] += 1


def get_class(c, k):
    return dictionary["classes"][c][k]


def get_player(p=None, k=None):
    if p is None:
        p = get_turn()
    return players[p][k]


def game():
    global card_frame, effect_frame, ui, target_frame, enemies_frame, deck_view, discard_view, exile_view

    # main.configure(background="#ffd6fa")

    button = Label(main, text="End turn", foreground="#cc0000", font="TkDefaultFont 8 bold", width=10)
    button.pack(side="bottom", pady=(0, 10))
    button.bind("<Button-1>", lambda _: end_turn())
    main.bind("<KeyRelease-e>", lambda _: end_turn())

    card_frame = QFrame(main, side="bottom", pady=(0, 10))
    Label(card_frame, text="card_frame").pack()

    effect_frame = QFrame(main, side="bottom", pady=(10, 10))
    Label(effect_frame, text="effect_frame").pack()

    ui = Label(text="ui")
    ui.pack(side="bottom")

    enemies_frame = QFrame(main, pady=(10, 0))

    target_frame = Frame()
    target_frame.place(relx=0.5, rely=0.5, anchor="center")

    #

    frame = Frame()
    frame.place(relx=0.95, rely=0.5, anchor="center")

    deck_view = Label(frame, text="Deck", justify="right")
    deck_view.pack(side="top")

    discard_view = Label(frame, text="Discard", justify="right")
    discard_view.pack(side="top")

    exile_view = Label(frame, text="Exile", justify="right")
    exile_view.pack(side="top")

    #

    for _ in players:
        cycle_turn()

        players[get_turn()]["hp"] = get_player(k="max_hp")
        players[get_turn()]["energy"] = get_player(k="max_energy")

        check_skills(Triggers.GameStart)

    start_turn()


def check_skills(trigger, p=None, **kwargs):
    if p is None:
        p = get_turn()

    for s in players[p]["skills"]:
        s = dictionary["skills"][s]

        if trigger in s:
            """
            t = True
            event = None

            for i in s:
                if type(s) is not tuple:
                    event = s[trigger]
                    break

                if type(i() if callable(i) else i) is bool:
                    t = i() if callable(i) else i

                elif callable(i):
                    event = i

            if t and event is not None:
                event()
            """
            s[trigger](**kwargs)


def draw_hand(amount=None):
    if amount is None:
        amount = get_player(k="hand_size")
    for _ in range(amount):
        if len(get_player(k="deck")) < 1:
            players[get_turn()]["deck"] = get_player(k="discard").copy()
            shuffle(players[get_turn()]["deck"])
            players[get_turn()]["discard"].clear()

        # Important limit hand size, needs testing
        if len(get_player(k="deck")) < 1 or len(get_player(k="hand")) == non_player["max_hand_size"]:
            break

        c = choice(get_player(k="deck"))
        players[get_turn()]["deck"].remove(c)
        players[get_turn()]["hand"].append(c)

        check_cards(c, Triggers.Drawn)


def get_turn(current=True):
    return non_player["player"] if current else non_player["opponents"]


def start_turn():
    players[get_turn()]["energy"] = get_player(k="max_energy")

    draw_hand()

    trigger_check(Triggers.TurnStart)

    for n in get_player(k="effects").copy():
        e = get_player(k="effects")[n]
        if dictionary["effects"][n]["type"] == "positive":
            continue

        if "temporary" in e:
            del players[get_turn()]["effects"][n]["temporary"]

        if "normal" in e:
            players[get_turn()]["effects"][n]["normal"] -= 1
            if players[get_turn()]["effects"][n]["normal"] <= 0:
                del players[get_turn()]["effects"][n]["normal"]

        if get_effect_total(n) <= 0:
            del players[get_turn()]["effects"][n]

    update_ui()


def end_turn():
    for c in players[get_turn()]["hand"].copy():
        players[get_turn()]["discard"].append(c)
        check_cards(c, Triggers.Discarded)
        players[get_turn()]["hand"].remove(c)

    trigger_check(Triggers.TurnEnd)

    for n in get_player(k="effects").copy():
        e = get_player(k="effects")[n]
        if dictionary["effects"][n]["type"] == "negative":
            continue

        if "temporary" in e:
            del players[get_turn()]["effects"][n]["temporary"]

        if "normal" in e:
            players[get_turn()]["effects"][n]["normal"] -= 1
            if players[get_turn()]["effects"][n]["normal"] <= 0:
                del players[get_turn()]["effects"][n]["normal"]

        if get_effect_total(n) <= 0:
            del players[get_turn()]["effects"][n]

    cycle_turn()
    start_turn()


# noinspection PyTypeChecker
def update_ui():
    [w.destroy() for w in target_frame.winfo_children()]

    ui.configure(text=f"{get_player(k="name")}\n{get_player(k="hp")}/{get_player(k="max_hp")} HP"
                      f"{f" + {get_player(k="block")}" if get_player(k="block") > 0 else ""}\n"
                      f"{get_player(k="energy")}/{get_player(k="max_energy")} Energy",
                 foreground=get_player(k="colour"))

    [w.destroy() for w in card_frame.winfo_children()]

    keys = "1234567890qwerty"
    key_index = 0

    frame = QFrame(card_frame, side="top")

    for i, c in enumerate(get_player(k="hand")):
        if not i % 4:
            frame = QFrame(card_frame, side="top", pady=(10, 0))

        button = Button(frame, text=f"{c}{f" {superscript(get_card(c, "cost"))}" if "unplayable" not in 
                                                                                    dictionary["cards"][c] else ""}",
                        command=lambda index_=i: play_card(index_), state="disabled" if get_player(k="energy") <
                                                                          get_card(c, "cost") or "unplayable" in
                                                                          dictionary["cards"][c] else "normal",
                        style=f"{get_card(c, "type")}.TButton")

        button.pack(side="left", padx=(0 if i == 0 or not i % 4 else 10, 0))
        create_tooltip(button, get_card(c, "description"), wait_time=100, x_offset=1, y_offset=35)

        if key_index < len(keys):
            key = keys[key_index]
            main.unbind(f"<KeyRelease-{key}>")
            if get_player(k="energy") >= get_card(c, "cost"):
                main.bind(f"<KeyRelease-{key}>", lambda _, index_=i: play_card(index_))
            key_index += 1

    [w.destroy() for w in effect_frame.winfo_children()]

    trigger = False

    for s in get_player(k="skills"):
        if Triggers.SkillButton in dictionary["skills"][s]:
            if not trigger:
                frame = QFrame(effect_frame)

            s = dictionary["skills"][s]

            flag = True
            event = None

            for i in s:
                if type(s[Triggers.SkillButton]) is not tuple:
                    event = s[Triggers.SkillButton]
                    break

                if type(i() if callable(i) else i) is bool:
                    trigger = i() if callable(i) else i

                elif callable(i):
                    event = i

            if flag:
                button = Label(frame, text=s["trigger_name"], font="TkDefaultFont 10 bold",
                               state="normal" if flag else
                               "disabled")
                button.pack(side="left", padx=(0 if not trigger else 5, 0))
                button.bind("<Button-1>", lambda _: event())

            if not trigger:
                trigger = True

    frame = QFrame(effect_frame)

    lsd = get_player(k="skills") + list(get_player(k="effects"))
    for i, e in enumerate(lsd):
        if i % 5:
            frame = QFrame(frame)

        if e in get_player(k="effects"):
            label = Label(frame, text=f"{get_effect_total(e)} {e}", fg=dictionary["effects"][e]["colour"])
            label.pack(side="left", padx=(0 if i == 0 else 5, 0))
            create_tooltip(label, dictionary["effects"][e]["description"], wait_time=100, x_offset=1, y_offset=35)
        else:
            label = Label(frame, text=f"{e}", fg=dictionary["skills"][e]["colour"])
            label.pack(side="left", padx=(0 if i == 0 else 5, 0))
            create_tooltip(label, dictionary["skills"][e]["description"], wait_time=100, x_offset=1, y_offset=35)

    for i in ["deck", "discard", "exile"]:
        if len(get_player(k=i)) > 0:
            create_tooltip(globals()[f"{i}_view"], "\n".join(get_player(k=i)), wait_time=50, x_offset=24, y_offset=35)

    [w.destroy() for w in enemies_frame.winfo_children()]

    for i, p in enumerate(non_player["opponents"]):
        frame = QFrame(enemies_frame, side="left", padx=(0 if i == 0 else 50, 0))

        label = Label(frame, text=f"{get_player(p, k="name")}\n{get_player(p, k="hp")}/"
                                  f"{get_player(p, k="max_hp")} HP{f" + {get_player(p, k="block")}" if 
                                                                   get_player(p, k="block") > 0 else ""}",
                      foreground=get_player(p, k="colour"))
        label.pack(side="top")

        frame = QFrame(frame)

        lsd = get_player(p, k="skills") + list(get_player(p, k="effects"))
        for i2, e in enumerate(lsd):
            if i2 % 5:
                frame = QFrame(frame)

            if e in get_player(p, k="effects"):
                label = Label(frame, text=f"{get_effect_total(e, p)} {e}", fg=dictionary["effects"][e]["colour"])
                label.pack(side="left", padx=(0 if i2 == 0 else 5, 0))
                create_tooltip(label, dictionary["effects"][e]["description"], wait_time=100, x_offset=1, y_offset=35)
            else:
                label = Label(frame, text=f"{e}", fg=dictionary["skills"][e]["colour"])
                label.pack(side="left", padx=(0 if i2 == 0 else 5, 0))
                create_tooltip(label, dictionary["skills"][e]["description"], wait_time=100, x_offset=1, y_offset=35)


def play_card(i, t=None, home="hand"):
    n, c = get_player(k=home)[i], dictionary["cards"][get_player(k=home)[i]]
    if c["target"] == "all_opponents":
        t = non_player["opponents"]

    elif len(non_player["opponents"]) == 1 and c["target"] == "opponent":
        t = non_player["opponents"]

    elif c["target"] == "self":
        t = get_turn()

    if t is None:
        Label(target_frame, text=f"Who do you target with {n}?", foreground="#cc0000").pack()
        frame = QFrame(target_frame)

        for i_, p in enumerate(non_player["opponents"]):
            Button(frame, text=p, command=lambda k=p: play_card(i, [k])).pack(side="left", padx=(0 if i_ == 0 else 5,
                                                                                                 0))

        return

    players[get_turn()]["energy"] -= get_card(n, "cost")

    for p in t:
        target_types = {
            "target": p,
            "self": get_turn()
        }

        if "damage" in c:
            attack(p, get_card(n, "damage"), "ignore_block" in c)

        if "block" in c:
            gain_block(get_turn(), get_card(n, "block"))

        if "effects" in c:
            effect = None
            amount = None
            duration = "normal"
            target = None

            for e in c["effects"]:
                if e in dictionary["effects"]:
                    effect = e
                elif type(e) is int:
                    amount = e
                elif e in ["temporary", "normal", "permanent"]:
                    duration = e
                elif e in target_types:
                    target = target_types[e]

            if all(i is not None for i in [effect, amount, duration, target]):
                add_effect(target, effect, amount, duration)

    trigger_check(Triggers.PlayCard)

    players[get_turn()]["discard"].append(players[get_turn()]["hand"].pop(i))
    check_cards(n, Triggers.Discarded)

    update_ui()


def get_card(c, k):
    return dictionary["cards"][c][k]


def get_effect_total(e, p=None, types=("normal", "temporary", "permanent")):
    if p is None:
        p = get_turn()

    v = 0

    if e in get_player(p, k="effects"):
        for i in types:
            if i in get_player(p, "effects")[e]:
                v += get_player(p, "effects")[e][i]

    return v


def add_effect(t, e, a, d):
    e, a, d = [e], [a], [d]

    trigger_check(Triggers.EffectCalc, e=e, a=a, d=d)

    if e[0] not in get_player(t, "effects"):
        players[t]["effects"].update({e[0]: {}})

    if d[0] not in get_player(t, "effects")[e[0]]:
        players[t]["effects"][e[0]].update({d[0]: 0})

    players[t]["effects"][e[0]][d[0]] += a[0]

    trigger_check(Triggers.EffectInflicted)

    trigger_check(Triggers.EffectGained, t)


def attack(t, d, ignore_block=False):
    d = [d]

    if not ignore_block:
        d[0] -= get_player(t, "block")

    trigger_check(Triggers.DamageCalc, d=d)

    if d[0] > 0:
        players[t]["hp"] -= d[0]

        trigger_check(Triggers.DamageDealt)

        trigger_check(Triggers.BlockBroken, t)

        trigger_check(Triggers.DamageTaken, t)

        trigger_check(Triggers.HealthLost, t)


def gain_block(t, b):
    b = [b]

    trigger_check(Triggers.BlockCalc, b=b)

    players[t]["block"] += b[0]

    trigger_check(Triggers.BlockGained)


def check_effects(trigger, p=None, **kwargs):
    if p is None:
        p = get_turn()

    for e in players[p]["effects"]:
        e = dictionary["effects"][e]

        if trigger in e:
            """
            t = True
            event = None

            for i in e:
                if type(e) is not tuple:
                    event = e[trigger]
                    break

                if type(i() if callable(i) else i) is bool:
                    t = i() if callable(i) else i

                elif callable(i):
                    event = i

            if t and event is not None:
                event()
            """
            e[trigger](**kwargs)


def trigger_check(trigger, t=None, **kwargs):
    check_skills(trigger, t, **kwargs)
    check_effects(trigger, t, **kwargs)


def check_cards(c, trigger, **kwargs):
    c = dictionary["cards"][c]

    if trigger in c:
        """
        t = True
        event = None

        if type(c) is not tuple:
            event = c[trigger]

        else:
            for i in c:

                if type(i() if callable(i) else i) is bool:
                    t = i() if callable(i) else i

                elif callable(i):
                    event = i

        if t and event is not None:
            event()
        """
        c[trigger](**kwargs)


main.mainloop()
