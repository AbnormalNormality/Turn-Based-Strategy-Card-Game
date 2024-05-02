from tkinter import Tk, Frame, Label, StringVar, colorchooser, BooleanVar
from tkinter.ttk import Button, Entry, OptionMenu, Style, Checkbutton
from AliasTkFunctions.tkfunctions import fix_resolution_issue, CreateToolTip
from AliasHelpfulFunctions.generalFunctions import minimize_python, restart_program, get_username, make_super_script
from random import choice, shuffle
from sys import exit
from pygame import mixer
from os import system

system("cls")
mixer.init()
mixer.music.load("017 - BMI Very Fat.mp3")
mixer.music.play(loops=-1)

# noinspection SpellCheckingInspection
dictionary = {
    "cards": {
        "card": {"description": "Deal 5 damage.", "type": "combat", "cost": 1, "target": "1 opponent", "damage": 5,
                 "add to deck": ["magic card", "hand", 10, "self"]},
        "magic card": {"description": "Gain 3 block.\nApply 2 weak.", "type": "magic", "cost": 1,
                       "target": "1 opponent", "block": [5, "self", False], "effects": {"Weak": [2, "self", False]}},
        "Slash": {"description": "Strike the opponent.\nDeal 4 damage.", "damage": 4},
    },
    "effects": {
        "effect": {"description": "effect description", "effect type": "positive"},
        "Weak": {"description": "Reduces damage you deal by 30%", "effect type": "negative"}
    },
    "classes": {
        "class": {"health": 50, "energy": 3, "skills": ["skill"], "effects": {},
                  "description": "Start with 60 health and skill.",
                  "deck": [
                      "card",
                      "card",
                      "card",
                      "magic card",
                      "magic card",
                      "magic card",
                  ]},
        "Fledgling": {"description": "A deck for beginners. Start with 60 health and Beginner's luck.", "skills": ["Beginner's luck"],
                      "deck": [
                        "Slash",
                        "Slash",
                        "Slash",
                        "Slash",
                      ]}
    },
    "skills": {
        "skill": "skill description",
        "Beginner's luck": "Recieve 20% less damage from incoming attacks",
    },
    "patch notes": {
        "Alpha 0": """
        First version of Alia's Turn-Based Strategy Card Game! Recoded (placeholder name)
        Added player names
        You can now choose your class.
        You can now restart without causing errors,*\nit now just re-opens the game.
        You can now choose a colour for yourself which will show in UI
        You can now choose whether a player is a CPU or a person (currently softlocks the game)
        Positive and negative buffs will have a different colour

        Added classes:
            class
            all
        Added skills:
            skill
        Added effects:
            effect
        Added cards:
            card
            magic card
        """,
        "Alpha 0.1": """
        Healing and effects implemented
        Dev features are now accessible as toggle when opening game
        Added test bg music
        Class names will no longer say Class next to the player's*\nname (Fledgling instead of Fledgling Class)
        Implemented adding cards to hands/decks/discards
        
        Added classes:
            Fledgling
        Added skill:
            Beginner's luck
        Added effects:
            Weak
        Changed cards:
            magic card*\nCreator's comment:*\nWorking with new names: Codex: Multiplayer Turn-Based Strategy*\nFeel free to suggest new names.
        """
    }
}
for card_name in dictionary["cards"]:
    card = dictionary["cards"][card_name]
    if "details" not in card:
        dictionary["cards"][card_name]["details"] = []
    if "cost" not in card:
        dictionary["cards"][card_name]["cost"] = 1
    if "type" not in card:
        dictionary["cards"][card_name]["type"] = "combat"
    if "description" not in card:
        dictionary["cards"][card_name]["description"] = ""
    if "target" not in card:
        dictionary["cards"][card_name]["target"] = "1 opponent"

