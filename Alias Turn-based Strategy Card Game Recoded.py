from tkinter import Tk, Frame, Label, StringVar, colorchooser, BooleanVar, messagebox, Toplevel, Scale
from tkinter.ttk import Button, Entry, OptionMenu, Style, Checkbutton
from AliasTkFunctions.tkfunctions import fix_resolution_issue, CreateToolTip, create_scrollable_frame
from AliasHelpfulFunctions.generalFunctions import minimize_python, restart_program, get_username, make_super_script, \
    returner, play_sound, read_line
from random import choice, shuffle, randint
from sys import exit
from os import system, path, listdir, makedirs
from copy import deepcopy
from math import floor, ceil

system("cls")
sounds = False
if sounds:
    if path.isfile("017 - BMI Very Fat.mp3"):
        play_sound("017 - BMI Very Fat.mp3", loops=-1)

# noinspection SpellCheckingInspection
dictionary = {
    "cards": {
        "card": {"description": "Deal 5 damage.\nAdd a magic card to your hand.", "type": "combat", "cost": 1,
                 "target": "1 opponent", "damage": 5,
                 "evoke": {"card": "magic card", "pile": "hand", "amount": 1, "target": "self"}},
        "magic card": {"description": "Gain 3 block.\nApply 2 weak.", "type": "magic", "cost": 1,
                       "target": "1 opponent", "block": {"amount": 5, "target": "self"},
                       "effects": {"Weak": {"amount": 2, "target": "opponent", "duration": "normal"}}},
        "Slash": {"description": "Strike the opponent.\nDeal 4 damage.", "damage": 4},

        "Ritual": {"description": "Lose 5 HP\nAdd one demon card to your hand.",
                   "evoke": {"card": lambda: choice(["Fortis", "Lentus", "Callidus"]), "target": "self", "amount": 1,
                             "pile": "hand"}, "heal": {"target": "self", "amount": -5}, "type": "magic", "cost": 0},
        "Fortis": {
            "description": "Gain 2 Strength until the start of your next turn.\nDeal *d damage\nRemove this card from your deck.",
            "effects": {"Strength": {"amount": 2, "target": "self", "duration": "temporary"}}, "damage": 4, "cost": 2,
            "type": "special", "details": ["remove"]},
        "Lentus": {
            "description": "Gain 2 Resistance until the start of your next turn.\nGain *b block\nRemove this card from your deck.",
            "block": {"amount": 10, "target": "self"},
            "effects": {"Resistance": {"amount": 2, "target": "self", "duration": "temporary"}}, "cost": 2,
            "type": "special", "details": ["remove"]},
        "Callidus": {
            "description": "Apply 2 Weak.\nApply 2 Frail\nApply 2 Vulnerable\nLose 2 HP\nRemove this card from your deck.",
            "cost": 2, "type": "special", "effects": {"Weak": {"amount": 2, "target": "opponent", "duration": "normal"},
                                                      "Frail": {"amount": 2, "target": "opponent",
                                                                "duration": "normal"},
                                                      "Vulnerable": {"amount": 2, "target": "opponent",
                                                                     "duration": "normal"}},
            "heal": {"target": "self", "amount": -1}, "details": ["remove"]},

        "SPECIAL DAMAGE": {"description": "Deal 3 damage for each unspent energy\n9 > 6 > 3",
                           "display name": "Spirit of Vengeance", "details": ["disintegrate", "do not discard"],
                           "damage": {"amount": 3, "times": lambda: c_energy}, "type": "special"},
        "SPECIAL BLOCK": {"description": "Gain 5 block for each unspent energy\n15 > 10 > 5",
                          "display name": "Spirit of Sanctuary", "details": ["disintegrate", "do not discard"],
                          "block": lambda: 5 * c_energy, "type": "special", "target": "self"},
        "SPECIAL EFFECT": {"description": "Gain 2 Thorns for each unspent energy\n6 > 4 > 2",
                           "display name": "Spirit of Reprisal", "details": ["disintegrate", "do not discard"],
                           "effects": {
                               "Thorns": {"amount": lambda: 2 * c_energy, "target": "self", "duration": "normal"}},
                           "type": "special", "target": "self"},
        "SPECIAL KING": {"description": "Heal 1 for each unspent energy\n3 > 2 > 1",
                         "display name": "Spirit of Renewal", "details": ["disintegrate", "do not discard"],
                         "heal": lambda: 1 * c_energy, "type": "special", "target": "self"},
        "basic damage": {"description": "Apply 1 Vulnerable\nDeal *d damage", "display name": "Acolyte",
                         "effects": {"Vulnerable": {"amount": 1, "target": "opponent", "duration": "normal"}},
                         "damage": 3},
        "basic block": {"description": "Apply 1 Weak\nGain *b block", "display name": "Disciple",
                        "effects": {"Weak": {"amount": 1, "target": "opponent", "duration": "normal"}}, "block": 3,
                        "type": "magic"},
        "basic effect": {"description": "Gain 1 Strength and Resistance until the end of the turn.",
                         "display name": "Devotee",
                         "effects": {"Strength": {"amount": 1, "target": "self", "duration": "temporary"},
                                     "Resistance": {"amount": 1, "target": "self", "duration": "temporary"}},
                         "type": "magic", "target": "self"},

        "Block": {"description": "Gain 5 block", "block": 5, "target": "self"},
        "Weak Magic": {"description": "Deal 2 damage\nApply 1 Weak", "effects": {"Weak": 1}, "damage": 2,
                       "type": "magic"},

        "burn damage": {"description": "Deal *d damage.\nIf the target has Burn, deal double damage.", "damage": 2,
                        "details_dict": {"increase damage if effect": {"effect": "Burn", "amount": 2}}},
        "burn block": {"description": "Gain *b block\nApply 1 Weak to all enemies with Burn.", "block": 4,
                       "details_dict": {"inflict to all with": {"inflicted status": "Weak", "checked status": "Burn",
                                                                "target": "all", "duration": "normal", "amount": 1}},
                       "target": "self"},
        "burn special": {"description": "Deal damage to target equal to their Burn value.",
                         "damage": lambda: get_effect_value(target, "Burn")},
        "poison damage": {"description": "Deal *d damage.\nIf the target has Poison, deal triple damage.", "damage": 2,
                          "details_dict": {"increase damage if effect": {"effect": "Poison", "amount": 3}}},
        "poison block": {"description": "Gain *b block\nApply 1 Frail to all enemies with Poison.", "block": 4,
                         "details_dict": {
                             "inflict to all with": {"inflicted status": "Frail", "checked status": "Poison",
                                                     "target": "all", "duration": "normal", "amount": 1}},
                         "target": "self"},
        "poison special": {"description": "Deal damage to target equal to their Poison value",
                           "damage": lambda: get_effect_value(target, "Poison")},

        "debuff damage": {"description": "Deal 4 damage\nApply 2 Frail to yourself.",
                          "effects": {"Frail": {"amount": 2, "target": "self", "duration": "normal"}},
                          "damage": 4},
        "debuff block": {"description": "Gain 4 block\nApply 2 Weak to yourself.",
                         "effects": {"Weak": {"amount": 2, "target": "self", "duration": "normal"}},
                         "block": 4},
        "debuff special": {"description": "Deal 2 damage for each debuff you have.", "damage": {"amount": 2, "times":
            lambda: len([i for i in get_player_data(get_turn(), "effects") if
                         dictionary["effects"][i]["type"] == "negative"])}},

        "mana damage": {"description": "Deal 3 damage.\nDeal damage more times equal to your mana / 10 (rounded down)",
                        "damage": {"amount": 3, "times":
                            lambda: 1 + (1 if player_data[get_turn()]["special"]["mana"] >= 10 else 0)}},

        # Class cards ^^^
        # Independent cards vvv

        "example independent": {"description": "hi :3"}
    },
    "effects": {
        "effect": {"description": "effect description", "type": "positive"},
        "Weak": {"description": "Reduces damage you deal by 30%", "type": "negative", "classification": "modifier"},
        "Poison": {"description": "Lose X health at the start of your turn",
                   "type": "negative", "classification": "damage over time"},
        "Burn": {"description": "Take X at the end of your turn", "type": "negative",
                 "classification": "damage over time"},
        "Frail": {"description": "Gain 30% less shield from cards", "type": "negative", "classification": "modifier"},
        "Vulnerable": {"description": "Take 30% more damage from cards", "type": "negative",
                       "classification": "modifier"},
        "Exhaust": {"description": "Start each turn with 30% less energy", "type": "negative",
                    "classification": "modifier"},
        "Strength": {"description": "Deal more X damage from cards", "type": "positive", "classification": "modifier"},
        "Resistance": {"description": "Gain X more shield from cards", "type": "positive",
                       "classification": "modifier"},
        "Bleed": {"description": "Lose 1/16th of your HP whe playing a card", "type": "negative",
                  "classification": "damage over time"},
        "Thorns": {"description": "Opponents take X damage when dealing unblocked damage",
                   "type": "positive", "classification": "damage over time"},
        "Armoured": {"type": "positive", "description": "Don't lose shield at the end of your turn.",
                     "classification": "other"},
        "Regeneration": {"type": "positive", "description": "Heal X at the end of your turn.",
                         "classification": "other"},
        "Reflect": {"type": "positive",
                    "description": "Reflect X0% damage back at attackers after effects, skills, and block.",
                    "classification": "damage over time"},
        "Conservation": {"type": "positive", "description": "Gain X energy at the start of your turn.",
                         "classification": "other"},
        "Fear": {"description": "Reduces damage you deal by 50%", "type": "negative", "classification": "modifier"},
        "Preperation": {"type": "positive", "description": "Draw X cards at the start of your turn.",
                        "classification": "other"},
    },
    "classes": {
        "class": {"health": 50, "energy": 3, "skills": ["skill"],
                  "description": "Start with 60 health and skill.",
                  "upgrades": {0: "test upgrade 0", 1: "test upgrade 0", 2: "test upgrade 0", 3: "test upgrade 0"},
                  "deck": [
                      "card",
                      "card",
                      "card",
                      "magic card",
                      "magic card",
                      "magic card",
                  ]},
        "Fledgling": {"description": "A deck for beginners. Start with 60 health and Beginner's luck.",
                      "skills": ["Beginner's luck"],
                      "deck": [
                          "Slash",
                          "Slash",
                          "Slash",
                          "Slash",
                          "Block",
                          "Block",
                          "Block",
                          "Weak Magic",
                      ]},
        "Cultist": {"description": "A class that relies on the support of demons to fight their enemy.",
                    "deck": [
                        "Ritual",
                    ], "health": 50, "energy": 3},
        "Spirit Watcher": {"description": "PLACEHOLDER", "skills": ["Spirit Call"],
                           "deck": [
                               "basic damage",
                               "basic damage",
                               "basic damage",
                               "basic block",
                               "basic block",
                               "basic block",
                               "basic effect",
                               "basic effect",
                           ], "health": 60, "energy": 3},
        "Pyromaniac": {"description": "PLACEHOLDER", "skills": ["Arsonist"], "health": 55,
                       "upgrades": {1: "Burn pierces through shield.",
                                    2: "Burn applied by your skill is affected by Strength.\nGain 1 Strength at the start of yout "
                                       "turn for each enemy with Burn.",
                                    3: "Apply 1 Poison every time you play a card insead of Burn.\nChange "
                                       "your starting deck to a Poison deck."},
                       "deck": ["burn damage", "burn damage", "burn damage", "burn damage", "burn block", "burn block",
                                "burn block", "burn special"]},
        "PLACEHOLDER: Debuff": {"skills": ["Defiance"], "health": 60, "description": "PLACEHOLDER",
                                "upgrades": {1: "Apply 1 of a random debuff to yourself at the start of your turn.",
                                             2: "You defult skill also gives you temporary Resistance.",
                                             3: "Double Strength gained from you default skill."},
                                "deck": ["debuff damage"] * 4 + ["debuff block"] * 3 + ["debuff special"] * 1},
        "PLACEHOLDER: Mana": {"skills": ["Mana burst"], "health": 40,
                              "description": "Gain 1 mana at the end of each turn.",
                              "upgrades": {1: "Gain 2 Mana at the start of each turn.",
                                           2: "Mana burst applies temporary Strength equal to your man instead of "
                                              "dealing damage.",
                                           3: "Start each turn with more energy equal to your Mana / 10 (rounded "
                                              "down, max 3)"},
                              "deck": ["mana damage"]},
    },
    "skills": {
        "skill": "skill description",
        "Beginner's luck": "Recieve 10% less damage from incoming attacks",
        "Spirit Call": "After you play 10 cards you can change your hand to special cards.",
        "Arsonist": "Apply 1 Burn to all enemies every time you play a card.",
        "Defiance": "Gain 1 temporary Strength at the start of your turn equal to the amount of the debuffs you have applied.",
        "Mana burst": "Deal damage equal to our mana.\nSet your mana to 0.",
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
        Changed effects:
            Weak
        Changed cards:
            magic card
        """,
        "Alpha 0.2": """
        Changed how mods are loaded
        When enabling mods it now tells you what the mods enabled add
        Added checks for modded skills for custom effects
        Renamed game window
        Fixed statuses not being added from cards
        Renamed add to deck to evoke
        Changed how GUI is sized
        You can now set a custom screen resolution by editing screen_size.txt
        Bleed and frost no longer stack
        Changed how effects are loaded
        Changed how cards are set
        Cultist is no longer a modded class
        
        Added classes:
            Cultist
        Added effects:
            Poison
            Burn
            Frail
            Vulnerable
            Frost
            Strength
            Resistance
            Bleed
            Thorns
            Armoured
        Changed effects:
            Frost
            Vulnerable
            Frail
            Bleed
        Added cards:
            all card
            Ritual
            Fortis
            Lentus
            Callidus
        
        Known issues:
            Some buttons don't place correctly depending on the size*\n   of your screen, working resolution is 1920x1080 / 1536x864
            Effects are applied to both players when applying to self
            If both players have the same class they both gain effects from cards
        """,
        "Alpha 0.3": """
        Fixed a bug relating to effects
        Changed the order effects are applied
        Changed how damage is dealt
        Changed the order effects are decreased (positive > start of turn, negative > end of turn)
        Added various keybinds for buttons
        Added class upgrades
        Various behind the scenes changes
        
        Added classes:
            Spirit Watcher
            Pyromaniac
        Changed classes:
            Fledgling
        Added skills:
            Spirit Call
            Arsonist
        Changed skills:
            Beginner's Luck
        Added effects:
            Regeneration
            Reflect
            Conservation
            Fear
            Preperation
        Added cards:
            Acolyte
            Desciple
            Devotee
            Spirit of Renewal
            Spirit of Veangence
            Spirit of Reprisal
            Spirit of Sanctuary
            Block
            Weak Magic
            burn block
            burn damage
            burn special
            poison block
            poison damage
            poison special
        Changed cards:
            Spirit of Veangence
            Weak Magic
        """,
        "Alpha 0.4": """
        You can now add extra cards to your deck at the start of the game
        Fixed a lot of bugs
        You can now toggle all on or off in deck editor
        Changed how restarting works
        Added card rarity
        Added card races
        Added independent cards
        Added BTS effect classifications
        Added a difficulty slider
        You can now add multiple copies of a card to your deck
        Some small UI changes
        
        Added classes:
            PLACEHOLDER: Debuff
            PLACEHOLDER: Mana
        Changed classes:
            PLACEHOLDER: Mana (60 > 40 HP, Mana burst caps at 10)
        Added cards:
            example independent
            debuff damage
            debuff block
            debuff special
            mana damage
        Changed cards:
            mana damage
        """
    },
}
dictionary["cards"].update({
    "all card": {
        "description": "Deal *D* damage.\nGain *B* block.\nApply 2 of every effect.\nAdd a magic card to your hand.\nHeal 2 HP.",
        "type": "special", "cost": 1, "target": "1 opponent", "block": {"amount": 5, "target": "self"},
        "heal": {"amount": 1, "target": "self"},
        "effects": {
            effect: {"amount": 2,
                     "target": "self" if dictionary["effects"][effect]["type"] == "positive" else "opponent",
                     "duration": "normal"}
            for effect in dictionary["effects"]}, "damage": 5,
        "evoke": {"card": "magic card", "pile": "hand", "amount": 2, "target": "self"}}})


def fix_dictionary():
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
        if "display name" not in card:
            dictionary["cards"][card_name]["display name"] = card_name
        if "details_dict" not in card:
            dictionary["cards"][card_name]["details_dict"] = {}
        if "rarity" not in card:
            dictionary["cards"][card_name]["rarity"] = "Common"
        if "race" not in card:
            dictionary["cards"][card_name]["race"] = "neutral"

        for i in ["block", "heal", "draw"]:
            if i in card and callable(card[i]):
                dictionary["cards"][card_name][i] = {"amount": card[i], "target": "self"}
            elif i in card and not (type(card[i]) is dict and "target" in card[i]):
                if type(card[i]) is int:
                    if i != "draw":
                        dictionary["cards"][card_name][i] = {
                            "amount": card[i],
                            "target": "self"
                        }
                    else:
                        dictionary["cards"][card_name][i] = {
                            "amount": card[i],
                            "loop": False
                        }
        if "damage" in card:
            if type(card["damage"]) is not dict:
                dictionary["cards"][card_name]["damage"] = {"amount": card["damage"]}
            if "target" not in card["damage"]:
                dictionary["cards"][card_name]["damage"].update({"target": "opponent"})
            if "times" not in card["damage"]:
                dictionary["cards"][card_name]["damage"].update({"times": 1})

        if "effects" in card:
            for effect in card["effects"]:
                if type(card["effects"][effect]) is not dict:
                    card["effects"][effect] = {"amount": card["effects"][effect], "duration": "normal",
                                               "target": "self" if dictionary["effects"][effect][
                                                                       "type"] == "positive" else "opponent"}

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
        if "upgrades" not in class_:
            dictionary["classes"][class_name]["upgrades"] = {1: "Not implemented",
                                                             2: "Not implemented",
                                                             3: "Not implemented"}

    for effect_name in dictionary["effects"]:
        effect = dictionary["effects"][effect_name]
        if "classification" not in effect:
            dictionary["effects"][effect_name]["classification"] = "other"


fix_dictionary()


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
# main.protocol("<configure>", lambda: main.focus_force())
main.protocol("WM_DELETE_WINDOW", exit)
main.bind("<Map>", YOU_HAVE_TO_FOCUS)

if not path.isfile("screen_size.txt"):
    open("screen_size.txt", "w").write(f"{main.winfo_screenwidth()}\n{main.winfo_screenheight()}")
Tk.winfo_screenwidth = lambda self: returner(int(read_line("screen_size.txt", 0)))
Tk.winfo_screenheight = lambda self: returner(int(read_line("screen_size.txt", 1)))


def main_window_size_and_center(width, height, window=main):
    width, height = round(main.winfo_screenwidth() / width), round(main.winfo_screenheight() / height)
    window.geometry(f"{round(width)}x{round(height)}+{(main.winfo_screenwidth() - round(width)) // 2}+"
                    f"{(main.winfo_screenheight() - round(height)) // 2}")
    main.update()


main_window_size_and_center(3, 3)

main.resizable(False, False)
main.title("New Game")
main.option_add("*Font", "calibri")

Style().configure("TMenubutton", font=("calibri", 10))
Style().configure("version_menu.TMenubutton", font=("calibri", 7, "bold"))
Style().configure("TButton", font=("calibri", 10))
Style().configure("end_button.TButton", foreground="#cc0000", font=("calibri", 10, "bold"))
Style().configure("combat.TButton", foreground="#ff7800")
Style().configure("magic.TButton", foreground="#006fff")
Style().configure("special.TButton", foreground="#00b000")
Style().configure("grey.TButton", foreground="#3d3d3d")
Style().configure("target.TButton", font=("calibri", 9))
Style().configure("skill.TButton", foreground="#32a852", font=("calibri", 9))
Style().configure("COUNTER.TButton", width=2)

latest_version = list(dictionary["patch notes"])[-1]
dictionary["patch notes"][f"{latest_version} (Current)"] = dictionary["patch notes"].pop(latest_version)
version = StringVar()
version_menu = OptionMenu(main, version, "Patch Notes", *list(dictionary["patch notes"]),
                          style="version_menu.TMenubutton")
version_menu.pack(side="top")
version.trace("w", update_tooltip)
version.set(list(dictionary["patch notes"])[-1])

bool_dict = {}


# noinspection PyDefaultArgument
def setup(stage=0, players_local=None, completed=[]):
    global players, auto, center_frame, dev_features, mods, s, edit_deck
    if players_local:
        players = int(players_local) if players_local and int(players_local) >= 2 else 2

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

        label = Label(frame, text="Do you want to enable dev features?", font=("calibri", 10))
        label.pack(side="left")
        CreateToolTip(label, "Access to debug cards, faster CPU load times...", y_change=20, x_change=0,
                      background="#ffffff", font=("calibri", 9))
        dev_features = BooleanVar()
        dev_features.set(True)
        Checkbutton(frame, variable=dev_features).pack(side="left")

        frame = Frame(center_frame)
        frame.pack(side="top", pady=5)

        def process_files_in_directory(directory):
            global s
            for item in listdir(directory):
                item_path = path.join(directory, item)
                if path.isfile(item_path):
                    try:
                        s.append(
                            f" • {".".join(item.split(".")[:-1])}: Adds {", ".join(list(eval(open(item_path, "r").read())))}")
                    except:
                        s.append("Error")
                elif path.isdir(item_path):
                    process_files_in_directory(item_path)

        s = []
        [process_files_in_directory(path.abspath(f"mods/{i}")) for i in ["effects", "cards", "skills", "classes"]]
        s = "\n" + "\n".join(sorted(s))
        label = Label(frame, text="Do you want to enable mods?", font=("calibri", 10))
        label.pack(side="left")
        CreateToolTip(label, f"Add mods in the mods folder:{s}", y_change=20, x_change=0, background="#ffffff",
                      font=("calibri", 9))
        mods = BooleanVar()
        mods.set(False)
        Checkbutton(frame, variable=mods).pack(side="left")

        frame = Frame(center_frame)
        frame.pack(side="top", pady=5)

        edit_deck = BooleanVar()
        edit_deck.set(True)

        def more_options():
            global edit_deck

            def on_close():
                modal.destroy()

            modal = Toplevel()
            modal.grab_set()
            main_window_size_and_center(4, 4, modal)
            modal.title("More options")
            modal.protocol("WM_DELETE_WINDOW", on_close)

            frame = Frame(modal)
            frame.pack(side="top")
            label = Label(frame, text="Do you want to enable editing decks?", font=("calibri", 10))
            label.pack(side="left")
            Checkbutton(frame, variable=edit_deck).pack(side="left")

            Button(modal, text="Close", command=modal.destroy).pack(side="bottom", pady=10)
            main.wait_window(modal)

        frame = Frame(center_frame)
        frame.pack(side="top", pady=5)

        Button(frame, text="More", command=more_options).pack(side="left", padx=(0, 10))
        Button(frame, text="Next", command=lambda: setup(1, players_local=player_entry.get())).pack(side="top",
                                                                                                    pady=5)
        if auto >= 1:
            setup(1, players_local=player_entry.get())

    if stage == 1:
        if len(completed) == 0:
            del s
            if mods.get():

                def process_files_in_directory(directory, mode):
                    if not path.isdir(directory):
                        makedirs(directory)
                    for item in listdir(directory):
                        item_path = path.join(directory, item)
                        if path.isfile(item_path):
                            print("Processing file:", item_path)
                            dictionary[mode].update(eval(open(item_path, "r").read()))
                        elif path.isdir(item_path):
                            print("Entering directory:", item_path)
                            process_files_in_directory(item_path, mode)

                [process_files_in_directory(path.abspath(f"mods/{i}"), i) for i in
                 ["effects", "cards", "skills", "classes"]]
                print("Finished loading mods!")

            for object_ in list(dictionary):
                for card in list(dictionary[object_]):
                    if card in ["combat", "magic card", "class", "skill", "effect", "all", "all card",
                                "example independent"]:
                        if type(dictionary[object_][card]) is not str:
                            dictionary[object_][card]["description"] = (f"{dictionary[object_][card]["description"]}"
                                                                        f" (This item is intended for developer use only)")
                        else:
                            dictionary[object_][
                                card] = f"{dictionary[object_][card]}\nThis item is intended for developer use only."
                        if not dev_features.get():
                            del dictionary[object_][card]

            dictionary["classes"]["all"] = {"health": 99, "energy": 3, "description": "Start with 99 health, every "
                                                                                      "skill, and 5 of every effect.",
                                            "skills": list(dictionary["skills"]), "deck": list(dictionary["cards"]),
                                            "effects": {effect: {"normal": 3} for effect in dictionary["effects"]}}

            fix_dictionary()

        for x in range(players):
            if x in completed:
                continue
            completed.append(x)
            x += 1
            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"Is player {x} a CPU?", font=("calibri", 10)).pack(side="left")
            globals()[f"player_{x}_ai"] = BooleanVar()
            globals()[f"player_{x}_ai"].set(False if x == 1 else globals()[f"player_{x - 1}_ai"].get())
            Checkbutton(frame, variable=globals()[f"player_{x}_ai"]).pack(side="left")

            def validify(chars):
                return len(chars) <= 16

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"What is player {x}'s name?", font=("calibri", 10)).pack(side="left")
            globals()[f"player_{x}_name"] = Entry(frame, width=14, justify="center", validate="key",
                                                  validatecommand=(main.register(validify),
                                                                   "%P"))
            globals()[f"player_{x}_name"].pack(side="left")
            u = " " * 17
            while len(u) > 16:
                u = get_username(numbers=False, spaces=True)
            globals()[f"player_{x}_name"].insert("0", u)

            def choose_colour():
                colour = colorchooser.askcolor(title=f"Choose player {x}'s colour")
                if colour[1]:
                    globals()[f"player_{x}_colour"].config(text=colour[1])
                    Style().configure("colour_picker.TButton", foreground=colour[1])

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"What colour is player {x}?", font=("calibri", 10)).pack(side="left")
            Style().configure("colour_picker.TButton", foreground="#000000")
            globals()[f"player_{x}_colour"] = Button(frame, text="#000000", command=choose_colour,
                                                     style="colour_picker.TButton", width=7)
            globals()[f"player_{x}_colour"].pack(side="left", padx=(5, 0))

            def update_class(*args):
                class_ = globals()[f"player_{x}_class"].get()
                tooltip = f"{get_class_data(class_, "description")}"
                for skill in get_class_data(class_, "skills"):
                    tooltip = tooltip + f"\n{skill}: {dictionary["skills"][skill]}"
                e = []
                for card in get_class_data(class_, "deck"):
                    e.append(dictionary["cards"][card]["display name"])
                tooltip = tooltip + f"\nDeck:\n • {"\n • ".join(sorted(e))}"
                CreateToolTip(option_menu, tooltip, y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))
                update_class_upgrades()

            def update_class_upgrades(*args):
                if globals()[f"player_{x}_class_upgrade"].get() == "0":
                    CreateToolTip(option_menu2, "Default skill", y_change=33, x_change=1, background="#ffffff",
                                  font=("calibri", 9))
                    return
                class_ = globals()[f"player_{x}_class"].get()
                upgrade = globals()[f"player_{x}_class_upgrade"].get()
                CreateToolTip(option_menu2,
                              get_class_data(class_, "upgrades")[int(upgrade)] if get_class_data(class_, "upgrades")[
                                  int(upgrade)] else "Not developed", y_change=33, x_change=1, background="#ffffff",
                              font=("calibri", 9))

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)
            Label(frame, text=f"What class is player {x}?", font=("calibri", 10)).pack(side="left")
            globals()[f"player_{x}_class"] = StringVar()
            option_menu = OptionMenu(frame, globals()[f"player_{x}_class"], choice(list(dictionary["classes"])),
                                     *sorted(list(dictionary["classes"])))
            option_menu.pack(side="left")
            globals()[f"player_{x}_class"].trace("w", update_class)

            globals()[f"player_{x}_class_upgrade"] = StringVar()
            option_menu2 = OptionMenu(frame, globals()[f"player_{x}_class_upgrade"], choice(['0', '1', '2', '3']),
                                      *['0', '1', '2', '3'])
            option_menu2.pack(side="left")
            globals()[f"player_{x}_class_upgrade"].trace("w", update_class_upgrades)
            update_class()

            frame = Frame(center_frame)
            frame.pack(side="top", pady=5)

            Label(frame, text=f"Select a difficulty for player {x}", font=("calibri", 10)).pack(side="left")

            def update_scale(value):
                value = int(value)
                if value == -2:  # Easiest
                    label.configure(text="Easiest")
                    tooltip = "Take 20% less damage from attacks.\nDeal 20% more damage"
                    globals()[f"difficulty_{x}"] = [0.8, 1.2]
                elif value == -1:
                    label.configure(text="Easy")
                    tooltip = "Take 10% less damage from attacks.\nDeal 10% more damage"
                    globals()[f"difficulty_{x}"] = [0.9, 1.1]
                elif value == 0:  # No changes
                    label.configure(text="Normal")
                    tooltip = "Normal difficulty, no changes"
                    globals()[f"difficulty_{x}"] = [1, 1]
                elif value == 1:
                    label.configure(text="Hard")
                    tooltip = "Take 10% more damage from attacks.\nDeal 10% less damage"
                    globals()[f"difficulty_{x}"] = [1.1, 0.9]
                elif value == 2:  # Hardest
                    label.configure(text="Hardest")
                    tooltip = "Take 20% more damage from attacks.\nDeal 20% less damage"
                    globals()[f"difficulty_{x}"] = [1.2, 0.8]
                else:
                    return
                CreateToolTip(label, tooltip,
                              y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))

            frame = Frame(frame)
            frame.pack(side="left", pady=5)

            label = Label(frame, text="help")
            label.pack(side="top")
            Scale(frame, from_=-2, to=2, orient="horizontal", command=update_scale, showvalue=False).pack(side="top")
            update_scale(0)

            break

        def more_options():
            global bool_dict
            modal = Toplevel()
            modal.grab_set()
            main_window_size_and_center(3.5, 3.5, modal)
            modal.title("More options")

            Button(modal, text="Close", command=modal.destroy).pack(side="bottom", pady=10)

            for area in ["skills", "cards"]:
                if x not in bool_dict:
                    bool_dict.update({x: {}})
                if area not in bool_dict[x]:
                    bool_dict[x].update({area: {}})
                personal_dict = dictionary[area]
                width = max([len(dictionary[area][i]["display name"] if area == "cards" else i) for i in
                             dictionary[area]]) * 9.4 + 30
                scrollable_frame = create_scrollable_frame(modal, (width, 0), pack_over_place=True, bg_colour="#f6f6f6",
                                                           side="right", fill="y", padx=10)
                scrollable_frame.configure(background="#f6f6f6")

                if area == "skills":
                    def toggle_checks():
                        global bool_dict
                        sta = None
                        for p in bool_dict[x]["skills"]:
                            if sta is None:
                                sta = not bool_dict[x]["skills"][p].get()
                            bool_dict[x]["skills"][p].set(sta)

                    Button(scrollable_frame, text="Toggle all on/off",
                           command=toggle_checks).pack(side="top", anchor="w")

                elif area == "cards":
                    def toggle_checks():
                        global bool_dict
                        sta = None
                        for p in bool_dict[x]["cards"]:
                            if sta is None:
                                sta = 1 if not int(bool_dict[x]["cards"][p].get()) else 0
                            bool_dict[x]["cards"][p].set(sta)

                    Button(scrollable_frame, text="Toggle all on/off",
                           command=toggle_checks).pack(side="top", anchor="w")

                for i in personal_dict:
                    if area == "skills":
                        if f"enabled_{i}" not in bool_dict[x][area]:
                            bool_dict[x][area].update({f"enabled_{i}": BooleanVar()})
                            bool_dict[x][area][f"enabled_{i}"].set(False)
                        Style().configure("Custom.TCheckbutton", background=scrollable_frame.cget("background"))
                        check = Checkbutton(scrollable_frame, text=i, variable=bool_dict[x][area][f"enabled_{i}"],
                                            style=f"Custom.TCheckbutton")
                        check.pack(side="top", anchor="w")
                        CreateToolTip(check, dictionary[area][i], background="#ffffff")

                    elif area == "cards":
                        def change_counter(value, i, limits=(0, 99)):
                            current = int(bool_dict[x][area][f"enabled_{i}"].get())
                            new_value = current + value
                            if new_value < limits[0]:
                                new_value = limits[0]
                            elif new_value > limits[1]:
                                new_value = limits[1]
                            bool_dict[x][area][f"enabled_{i}"].set(new_value)

                        if f"enabled_{i}" not in bool_dict[x]["cards"]:
                            bool_dict[x]["cards"].update({f"enabled_{i}": StringVar()})
                            bool_dict[x]["cards"][f"enabled_{i}"].set("0")

                        frame = Frame(scrollable_frame)
                        frame.pack(side="top", anchor="w")
                        if dictionary[area][i]["type"] == "combat":
                            colour = "#ff7800"
                        elif dictionary[area][i]["type"] == "magic":
                            colour = "#006fff"
                        else:
                            colour = "#00b000"

                        Label(frame, font=("calibri", 9), foreground=colour, text=i,
                              background=scrollable_frame.cget("background")).pack(side="left")

                        Entry(frame, width=3, justify="center",
                              textvariable=bool_dict[x]["cards"][f"enabled_{i}"],
                              state="readonly").pack(side="left")

                        Button(frame, text="+", command=lambda i=i: change_counter(1, i),
                               style="COUNTER.TButton").pack(
                            side="left")

                        Button(frame, text="-", command=lambda i=i: change_counter(-1, i),
                               style="COUNTER.TButton").pack(
                            side="left")

            main.wait_window(modal)

        frame = Frame(center_frame)
        frame.pack(side="top", pady=5)
        if edit_deck.get():
            Button(frame, text="Edit", command=more_options).pack(side="left", padx=(0, 10))

        if not completed == list(range(players)):
            Button(frame, text="Next", command=lambda: setup(1, completed=completed)).pack(side="left")
            if auto >= 2:
                setup(1, completed=completed)
        else:
            Button(frame, text="Start", command=start_game).pack(side="left")
            if auto >= 2:
                main.after(1, start_game)


def start_game():
    global players, player_data, turn, card_frame, player_info, enemy_info, end_button, target_frame, turn_label, \
        view_deck, view_discard, view_exile, bool_dict
    player_data = {}
    for x in range(players):
        x += 1
        class_name = globals()[f"player_{x}_class"].get()
        player_data.update({x: {
            "name": globals()[f"player_{x}_name"].get() if (globals()[f"player_{x}_name"].get().strip()) else
            f"Player {x}", "class": class_name, "max health": get_class_data(class_name, "health"),
            "health": get_class_data(class_name, "health"), "turn energy": get_class_data(class_name, "energy"),
            "energy": 0, "skills": [skill for skill in get_class_data(class_name, "skills")], "effects":
                deepcopy(get_class_data(class_name, "effects")), "hand size": 4,
            "deck": get_class_data(class_name, "deck").copy(),
            "hand": [], "discard": [], "exile": [], "special": {},
            "ai": choice(["random"]) if globals()[f"player_{x}_ai"].get() else False,
            "colour": globals()[f"player_{x}_colour"].cget("text"), "block": 0, "played cards": [],
            "played cards this turn": [], "class upgrade": int(globals()[f"player_{x}_class_upgrade"].get()),
            "difficulty": globals()[f"difficulty_{x}"],
        }})
        if player_data[x]["class"] == "Pyromaniac" and player_data[x]["class upgrade"] == 3:
            for i in range(len(player_data[x]["deck"]) + 1):
                player_data[x]["deck"][i - 1] = player_data[x]["deck"][i - 1].replace("burn", "poison")

        if x in bool_dict:
            for area in ["skills", "cards"]:
                for i in dictionary[area]:
                    if (area == "skills" and bool_dict[x][area][f"enabled_{i}"].get() and
                            i not in player_data[x]["skills"]):
                        player_data[x]["skills"].append(i)
                    elif area == "cards":
                        [player_data[x]["deck"].append(i) for n in range(int(bool_dict[x][area][f"enabled_{i}"].get()) + 1)]

        if "Spirit Call" in player_data[x]["skills"]:
            player_data[x]["special"].update({"spirit counter": 0 if not dev_features.get() else 10})

        if "Mana burst" in player_data[x]["skills"]:
            player_data[x]["special"].update({"mana": 0 if not dev_features.get() else 10})

        shuffle(player_data[x]["deck"])
    turn = {
        "turn": 0, "all": list(player_data)}
    if dev_features.get():
        [print(f"{p}: {player_data[p]}") for p in player_data]
    [w.place_forget() for w in main.winfo_children()]
    [w.pack_forget() for w in main.winfo_children()]
    main_window_size_and_center(2, 2)
    main.title(f"Alia's Turn-based Strategy Card Game! Recoded{" & Modded" if mods.get() else ""}")

    end_button = Button(main, text="End Turn", command=end_turn, style="end_button.TButton")
    end_button.place(x=main.winfo_width() - 150, y=main.winfo_height() - 110)
    main.bind("<KeyRelease-Return>", lambda event: end_turn(event=event))

    def check_restart():
        inp = messagebox.askyesnocancel("Surrender?",
                                        "What do you want to do?\nPress 'Yes' to restart\nPress 'No' to surrender")
        if inp is True:
            restart_program()
        elif inp is False:
            player_data[get_turn()]["health"] = 0
            end_turn()
        else:
            pass

    Button(main, text="Surrender", command=check_restart,
           style="end_button.TButton").place(x=main.winfo_width() - 150,
                                             y=main.winfo_height() - 55)

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

    view_deck = Label(main, text="Deck")
    view_deck.place(x=main.winfo_width() - 90, y=main.winfo_height() - 250, anchor="e")
    view_discard = Label(main, text="Discard")
    view_discard.place(x=main.winfo_width() - 90, y=main.winfo_height() - 225, anchor="e")
    view_exile = Label(main, text="Exile")
    view_exile.place(x=main.winfo_width() - 90, y=main.winfo_height() - 200, anchor="e")

    def onKeyPress1(event):
        [print(f"{p}: {player_data[p]}") for p in player_data]
        [print(f"{p}: {turn[p]}") for p in turn]

    def onKeyPress2(event):
        [print(f"{p}: {dictionary["cards"][p]}") for p in dictionary["cards"]]

    if dev_features.get():
        main.bind("<Control-d>", onKeyPress1)
        main.bind("<Control-c>", onKeyPress2)
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
    update_info()
    turn_label.configure(text=f"Turn {turn["turn"]}")
    player_data[get_turn()]["energy"] = player_data[get_turn()]["turn energy"]

    if "Mana burst" in get_player_data(get_turn(), "skills") and get_player_data(get_turn(), "class upgrade") == 3:
        e = floor(player_data[get_turn()]["special"]["mana"] / 10)
        player_data[get_turn()]["energy"] += e if e <= 3 else 3

    if "Exhaust" in player_data[get_turn()]["effects"]:
        player_data[get_turn()]["energy"] = round(player_data[get_turn()]["energy"] * 2 / 3)
    if "Conservation" in player_data[get_turn()]["effects"]:
        player_data[get_turn()]["energy"] += get_effect_value(get_turn(), "Conservation")
    if "Armoured" not in player_data[get_turn()]["effects"]:
        player_data[get_turn()]["block"] = 0

    player_data[get_turn()]["health"] -= get_effect_value(get_turn(), "Poison") if "Poison" in player_data[get_turn()][
        "effects"] else 0

    draw_hand()
    if "Preparation" in player_data[get_turn()]["effects"]:
        draw_hand(get_effect_value(get_turn(), "Preparation"))

    for effect in get_player_data(get_turn(), "effects").copy():
        # "effects": {"normal": 0, "permanent": 0, "temporary": 0}
        if dictionary["effects"][effect]["type"] == "negative":
            continue

        if "normal" in player_data[get_turn()]["effects"][effect]:
            player_data[get_turn()]["effects"][effect]["normal"] -= 1
            if player_data[get_turn()]["effects"][effect]["normal"] <= 0:
                del player_data[get_turn()]["effects"][effect]["normal"]

        if "temporary" in player_data[get_turn()]["effects"][effect]:
            del player_data[get_turn()]["effects"][effect]["temporary"]

        if not player_data[get_turn()]["effects"][effect]:
            del player_data[get_turn()]["effects"][effect]

    if get_player_data(get_turn(), "class") == "Pyromaniac" and get_player_data(get_turn(), "class upgrade") == 2:
        c = 0
        for t in get_turn("other"):
            if "Burn" in get_player_data(t, "effects"):
                c += 1

        if c > 0:
            if "Strength" not in get_player_data(get_turn(), "effects"):
                player_data[get_turn()]["effects"].update({"Strength": {}})

            if "temporary" not in player_data[get_turn()]["effects"]["Strength"]:
                player_data[get_turn()]["effects"]["Strength"].update({"temporary": 0})

            player_data[get_turn()]["effects"]["Strength"]["temporary"] += c + 1

    if "Defiance" in get_player_data(get_turn(), "skills"):
        if get_player_data(get_turn(), "class upgrade") == 1 and len(
                [i for i in dictionary["effects"] if dictionary["effects"][i]["type"] == "negative"]) > 0:
            effect = choice([i for i in dictionary["effects"] if dictionary["effects"][i]["type"] == "negative"])
            if effect not in get_player_data(get_turn(), "effects"):
                player_data[get_turn()]["effects"].update({effect: {}})
            if "normal" not in player_data[get_turn()]["effects"][effect]:
                player_data[get_turn()]["effects"][effect].update({"normal": 0})
            player_data[get_turn()]["effects"][effect]["normal"] += 2

        amount = len(
            [i for i in get_player_data(get_turn(), "effects") if dictionary["effects"][i]["type"] == "negative"]) * (
                     2 if get_player_data(get_turn(), "class upgrade") == 3 else 1)

        for effect in ["Strength", "Resistance"]:
            if effect == "Resistance" and get_player_data(get_turn(), "class upgrade") != 2 or amount == 0:
                continue
            if effect not in get_player_data(get_turn(), "effects"):
                player_data[get_turn()]["effects"].update({effect: {}})
            if "temporary" not in player_data[get_turn()]["effects"][effect]:
                player_data[get_turn()]["effects"][effect].update({"temporary": 0})
            player_data[get_turn()]["effects"][effect]["temporary"] += amount

    if mods.get():
        def process_files_in_directory(directory):
            for item in listdir(directory):
                item_path = path.join(directory, item)
                if path.isfile(item_path):
                    exec(open(item_path, "r").read())
                elif path.isdir(item_path):
                    process_files_in_directory(item_path)

        process_files_in_directory(path.abspath("mods/skills/start turn check"))

    update_info()
    if player_data[get_turn()]["health"] <= 0:
        end_turn()
    elif get_player_data(get_turn(), "ai"):
        main.after(500 if not dev_features.get() else 100, ai_choice)


def end_turn(event=None):
    discard_hand()
    if "Regeneration" in get_player_data(get_turn(), "effects"):
        health = get_effect_value(get_turn(), "Regeneration")
        if player_data[get_turn()]["health"] + health > player_data[get_turn()]["max health"]:
            health = player_data[get_turn()]["max health"] - player_data[get_turn()]["health"]
        player_data[get_turn()]["health"] += health

    if "Burn" in player_data[get_turn()]["effects"]:
        damage = get_effect_value(get_turn(), "Burn")
        pass_shield = False
        for eieio in get_turn("other"):
            if get_player_data(eieio, "class") == "Pyromaniac" and get_player_data(eieio, "class upgrade") == 1:
                pass_shield = True
                break
        if not pass_shield:
            stored = damage
            damage -= player_data[get_turn()]["block"]
            player_data[get_turn()]["block"] -= stored
            if player_data[get_turn()]["block"] < 0:
                player_data[get_turn()]["block"] = 0
        player_data[get_turn()]["health"] -= damage
        print(damage)

    for effect in get_player_data(get_turn(), "effects").copy():
        # "effects": {"normal": 0, "permanent": 0, "temporary": 0}
        if dictionary["effects"][effect]["type"] == "positive":
            continue

        if "normal" in player_data[get_turn()]["effects"][effect]:
            player_data[get_turn()]["effects"][effect]["normal"] -= 1
            if player_data[get_turn()]["effects"][effect]["normal"] <= 0:
                del player_data[get_turn()]["effects"][effect]["normal"]

        if "temporary" in player_data[get_turn()]["effects"][effect]:
            del player_data[get_turn()]["effects"][effect]["temporary"]

        if not player_data[get_turn()]["effects"][effect]:
            del player_data[get_turn()]["effects"][effect]

    for effect in list(get_player_data(get_turn(), "effects")):
        break  # old code
        if not player_data[get_turn()]["effects"][effect][1]:
            player_data[get_turn()]["effects"][effect] = [player_data[get_turn()]["effects"][effect][0] - 1,
                                                          player_data[get_turn()]["effects"][effect][1]]
        if get_player_data(get_turn(), "effects")[effect][0] <= 0:
            del player_data[get_turn()]["effects"][effect]

    if "Mana burst" in get_player_data(get_turn(), "skills") and player_data[get_turn()]["special"]["mana"] != 10:
        player_data[get_turn()]["special"]["mana"] += 2 if get_player_data(get_turn(), "class upgrade") == 1 and \
                                                           player_data[get_turn()]["special"]["mana"] != 9 else 1

    if mods.get():
        def process_files_in_directory(directory):
            for item in listdir(directory):
                item_path = path.join(directory, item)
                if path.isfile(item_path):
                    exec(open(item_path, "r").read())
                elif path.isdir(item_path):
                    process_files_in_directory(item_path)

        process_files_in_directory(path.abspath("mods/skills/end turn check"))

    player_data[get_turn()]["played cards this turn"].clear()
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
    main.unbind("<KeyRelease-Return>")
    if not get_player_data(get_turn(), "ai"):
        main.bind("<KeyRelease-Return>", lambda event: end_turn(event=event))
    [w.destroy() for w in target_frame.winfo_children()]

    for label in ["deck", "discard", "exile"]:
        e = []
        for card in get_player_data(get_turn(), label):
            e.append(dictionary["cards"][card]["display name"])
        globals()[f"view_{label}"].configure(text=f"{label.capitalize()} ({len(get_player_data(get_turn(), label))})")
        CreateToolTip(globals()[f"view_{label}"], "\n".join(e), y_change=35,
                      x_change=0, background="#ffffff", font=("calibri", 9))

    [widget.destroy() for widget in card_frame.winfo_children()]
    counter = 0
    frame = Frame(card_frame)
    frame.pack(side="top")
    key_order = "1 2 3 4 5 6 7 8 9 0 q w e r t y u i o p a s d f g h j k l z x c v b n m".split(" ")
    for card in get_player_data(get_turn(), "hand"):
        if counter == 6:
            frame = Frame(card_frame)
            frame.pack(side="top")
            counter = 0
        counter += 1
        button = Button(frame,
                        text=f" {get_card_data(card, "display name")} {make_super_script(get_card_data(card, "cost"))} ",
                        style=f"{get_card_data(card, "type") if
                        get_card_data(card, "cost") <= get_player_data(get_turn(), "energy")
                        else "grey"}.TButton", command=lambda c=card: choose_target(c), state="disabled" if
            get_player_data(get_turn(), "ai") else "enabled")
        button.pack(side="left", padx=5)
        if counter < len(key_order):
            main.bind(f"<KeyRelease-{key_order[0]}>", lambda event, c=card: choose_target(c, event=event))
            del key_order[0]

        t = get_card_data(card, "description")
        for a in ["damage", "block"]:
            if f"*{a[0]}" in t and a in dictionary["cards"][card]:
                t = t.replace(f"*{a[0]}", f"{get_full_value(card, a)}")

        CreateToolTip(button, f"Costs {get_card_data(card, "cost")} energy\n{t}",
                      y_change=35, x_change=0, background="#ffffff", font=("calibri", 9))

    [widget.destroy() for widget in player_info.winfo_children()]
    label = Label(player_info,
                  text=f"{get_player_data(get_turn(), "name")} | {get_player_data(get_turn(), "class")}{f" {get_player_data(get_turn(), "class upgrade")}" if get_player_data(get_turn(), "class upgrade") else ""}"
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
    tooltip = tooltip + f"{"" if get_player_data(get_turn(), "class upgrade") == 0 else f"\nUpgrade {get_player_data(get_turn(), "class upgrade")}: {get_class_data(class_, "upgrades")[get_player_data(get_turn(), "class upgrade")]}"}\nDeck:\n • {"\n • ".join(sorted(get_class_data(class_, "deck")))}"
    CreateToolTip(label, tooltip, y_change=35, background="#ffffff", font=("calibri", 9))

    counter = 5
    if get_player_data(get_turn(), "skills"):
        for skill in get_player_data(get_turn(), "skills"):
            if counter >= 5:
                frame = Frame(player_info)
                frame.pack(side="top")
                counter = 0
            counter += 1
            if skill == "Spirit Call":
                c = get_player_data(get_turn(), "special")["spirit counter"]
            elif skill == "Mana burst":
                c = get_player_data(get_turn(), "special")["mana"]
            else:
                c = ""
            label = Label(frame, text=f"{skill}{" " if c != "" else ""}{c}", foreground="#4b7dc9", font=("calibri", 10))
            label.pack(side="left", padx=3)
            CreateToolTip(label, dictionary["skills"][skill], background="#ffffff", font=("calibri", 9), x_change=0,
                          y_change=25)

    if get_player_data(get_turn(), "effects"):
        for effect in get_player_data(get_turn(), "effects"):
            if counter >= 5:
                frame = Frame(player_info)
                frame.pack(side="top")
                counter = 0
            counter += 1
            label = Label(frame, text=f"{effect} {get_effect_value(get_turn(), effect)}",
                          foreground="#4b7dc9" if dictionary["effects"][effect]["type"] == "positive" else
                          "#de4765", font=("calibri", 10))
            label.pack(side="left", padx=3)
            CreateToolTip(label,
                          f"{dictionary["effects"][effect]["description"]}\n{"\n".join([f"{get_player_data(get_turn(), "effects")[effect][e]} {e} {effect.capitalize()}" for e in get_player_data(get_turn(), "effects")[effect]])}"
                          .replace("X", f"{get_effect_value(get_turn(), effect)}"),
                          background="#ffffff", font=("calibri", 9), x_change=0, y_change=25)

    frame = Frame(player_info)
    frame.pack(side="top")

    if "Spirit Call" in player_data[get_turn()]["skills"] and player_data[get_turn()]["special"][
        "spirit counter"] == 10:
        def spirit_call():
            discard_hand()
            player_data[get_turn()]["hand"] += ["SPECIAL DAMAGE", "SPECIAL BLOCK", "SPECIAL EFFECT", "SPECIAL KING"]
            player_data[get_turn()]["special"]["spirit counter"] = 0
            player_data[get_turn()]["energy"] = player_data[get_turn()]["turn energy"]
            update_info()

        Button(frame, text="Spirit Call", style="skill.TButton",
               state="disabled" if get_player_data(get_turn(), "ai") else "normal",
               command=spirit_call).pack(side="left", padx=5)

    if "Mana burst" in player_data[get_turn()]["skills"]:
        if get_player_data(get_turn(), "class upgrade") != 2:
            def mana_burst():
                for target in get_turn("other"):
                    damage = get_player_data(get_turn(), "special")["mana"]
                    stored = damage
                    damage -= player_data[target]["block"]
                    player_data[target]["block"] -= stored
                    if player_data[target]["block"] < 0:
                        player_data[target]["block"] = 0
                    if damage < 0:
                        damage = 0
                    player_data[target]["health"] -= damage
                player_data[get_turn()]["special"]["mana"] = 0
                update_info()
        else:
            def mana_burst():
                if "Strength" not in get_player_data(get_turn(), "effects"):
                    player_data[get_turn()]["effects"].update({"Strength": {}})
                if "temporary" not in player_data[get_turn()]["effects"]["Strength"]:
                    player_data[get_turn()]["effects"]["Strength"].update({"temporary": 0})
                player_data[get_turn()]["effects"]["Strength"]["temporary"] += get_player_data(get_turn(), "special")[
                    "mana"]
                player_data[get_turn()]["special"]["mana"] = 0
                update_info()

        Button(frame, text="Mana burst", style="skill.TButton",
               command=mana_burst, state="disabled" if player_data[get_turn()]["special"]["mana"] == 0 or
                                                       get_player_data(get_turn(), "ai") else "normal").pack(
            side="left", padx=5)

    if not frame.winfo_children():
        frame.destroy()

    [widget.destroy() for widget in enemy_info.winfo_children()]
    counter = 0
    frame2 = Frame(enemy_info)
    frame2.pack(side="top")
    for enemy in get_turn("other"):
        if get_player_data(enemy, "health") <= 0:
            continue
        if counter == 4:
            frame2 = Frame(enemy_info)
            frame2.pack(side="top")
            counter = 0
        counter += 1
        frame = Frame(frame2)
        frame.pack(side="left", padx=5, anchor="n")
        label = Label(frame,
                      text=f"{get_player_data(enemy, "name")} | {get_player_data(enemy, "class")}{f" {get_player_data(enemy, "class upgrade")}" if get_player_data(enemy, "class upgrade") else ""}"
                           f"\n{get_player_data(enemy, "health")}/{get_player_data(enemy, "max health")} "
                           f"HP{f" + {get_player_data(enemy, "block")} Block" if get_player_data(enemy, "block") else ""}",
                      font=("calibri", 9), foreground=get_player_data(enemy, "colour"), width=25)
        label.pack(side="top", pady=(10, 0))

        class_ = get_player_data(enemy, "class")
        tooltip = f"{get_class_data(class_, "description")}"
        for skill in get_class_data(class_, "skills"):
            tooltip = tooltip + f"\n{skill}: {dictionary["skills"][skill]}"
        tooltip = tooltip + f"{"" if get_player_data(enemy, "class upgrade") == 0 else f"\nUpgrade {get_player_data(enemy, "class upgrade")}: {get_class_data(class_, "upgrades")[get_player_data(enemy, "class upgrade")]}"}\nDeck:\n • {"\n • ".join(sorted(get_class_data(class_, "deck")))}"
        CreateToolTip(label, f"{get_player_data(enemy, "name")}\n{tooltip}", y_change=35, background="#ffffff",
                      font=("calibri", 9))

        counter2 = 3
        if get_player_data(enemy, "skills"):
            frame3 = Frame(frame)
            frame3.pack(side="top")
            for skill in get_player_data(enemy, "skills"):
                if counter2 >= 3:
                    frame3 = Frame(frame)
                    frame3.pack(side="top")
                    counter2 = 0
                counter2 += 1
                if skill == "Spirit Call":
                    c = get_player_data(enemy, "special")["spirit counter"]
                elif skill == "Mana burst":
                    c = get_player_data(enemy, "special")["mana"]
                else:
                    c = ""
                label = Label(frame3, text=f"{skill}{" " if c != "" else ""}{c}", foreground="#4b7dc9",
                              font=("calibri", 8))
                label.pack(side="left", padx=3)
                CreateToolTip(label, dictionary["skills"][skill], background="#ffffff", font=("calibri", 9), x_change=0,
                              y_change=22)

        if get_player_data(enemy, "effects"):
            if not get_player_data(enemy, "skills"):
                frame3 = Frame(frame)
                frame3.pack(side="top")
            for effect in get_player_data(enemy, "effects"):
                if counter2 >= 3:
                    frame3 = Frame(frame)
                    frame3.pack(side="top")
                    counter2 = 0
                counter2 += 1
                label = Label(frame3, text=f"{effect} {get_effect_value(enemy, effect)}",
                              foreground="#4b7dc9" if dictionary["effects"][effect]["type"] == "positive" else
                              "#de4765", font=("calibri", 8))
                label.pack(side="left", padx=3)
                CreateToolTip(label,
                              f"{dictionary["effects"][effect]["description"]}\n{"\n".join([f"{get_player_data(enemy, "effects")[effect][e]} {e} {effect.capitalize()}" for e in get_player_data(enemy, "effects")[effect]])}"
                              .replace("X", f"{get_effect_value(enemy, effect)}"),
                              background="#ffffff", font=("calibri", 9), x_change=0, y_change=22)

    alive_count = 0
    alive_player = None
    for target in get_turn("all"):
        if get_player_data(target, "health") > 0:
            alive_count += 1
            alive_player = get_player_data(target, "name")
    if alive_count < 2:
        if messagebox.askyesno(title=f"{alive_player if alive_player else get_turn()} wins!",
                               message=f"{alive_player if alive_player else
                               get_turn()} wins!\nPlay again?"):
            restart_program()
        else:
            exit()


# noinspection PyUnusedLocal
def play_card(card_name, targets):
    global c_energy, target
    [w.destroy() for w in target_frame.winfo_children()]
    if get_card_data(card_name, "cost") > get_player_data(get_turn(), "energy"):
        return
    c_energy = player_data[get_turn()]["energy"]
    player_data[get_turn()]["energy"] -= get_card_data(card_name, "cost")
    player_data[get_turn()]["played cards this turn"].append(card_name)
    player_data[get_turn()]["played cards"].append(card_name)
    if "Bleed" in get_player_data(get_turn(), "effects"):
        player_data[get_turn()]["health"] -= round(player_data[get_turn()]["max health"] * (1 / 16))
        if player_data[get_turn()]["health"] < 0:
            player_data[get_turn()]["health"] = 0

    if "spirit counter" in get_player_data(get_turn(), "special") and player_data[get_turn()]["special"][
        "spirit counter"] < 10 and "SPECIAL DAMAGE" not in player_data[get_turn()]["hand"]:
        player_data[get_turn()]["special"]["spirit counter"] += 1

    if mods.get():
        def process_files_in_directory(directory):
            for item in listdir(directory):
                item_path = path.join(directory, item)
                if path.isfile(item_path):
                    exec(open(item_path, "r").read())
                elif path.isdir(item_path):
                    process_files_in_directory(item_path)

        process_files_in_directory(path.abspath("mods/skills/card played check"))

    card = dictionary["cards"][card_name]

    loop = 0
    if not type(targets) is list:
        targets = [targets]
    for target in targets:
        if get_player_data(target, "health") <= 0:
            continue
        loop += 1

        if "effects" in card:
            # "effects": {"Weak": {"amount": 2, "target": "opponent", "duration": "normal/permanent/temporary"}}
            # "effects": {"Weak": {"permanent": 5}}
            for status in card["effects"]:
                if (dictionary["effects"][status]["type"] == "negative" and card["effects"][status][
                    "target"] == "self") or (
                        dictionary["effects"][status]["type"] == "positive" and card["effects"][status][
                    "target"] == "opponent") or (card["effects"][status]["target"] == "self" and loop > 1):
                    continue
                amount = card["effects"][status]["amount"]() if callable(card["effects"][status]["amount"]) else \
                    card["effects"][status]["amount"]
                target_ = get_turn() if card["effects"][status]["target"] == "self" else target
                duration = card["effects"][status]["duration"]

                # "effects": {"normal": 0, "permanent": 0, "temporary": 0}
                if status not in get_player_data(target_, "effects"):
                    player_data[target_]["effects"].update({status: {}})

                if duration not in player_data[target_]["effects"][status]:
                    player_data[target_]["effects"][status].update({duration: 0})

                player_data[target_]["effects"][status][duration] += amount

        if "inflict to all with" in card["details_dict"]:
            # "details_dict": {"inflict to all with": {"inflicted status": "Weak", "checked status": "Burn",
            # "target": "all", "duration": "normal", "amount": 1}}
            target__ = card["details_dict"]["inflict to all with"]["target"]
            targets_ = [get_turn()] if target__ == "self" else target if target__ == "opponent" else get_turn("other")
            for target_ in targets_:
                effect_1 = card["details_dict"]["inflict to all with"]["inflicted status"]
                effect_2 = card["details_dict"]["inflict to all with"]["checked status"]
                duration = card["details_dict"]["inflict to all with"]["duration"]
                amount = card["details_dict"]["inflict to all with"]["amount"]
                if effect_2 in get_player_data(target_, "effects"):
                    if effect_1 not in get_player_data(target_, "effects"):
                        player_data[target_]["effects"].update({effect_1: {}})

                    if duration not in player_data[target_]["effects"][effect_1]:
                        player_data[target_]["effects"][effect_1].update({duration: 0})

                    player_data[target_]["effects"][effect_1][duration] += amount

        if "damage" in card:
            # {"amount": 1, "times": 1, "target": "opponent"}
            damage = card["damage"]["amount"]() if callable(card["damage"]["amount"]) else card["damage"]["amount"]
            target_ = get_turn() if card["damage"]["target"] == "self" else target

            # Addition & subtraction
            damage += get_effect_value(get_turn(), "Strength") if "Strength" in player_data[get_turn()][
                "effects"] else 0

            # Multiplication
            damage *= 2 / 3 if "Weak" in player_data[get_turn()]["effects"] else 1
            damage *= 0.9 if "Beginner's luck" in player_data[target_]["skills"] else 1
            damage *= 4 / 3 if "Vulnerable" in player_data[target_]["effects"] else 1
            if "increase damage if effect" in card["details_dict"] and \
                    card["details_dict"]["increase damage if effect"]["effect"] in get_player_data(target_, "effects"):
                damage *= card["details_dict"]["increase damage if effect"]["amount"]
            damage *= get_player_data(target, "difficulty")[0]
            damage *= get_player_data(get_turn(), "difficulty")[1]

            loop_x = card["damage"]["times"]() if callable(card["damage"]["times"]) else card["damage"]["times"]
            attack_loop = 0
            for x in range(1, loop_x + 1):
                attack_loop += 1
                if mods.get():
                    def process_files_in_directory(directory):
                        for item in listdir(directory):
                            item_path = path.join(directory, item)
                            if path.isfile(item_path):
                                exec(open(item_path, "r").read())
                            elif path.isdir(item_path):
                                process_files_in_directory(item_path)

                    process_files_in_directory(path.abspath("mods/skills/damage dealt check"))

                damage = round(damage)
                if "ignores block" not in card["details"]:
                    stored = damage
                    damage -= player_data[target_]["block"]
                    player_data[target_]["block"] -= stored
                    if player_data[target_]["block"] < 0:
                        player_data[target_]["block"] = 0
                if damage < 0:
                    damage = 0
                player_data[target_]["health"] -= damage

                if "drain" in card["details"]:
                    heal = damage
                    if player_data[get_turn()]["health"] + heal > player_data[get_turn()]["max health"]:
                        heal = player_data[get_turn()]["max health"] - player_data[get_turn()]["health"]
                    player_data[get_turn()]["health"] += heal

                if "Reflect" in get_player_data(target_, "effects") and damage > 0:
                    damage2 = round(damage * get_effect_value(target_, "Reflect") / 10)
                    stored = damage2
                    damage2 -= player_data[get_turn()]["block"]
                    player_data[get_turn()]["block"] -= stored
                    if player_data[get_turn()]["block"] < 0:
                        player_data[get_turn()]["block"] = 0
                    player_data[get_turn()]["health"] -= damage2
                    if player_data[get_turn()]["health"] < 0:
                        player_data[get_turn()]["health"] = 0

                if damage > 0 and "Thorns" in get_player_data(target_, "effects"):
                    damage = get_effect_value(target_, "Thorns")
                    stored = damage
                    damage -= player_data[get_turn()]["block"]
                    player_data[get_turn()]["block"] -= stored
                    if player_data[get_turn()]["block"] < 0:
                        player_data[get_turn()]["block"] = 0
                    player_data[get_turn()]["health"] -= round(damage)
                    if player_data[get_turn()]["health"] < 0:
                        player_data[get_turn()]["health"] = 0

        if "block" in card and not (card["block"]["target"] == "self" and loop > 1):
            # block: {"amount": 3, "target": "self"}
            block, target_ = card["block"]["amount"]() if callable(card["block"]["amount"]) else card["block"][
                "amount"], get_turn() if card["block"]["target"] == "self" else target

            block *= 2 / 3 if "Frail" in player_data[get_turn()]["effects"] else 1

            block += get_effect_value(get_turn(), "Resistance") if "Resistance" in player_data[get_turn()][
                "effects"] else 0

            block = round(block)
            player_data[target_]["block"] += block

        if "heal" in card and not (card["heal"]["target"] == "self" and loop > 1):
            # block: {"amount": 3, "target": "self"}
            health, target_ = card["heal"]["amount"]() if callable(card["heal"]["amount"]) else card["heal"][
                "amount"], get_turn() if card["heal"]["target"] == "self" else target
            if player_data[target_]["health"] + health > player_data[target_]["max health"]:
                health = player_data[target_]["max health"] - player_data[target_]["health"]
            player_data[target_]["health"] += health

        if "draw" in card and not (card["draw"]["loop"] == "self" and loop > 1):
            draw_hand(card["draw"]["amount"]() if callable(card["draw"]["amount"]) else card["draw"]["amount"])

        if "evoke" in card and not (card["evoke"]["target"] == "self" and loop > 1):
            # "evoke": [card "magic card", pile "hand", amount 2, target "self"]
            card_, target_ = card["evoke"]["card"], get_turn() if card["evoke"]["target"] == "self" else target
            [player_data[target_][card["evoke"]["pile"]].append(card_() if callable(card_) else card_) for x in
             range(1, card["evoke"]["amount"] + 1)]

        if "special" in card:
            exec(card["special"])

        if "effects" in card:
            # "effects": {"Weak": {"amount": 2, "target": "opponent", "duration": "normal/permanent/temporary"}}
            # "effects": {"Weak": {"permanent": 5}}
            for status in card["effects"]:
                if not ((dictionary["effects"][status]["type"] == "negative" and card["effects"][status][
                    "target"] == "self") or (
                                dictionary["effects"][status]["type"] == "positive" and card["effects"][status][
                            "target"] == "opponent")) or (card["effects"][status]["target"] == "self" and loop > 1):
                    continue
                amount = card["effects"][status]["amount"]() if callable(card["effects"][status]["amount"]) else \
                    card["effects"][status]["amount"]
                target_ = get_turn() if card["effects"][status]["target"] == "self" else target
                duration = card["effects"][status]["duration"]

                # "effects": {"normal": 0, "permanent": 0, "temporary": 0}
                if status not in get_player_data(target_, "effects"):
                    player_data[target_]["effects"].update({status: {}})

                if duration not in player_data[target_]["effects"][status]:
                    player_data[target_]["effects"][status].update({duration: 0})

                player_data[target_]["effects"][status][duration] += amount + get_effect_value(get_turn(), "Strength")

                if "energy" in card:
                    player_data[get_turn()]["energy"] += card["energy"]() if callable(card["energy"]) else card[
                        "energy"]

            # "effects": {"Weak": [2, "opponent", permanent False, loop False]}
            for status in card["effects"]:
                break  # old code
                amount, target_ = (round(card["effects"][status][0]), get_turn() if card["effects"][status][1] == "self"
                else target)
                if status not in player_data[target_]["effects"] and (
                        not card["effects"][status][3] or (card["effects"][status][3] and loop == 1)):
                    player_data[target_]["effects"][status] = [amount, card["effects"][status][2]]
                elif not card["effects"][status][3] or (card["effects"][status][3] and loop == 1):
                    player_data[target_]["effects"][status][0] += amount
                    player_data[target_]["effects"][status][1] = player_data[target_]["effects"][status][1] \
                        if not player_data[target_]["effects"][status][1] else card["effects"][status][2]

    if "Arsonist" in player_data[get_turn()]["skills"]:
        for p in get_turn("other"):
            effect = "Burn" if get_player_data(get_turn(), "class upgrade") != 3 else "Poison"
            duration = "normal"
            if effect not in get_player_data(p, "effects"):
                player_data[p]["effects"].update({effect: {}})

            if duration not in player_data[p]["effects"][effect]:
                player_data[p]["effects"][effect].update({duration: 0})

            player_data[p]["effects"][effect][duration] += 1

    if "duplicate" in card["details"]:
        player_data[get_turn()]["discard"].append(card_name)

    if card_name in player_data[get_turn()]["hand"]:
        if "remove" in card["details"]:
            player_data[get_turn()]["exile"].append(card_name)
        elif "do not discard" not in card["details"]:
            player_data[get_turn()]["discard"].append(card_name)
        if "do not discard" not in card["details"]:
            player_data[get_turn()]["hand"].remove(card_name)

    del c_energy
    update_info()


def choose_target(card, back=False, event=None):
    if get_card_data(card, "cost") > get_player_data(get_turn(), "energy"):
        return
    [w.destroy() for w in target_frame.winfo_children()]
    if back:
        return
    elif get_card_data(card, "target") == "all opponents" or (get_card_data(card, "target") == "1 opponent" and
                                                              len([i for i in get_turn("other") if
                                                                   get_player_data(i, "health") <= 0]) <= 2):
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
        Button(frame, text="Back", command=lambda: choose_target(card, back=True), style="target.TButton").pack(
            side="left")
        counter = 0
        for x in list(player_data):
            if counter == 4:
                frame = Frame(target_frame)
                frame.pack(side="top")
                counter = 0
            counter += 1
            if get_card_data(card, "target") == "1 opponent" and x in get_turn("other"):
                Style().configure(f"{x}.target.TButton", foreground=get_player_data(x, "colour"))
                Button(frame, text=player_data[x]["name"], command=lambda x=x: play_card(card, [x]),
                       style=f"{x}.target.TButton").pack(side="left", padx=2)


def ai_choice(loops=0, player=None):
    if player is None:
        player = get_turn()
    ai = get_player_data(get_turn(), "ai")
    if dev_features.get():
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

    main.after(500 if not dev_features.get() else 100, lambda: ai_choice(loops + 1))


def get_effect_value(target, effect):
    value = 0
    if effect in player_data[target]["effects"]:
        if "normal" in player_data[target]["effects"][effect]:
            value += player_data[target]["effects"][effect]["normal"]

        if "permanent" in player_data[target]["effects"][effect]:
            value += player_data[target]["effects"][effect]["permanent"]

        if "temporary" in player_data[target]["effects"][effect]:
            value += player_data[target]["effects"][effect]["temporary"]
    return value


def get_full_value(card, key):
    if key not in dictionary["cards"][card]:
        return None
    og_value = get_card_data(card, key)
    if type(og_value) is dict:
        value = og_value["amount"]
    else:
        value = og_value
    if dev_features.get():
        print(value)

    if key == "damage":
        value *= 2 / 3 if "Weak" in player_data[get_turn()]["effects"] else 1
        value += get_effect_value(get_turn(), "Strength") if "Strength" in player_data[get_turn()][
            "effects"] else 1

    elif key == "block":
        value *= 2 / 3 if "Frail" in player_data[get_turn()]["effects"] else 1
        value += get_effect_value(get_turn(), "Resistance") if "Resistance" in player_data[get_turn()][
            "effects"] else 1

    return round(value)


def discard_hand():
    for card in get_player_data(get_turn(), "hand").copy():
        if "constant" not in get_card_data(card, "details"):
            if "disintegrate" not in get_card_data(card, "details"):
                player_data[get_turn()]["discard"].append(card)
            player_data[get_turn()]["hand"].remove(card)


auto = 0
setup()

main.mainloop()