for class_name in dictionary["classes"]:
    class_ = dictionary["classes"][class_name]
    if "health" not in class_:
        dictionary["classes"][class_name]["health"] = 50
    if "energy" not in class_:
        dictionary["classes"][class_name]["energy"] = 3
    if "description" not in class_:
        dictionary["classes"][class_name]["description"] = ""
    if "skills" not in class_:
        dictionary["classes"][class_name]["skills"] = []
    if "deck" not in class_:
        dictionary["classes"][class_name]["deck"] = []
    if "effects" not in class_:
        dictionary["classes"][class_name]["effects"] = {}

dictionary["classes"]["all"] = {"health": 99, "energy": 3, "description": "Start with 99 health, every "
                                                                          "skill, and 5 of every effect.",
                                "skills": list(dictionary["skills"]), "deck": list(dictionary["cards"]),
                                "effects": {effect: [5, False] for effect in dictionary["effects"]}}


def main_window_size_and_center(width, height):
    main.geometry(f"{round(width)}x{round(height)}+{(main.winfo_screenwidth() - round(width)) // 2}+"
                  f"{(main.winfo_screenheight() - round(height)) // 2}")
    main.update()


# noinspection PyUnusedLocal
def update_tooltip(*args):
    CreateToolTip(version_menu, dictionary["patch notes"][version.get()].rstrip("\n        ").
                  replace("\n        \n", "\n\n").replace("\n        ", "\n • ").lstrip("\n").
                  replace("\n •     ", "\n     - ").replace("*\n", "\n    "), x_change=0, y_change=26,
                  background="#ffffff", font=("calibri", 9))


def YOU_HAVE_TO_FOCUS(*event):
    main.focus_force()


fix_resolution_issue()
minimize_python()

main = Tk()
main.protocol("<map>", lambda: main.focus_force())
main.protocol("WM_DELETE_WINDOW", exit)
main.bind("<Map>", YOU_HAVE_TO_FOCUS)
main_window_size_and_center(main.winfo_screenwidth() / 3, main.winfo_screenheight() / 3)
main.resizable(False, False)
main.title("Alia's Turn-based Strategy Card Game! Recoded")
main.option_add("*Font", "calibri")

style = Style()
style.configure("TMenubutton", font=("calibri", 10))
style.configure("version_menu.TMenubutton", font=("calibri", 7, "bold"))
style.configure("TButton", font=("calibri", 10))
style.configure("end_button.TButton", foreground="#cc0000", font=("calibri", 10, "bold"))
style.configure("combat.TButton", foreground="#ff7800")
style.configure("magic.TButton", foreground="#006fff")
style.configure("grey.TButton", foreground="#3d3d3d")
style.configure("target.TButton", font=("calibri", 9))

latest_version = list(dictionary["patch notes"])[-1]
dictionary["patch notes"][f"{latest_version} (Current)"] = dictionary["patch notes"].pop(latest_version)
version = StringVar()
version_menu = OptionMenu(main, version, "Patch Notes", *list(dictionary["patch notes"]),
                          style="version_menu.TMenubutton")
version_menu.pack(side="top")
version.trace("w", update_tooltip)
version.set(list(dictionary["patch notes"])[-1])


# noinspection PyDefaultArgument
def setup(stage=0, players_local=None, completed=[]):
    global players, auto, center_frame, dev_features
    if players_local:
        players = int(players_local) if players_local and int(players_local) >= 1 else 1

    if stage == 0:
        center_frame = Frame(main)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
    [w.pack_forget() for w in center_frame.winfo_children()]

    if stage == 0:
        frame = Frame(center_frame)
        frame.pack(side="top")

        def validify(chars):
            return (all(char.isdigit() for char in chars) or chars == "") and len(chars) <= 1

        Label(frame, text="How many players are you playing with? ", font=("calibri", 10)).pack(side="left")
        player_entry = Entry(frame, width=2, justify="center", validate="key", validatecommand=(main.register(validify),
                                                                                                "%P"))
        player_entry.pack(side="left")
        player_entry.insert("0", "2")

        frame = Frame(center_frame)
        frame.pack(side="top", pady=5)

        Label(frame, text="Do you want to enable dev features?", font=("calibri", 10)).pack(side="left")
        dev_features = BooleanVar()
        dev_features.set(True)
        Checkbutton(frame, variable=dev_features).pack(side="left")

        Button(center_frame, text="Next", command=lambda: setup(1, players_local=player_entry.get())).pack(side="top",
                                                                                                           pady=5)
        if auto >= 1:
            setup(1, players_local=player_entry.get())

    if stage == 1:
        if len(completed) == 0:
            for object_ in list(dictionary):
                for card in list(dictionary[object_]):
                    if card in ["combat", "magic card", "class", "skill", "effect", "all"]:
                        if type(dictionary[object_][card]) is not str:
                            dictionary[object_][card]["description"] = (f"{dictionary[object_][card]["description"]}"
                                                                        f"\nThis item is intended for developer use only.")
                        else:
                            dictionary[object_][
                                card] = f"{dictionary[object_][card]}\nThis item is intended for developer use only."
                        if not dev_features.get():
                            del dictionary[object_][card]
        for x in range(players):
            if x in completed:
                continue
            completed.append(x)
            x += 1
            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"Is player {x} a CPU?", font=("calibri", 10)).pack(side="left")
            globals()[f"player_{x}_ai"] = BooleanVar()
            globals()[f"player_{x}_ai"].set(False)
            Checkbutton(frame, variable=globals()[f"player_{x}_ai"]).pack(side="left")

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"What is player {x}'s name?", font=("calibri", 10)).pack(side="left")
            globals()[f"player_{x}_name"] = Entry(frame, width=14, justify="center")
            globals()[f"player_{x}_name"].pack(side="left")
            globals()[f"player_{x}_name"].insert("0", get_username(numbers=False, spaces=True))

            def choose_colour():
                colour = colorchooser.askcolor(title=f"Choose player {x}'s colour")
                if colour[1]:
                    globals()[f"player_{x}_colour"].config(text=colour[1])
                    style.configure("colour_picker.TButton", foreground=colour[1])

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"What colour is player {x}?", font=("calibri", 10)).pack(side="left")
            style.configure("colour_picker.TButton", foreground="#000000")
            globals()[f"player_{x}_colour"] = Button(frame, text="#000000", command=choose_colour,
                                                     style="colour_picker.TButton", width=7)
            globals()[f"player_{x}_colour"].pack(side="left", padx=(5, 0))

            def update_class(*args):
                class_ = globals()[f"player_{x}_class"].get()
                tooltip = f"{get_class_data(class_, "description")}"
                for skill in get_class_data(class_, "skills"):
                    tooltip = tooltip + f"\n{skill}: {dictionary["skills"][skill]}"
                tooltip = tooltip + f"\nDeck:\n • {"\n • ".join(sorted(get_class_data(class_, "deck")))}"
                CreateToolTip(option_menu, tooltip, y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"What class is player {x}?", font=("calibri", 10)).pack(side="left")
            globals()[f"player_{x}_class"] = StringVar()
            option_menu = OptionMenu(frame, globals()[f"player_{x}_class"], choice(list(dictionary["classes"])),
                                     *list(dictionary["classes"]))
            option_menu.pack(side="left")
            globals()[f"player_{x}_class"].trace("w", update_class)
            update_class()
            break

        if not completed == list(range(players)):
            Button(center_frame, text="Next", command=lambda: setup(1, completed=completed)).pack(side="top", pady=5)
            if auto >= 1:
                setup(1, completed=completed)
        else:
            Button(center_frame, text="Start", command=start_game).pack(side="top", pady=5)
            if auto >= 1:
                main.after(1, start_game)


def start_game():
    global players, player_data, turn, card_frame, player_info, enemy_info, end_button, target_frame, turn_label
    player_data = {}
    for x in range(players):
        x += 1
        class_name = globals()[f"player_{x}_class"].get()
        player_data.update({x: {
            "name": globals()[f"player_{x}_name"].get() if (globals()[f"player_{x}_name"].get().strip()) else
            f"Player {x}", "class": class_name, "max health": get_class_data(class_name, "health"),
            "health": get_class_data(class_name, "health"), "turn energy": get_class_data(class_name, "energy"),
            "energy": 0, "skills": [skill for skill in get_class_data(class_name, "skills")], "effects":
                get_class_data(class_name, "effects"), "hand size": 4, "deck": get_class_data(class_name, "deck").copy(),
            "hand": [], "discard": [], "exile": [],
            "ai": choice(["random"]) if globals()[f"player_{x}_ai"].get() else False,
            "colour": globals()[f"player_{x}_colour"].cget("text"), "block": 0,
        }})
        shuffle(player_data[x]["deck"])
    turn = {
        "turn": 0, "all": list(player_data)}
    [print(f"{p}: {player_data[p]}") for p in player_data]
    [w.place_forget() for w in main.winfo_children()]
    [w.pack_forget() for w in main.winfo_children()]
    main_window_size_and_center(main.winfo_screenwidth() / 2, main.winfo_screenheight() / 2)

    end_button = Button(main, text="End Turn", command=end_turn, style="end_button.TButton")
    end_button.place(x=main.winfo_width() - 150, y=main.winfo_height() - 110)
    (Button(main, text="Restart Game", command=restart_program, style="end_button.TButton")
     .place(x=main.winfo_width() - 150, y=main.winfo_height() - 55))

    card_frame = Frame(main)
    card_frame.pack(side="bottom", pady=20)
    target_frame = Frame(main)
    target_frame.place(relx=0.5, rely=0.5, anchor="center")

    player_info = Frame(main)
    player_info.pack(side="bottom")
    enemy_info = Frame(main)
    enemy_info.pack(side="top")

    turn_label = Label(main, font=("calibri", 16))
    turn_label.place(x=main.winfo_width() - 90, y=main.winfo_height() - 150, anchor="center")

    start_turn()


def get_player_data(target, key):
    return player_data[target][key]


def get_turn(key="current"):
    return turn[key]


def get_card_data(target, key):
    return dictionary["cards"][target][key]


def get_class_data(target, key):
    return dictionary["classes"][target][key]


def progress_turn():
    global turn
    if "current" not in turn:
        turn["current"] = choice(list(turn["all"]))
    index = turn["all"].index(turn["current"]) + 1
    while index + 1 > len(turn["all"]):
        index -= len(turn["all"])
    turn["current"] = turn["all"][index]
    turn["other"] = turn["all"].copy()
    turn["other"].remove(turn["current"])
    turn["turn"] += 1
    pass


def start_turn():
    progress_turn()
    turn_label.configure(text=f"Turn {turn["turn"]}")
    player_data[get_turn()]["energy"] = player_data[get_turn()]["turn energy"]
    player_data[get_turn()]["block"] = 0
    draw_hand()

    update_info()
    if get_player_data(get_turn(), "ai"):
        main.after(100, ai_choice)


def end_turn():
    for card in get_player_data(get_turn(), "hand").copy():
        player_data[get_turn()]["discard"].append(card)
        player_data[get_turn()]["hand"].remove(card)

    for effect in list(get_player_data(get_turn(),
                                       "effects")):
        if not player_data[get_turn()]["effects"][effect][1]:
            player_data[get_turn()]["effects"][effect] = [player_data[get_turn()]["effects"][effect][0] - 1,
                                                          player_data[get_turn()]["effects"][effect][1]]
        if get_player_data(get_turn(), "effects")[effect][0] <= 0:
            del player_data[get_turn()]["effects"][effect]
    start_turn()


def draw_hand(draw="hand"):
    if draw == "hand":
        draw = player_data[turn["current"]]["hand size"]

    for x in range(draw):
        if len(get_player_data(get_turn(), "deck")) == 0 and len(get_player_data(get_turn(), "discard")) == 0:
            continue
        if not len(get_player_data(get_turn(), "deck")) > 0:
            player_data[get_turn()]["deck"].extend(player_data[get_turn()]["discard"])
            shuffle(player_data[get_turn()]["deck"])
            player_data[get_turn()]["discard"].clear()

        player_data[get_turn()]["hand"].append(get_player_data(get_turn(), "deck")[0])
        player_data[get_turn()]["deck"].remove(get_player_data(get_turn(), "deck")[0])


def update_info():
    global player_info, enemy_info, end_button
    end_button["state"] = "disabled" if get_player_data(get_turn(), "ai") else "enabled"
    [w.destroy() for w in target_frame.winfo_children()]

    [widget.destroy() for widget in card_frame.winfo_children()]
    counter = 0
    frame = Frame(card_frame)
    frame.pack(side="top")
    for card in get_player_data(get_turn(), "hand"):
        if counter == 4:
            frame = Frame(card_frame)
            frame.pack(side="top")
            counter = 0
        counter += 1
        button = Button(frame, text=f" {card} {make_super_script(get_card_data(card, "cost"))} ", style=f"{get_card_data
                        (card, "type") if get_card_data(card, "cost") <= get_player_data(get_turn(), "energy") else 
                        "grey"}.TButton", command=lambda c=card: choose_target(c), state="disabled" if
                        get_player_data(get_turn(), "ai") else "enabled")
        button.pack(side="left", padx=5)
        CreateToolTip(button, f"Costs {get_card_data(card, "cost")} energy\n{get_card_data(card, "description")}",
                      y_change=35, x_change=0, background="#ffffff", font=("calibri", 9))

    [widget.destroy() for widget in player_info.winfo_children()]
    label = Label(player_info, text=f"{get_player_data(get_turn(), "name")} | {get_player_data(get_turn(), "class")}"
                                    f"\n{get_player_data(get_turn(), "health")}/{get_player_data(get_turn(), 
                                                                                                      "max health")} "
                                    f"HP{f" + {get_player_data(get_turn(), "block")} Block" if get_player_data(get_turn(), "block") else ""} | {get_player_data(get_turn(), "energy")}/{get_player_data(get_turn(), 
                                                                                                    "turn energy")} "
                                    f"Energy", foreground=get_player_data(get_turn(), "colour"), font=("calibri", 10))
    label.pack(side="top")

    class_ = get_player_data(get_turn(), "class")
    tooltip = f"{get_class_data(class_, "description")}"
    for skill in get_class_data(class_, "skills"):
        tooltip = tooltip + f"\n{skill}: {dictionary["skills"][skill]}"
    tooltip = tooltip + f"\nDeck:\n • {"\n • ".join(sorted(get_class_data(class_, "deck")))}"
    CreateToolTip(label, tooltip, y_change=35, background="#ffffff", font=("calibri", 9))

    if get_player_data(get_turn(), "skills"):
        frame = Frame(player_info)
        frame.pack(side="top")
        for skill in get_player_data(get_turn(), "skills"):
            label = Label(frame, text=f"{skill}", foreground="#4b7dc9", font=("calibri", 10))
            label.pack(side="left", padx=3)
            CreateToolTip(label, dictionary["skills"][skill], background="#ffffff", font=("calibri", 9))

    if get_player_data(get_turn(), "effects"):
        if not get_player_data(get_turn(), "skills"):
            frame = Frame(player_info)
            frame.pack(side="top")
        for effect in get_player_data(get_turn(), "effects"):
            label = Label(frame, text=f"{effect} {get_player_data(get_turn(), "effects")[effect][0]}",
                          foreground="#4b7dc9" if dictionary["effects"][effect]["effect type"] == "positive" else
                          "#de4765", font=("calibri", 10))
            label.pack(side="left", padx=3)
            CreateToolTip(label, dictionary["effects"][effect]["description"].replace("X", f"{get_player_data(get_turn(), "effects")
                          [effect][0]}"), background="#ffffff", font=("calibri", 9))

    [widget.destroy() for widget in enemy_info.winfo_children()]
    counter = 0
    frame2 = Frame(enemy_info)
    frame2.pack(side="top")
    for enemy in get_turn("other"):
        if counter == 4:
            frame2 = Frame(enemy_info)
            frame2.pack(side="top")
            counter = 0
        counter += 1
        frame = Frame(frame2)
        frame.pack(side="left", padx=5, anchor="n")
        label = Label(frame, text=f"{get_player_data(enemy, "name")} | {get_player_data(enemy, "class")}"
                                  f"\n{get_player_data(enemy, "health")}/{get_player_data(enemy, "max health")} "
                                  f"HP{f" + {get_player_data(enemy, "block")} Block" if get_player_data(enemy, "block") else ""}", font=("calibri", 9), foreground=get_player_data(enemy, "colour"), width=25)
        label.pack(side="top", pady=(10, 0))

        class_ = get_player_data(enemy, "class")
        tooltip = f"{get_class_data(class_, "description")}"
        for skill in get_class_data(class_, "skills"):
            tooltip = tooltip + f"\n{skill}: {dictionary["skills"][skill]}"
        tooltip = tooltip + f"\nDeck:\n • {"\n • ".join(sorted(get_class_data(class_, "deck")))}"
        CreateToolTip(label, tooltip, y_change=35, background="#ffffff", font=("calibri", 9))

        counter2 = 0
        if get_player_data(enemy, "skills"):
            frame = Frame(frame)
            frame.pack(side="top")
            counter2 = 0
            for skill in get_player_data(enemy, "skills"):
                if counter2 == 4:
                    frame = Frame(frame)
                    frame.pack(side="top")
                counter2 += 1
                label = Label(frame, text=f"{skill}", foreground="#4b7dc9", font=("calibri", 10))
                label.pack(side="left", padx=3)
                CreateToolTip(label, dictionary["skills"][skill], background="#ffffff", font=("calibri", 9))

        if get_player_data(enemy, "effects"):
            if not get_player_data(enemy, "skills"):
                frame = Frame(frame)
                frame.pack(side="top")
            for effect in get_player_data(enemy, "effects"):
                if counter2 == 4:
                    frame = Frame(frame)
                    frame.pack(side="top")
                    counter2 = 0
                counter2 += 1
                label = Label(frame, text=f"{effect} {get_player_data(enemy, "effects")[effect][0]}",
                              foreground="#4b7dc9" if dictionary["effects"][effect]["effect type"] == "positive" else
                              "#de4765", font=("calibri", 9))
                label.pack(side="left", padx=3)
                CreateToolTip(label, dictionary["effects"][effect]["description"].replace("X", f"{get_player_data(enemy, "effects")
                              [effect][0]}"), background="#ffffff", font=("calibri", 9))


# noinspection PyUnusedLocal
def play_card(card_name, targets):
    [w.destroy() for w in target_frame.winfo_children()]
    if get_card_data(card_name, "cost") > get_player_data(get_turn(), "energy"):
        return
    player_data[get_turn()]["energy"] -= get_card_data(card_name, "cost")

    card = dictionary["cards"][card_name]

    loop = 0
    if not type(targets) is list:
        targets = [targets]
    for target in targets:
        loop += 1

        if "damage" in card:
            damage = card["damage"]

            damage *= 0.3 if "Weak" in player_data[get_turn()]["effects"] else 1
            damage *= 0.8 if "Beginner's luck" in player_data[target]["skills"] else 1

            if "ignores block" not in card["details"]:
                stored = damage
                damage -= player_data[target]["block"]
                player_data[target]["block"] -= stored
                if player_data[target]["block"] < 0:
                    player_data[target]["block"] = 0
            damage = round(damage)
            if damage < 0:
                damage = 0
            player_data[target]["health"] -= damage
            if player_data[target]["health"] < 0:
                player_data[target]["health"] = 0

        if "block" in card and (not card["block"][2] or (card["block"][2] and loop == 1)):
            block, target_ = card["block"][0], get_turn() if card["block"][1] == "self" else target
            player_data[target_]["block"] += block

        if "effects" in card:
            for status in card["effects"]:
                amount, target_ = (round(card["effects"][status][0]), get_turn() if card["effects"][status][1] == "self"
                                   else target)
                if status not in player_data[target_]["effects"]:
                    player_data[target_]["effects"][status] = [amount, card["effects"][status][2]]
                elif isinstance(player_data[target_]["effects"][status], int):
                    player_data[target_]["effects"][status][0] += amount
                    player_data[target_]["effects"][status][2] = player_data[target_]["effects"][status][2] \
                        if not player_data[target_]["effects"][status][2] else card["effects"][status][2]

        if "heal" in card and (not card["heal"][2] or (card["heal"][2] and loop == 1)):
            health, target_ = card["health"][0], get_turn() if card["health"][1] == "self" else target
            if health < 0:
                health = 0
            player_data[target_]["health"] += health

        if "draw" in card and (not card["draw"][1] or (card["draw"][1] and loop == 1)):
            draw_hand(card["draw"][0])

        if "add to deck" in card:
            card_, target_ = card["add to deck"][0], get_turn() if card["add to deck"][3] == "self" else target
            [player_data[target_][card["add to deck"][1]].append(card_) for x in range(1, card["add to deck"][2])]

        if "special" in card:
            exec(card["special"])

    if "duplicate" in card["details"]:
        player_data[get_turn()]["discard"].append(card_name)

    if card_name in player_data[get_turn()]["hand"]:
        player_data[get_turn()]["discard"].append(card_name)
        player_data[get_turn()]["hand"].remove(card_name)

    update_info()


def choose_target(card, back=False):
    if get_card_data(card, "cost") > get_player_data(get_turn(), "energy"):
        return
    [w.destroy() for w in target_frame.winfo_children()]
    if back:
        return
    elif get_card_data(card, "target") == "all opponents" or (get_card_data(card, "target") == "1 opponent" and
                                                            len(get_turn("other")) == 1):
        play_card(card, get_turn("other"))
    elif get_card_data(card, "target") == "all players":
        play_card(card, get_turn("all"))
    elif get_card_data(card, "target") == "self":
        play_card(card, [get_turn()])
    else:
        label = Label(target_frame, text=f"Who do you target with {card}?", foreground="#cc0000")
        label.pack(side="top", pady=(0, 5))
        CreateToolTip(label, f"Costs {get_card_data(card, "cost")} energy\n{get_card_data(card, "description")}",
                      y_change=35, x_change=60, background="#ffffff", font=("calibri", 9))
        frame = Frame(target_frame)
        frame.pack(side="top")
        Button(frame, text="Back", command=lambda: choose_target(card, back=True), style="target.TButton").pack(side="left")
        counter = 0
        for x in list(player_data):
            if counter == 4:
                frame = Frame(target_frame)
                frame.pack(side="top")
                counter = 0
            counter += 1
            if get_card_data(card, "target") == "1 opponent" and x in get_turn("other"):
                style.configure("target.TButton", foreground=get_player_data(x, "colour"))
                Button(frame, text=player_data[x]["name"], command=lambda: play_card(card, [x]),
                       style="target.TButton").pack(side="left", padx=2)


def ai_choice(loops=0, player=None):
    if player is None:
        player = get_turn()
    ai = get_player_data(get_turn(), "ai")
    print(f"Loops: {loops}")
    if ((get_player_data(get_turn(), "energy") == 0 and not
        any(get_card_data(card, "cost") == 0 for card in get_player_data(get_turn(), "hand"))) or
            loops == 20 or get_turn() != player or len(get_player_data(get_turn(), "hand")) == 0):  # Failsafe
        end_turn()
        return

    if ai == "random":
        target = choice(get_turn("other"))
        while target == get_turn():
            target = choice(get_turn("other"))
        play_card(choice(get_player_data(get_turn(), "hand").copy()), [target])
    elif ai == "strategic":
        pass

    main.after(100, lambda: ai_choice(loops + 1))


auto = 0
setup()
main.mainloop()
