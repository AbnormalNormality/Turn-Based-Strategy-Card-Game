from tkinter import Tk, Frame, Label, StringVar, Text, messagebox
from tkinter.ttk import Button, Style, OptionMenu
from AliasTkFunctions.tkfunctions import CreateToolTip, fix_resolution_issue, change_title_bar_windows_only
from AliasHelpfulFunctions.generalFunctions import minimize_python, make_super_script
from random import choice, randint, shuffle
from keyboard import is_pressed

fix_resolution_issue()
minimize_python()

main = Tk()
screenWidth, screenHeight = main.winfo_screenwidth(), main.winfo_screenheight()
mainWidth, mainHeight = round(screenWidth // 2), round(screenHeight // 2)
main.geometry(f"{mainWidth}x{mainHeight}+{(screenWidth - mainWidth) // 2}+{(screenHeight - mainHeight) // 2}")
main.title("Turn Based Strategy Card Game")
main.after(1, lambda: main.focus_force())
main.protocol("WM_DELETE_WINDOW", exit)
main.resizable(False, False)

card_frame = Frame(main)
card_frame.pack(side="bottom", pady=20)

style = Style()
style.configure("TButton", font=("calibri", 10), justify="center")
style.configure("Custom.TButton", foreground="#cc0000", font=("calibri", 10), justify="center")

side_bar = Frame(main)
side_bar.place(x=mainWidth - 130, y=mainHeight // 3)

turn_label = Label(main, font=("calibri", 16))
turn_label.place(x=10, y=5)

log = Tk()
logWidth, logHeight = round(screenWidth // 4), round(screenHeight // 3)
log.geometry(f"{logWidth}x{logHeight}+{(screenWidth - logWidth) // 2}+{(screenHeight - logHeight) // 2}")
log.title("TBSCG Log")
log.after(1, lambda: log.focus_force())
log.minsize(300, 100)

log_text = Text(log, font=("calibri", 11), wrap="word", state="disabled")
log_text.pack(side="left", fill="both", expand=True)


def show_hand():
    [widget.destroy() for widget in card_frame.winfo_children()]
    frame = None
    counter = 0
    for card in player_info[player_turn]["hand"]:
        if counter == 0:
            frame = Frame(card_frame)
            frame.pack(side="top", pady=5)
        button = Button(frame,
                        text=f" {card} {make_super_script(value(definitions["card_definitions"][card]["cost"]))} ",
                        command=lambda c=card: play_card(c))
        button.pack(side="left", padx=5)
        # Label(button, text="hi").place(y=20)

        tooltip = (
            f"Costs {value(definitions["card_definitions"][card]["cost"])} energy ({definitions["card_definitions"][card]["type"].capitalize()})"
            f"{f"\n{definitions["card_definitions"][card]["tooltip"]}"
            if "tooltip" in definitions["card_definitions"][card] else ""}")
        CreateToolTip(button, tooltip, y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))
        counter += 1
        if counter == 4:
            counter = 0

    update_info_labels()


def draw_hand(draw="handful", card_name=None):
    if draw == "handful":
        draw = player_info[player_turn]["hand size"]
    if draw >= 0:
        if len(player_info[player_turn]["deck"]) < draw:
            for card in player_info[player_turn]["discard"].copy():
                player_info[player_turn]["deck"].append(card)
                player_info[player_turn]["discard"].remove(card)
            shuffle(player_info[player_turn]["deck"])
            shuffle(player_info[player_turn]["discard"])

        for x in range(draw):
            if len(player_info[player_turn]["deck"]) > 0:
                card = choice(player_info[player_turn]["deck"])
                player_info[player_turn]["hand"].append(card)
                player_info[player_turn]["deck"].remove(card)
            else:
                player_info[player_turn]["deck"].extend(player_info[player_turn]["discard"])
                player_info[player_turn]["discard"] = []
                shuffle(player_info[player_turn]["deck"])
                if len(player_info[player_turn]["deck"]) > 0:
                    card = choice(player_info[player_turn]["deck"])
                    player_info[player_turn]["hand"].append(card)
                    player_info[player_turn]["deck"].remove(card)
                else:
                    break
    else:
        for x in range(-draw):
            if len(player_info[player_turn]["hand"]) > 0:
                cards_to_choose_from = [c for c in player_info[player_turn]["hand"] if c != card_name]
                if cards_to_choose_from:
                    card_to_remove = choice(cards_to_choose_from)
                    player_info[player_turn]["discard"].append(card_to_remove)
                    player_info[player_turn]["hand"].remove(card_to_remove)
                else:
                    break
            else:
                break


def end_turn():
    global turn, player_turn
    for card in player_info[player_turn]["hand"].copy():
        if "do not discard" in definitions["card_definitions"][card]["details"]:
            continue

        player_info[player_turn]["discard"].append(card)
        player_info[player_turn]["hand"].remove(card)

    if "Burn" in player_info[player_turn]["effects"]:
        damage = player_info[player_turn]["effects"]["Burn"]
        stored = damage
        damage -= player_info[player_turn]["block"]
        player_info[player_turn]["block"] -= stored
        if player_info[player_turn]["block"] < 0:
            player_info[player_turn]["block"] = 0
        player_info[player_turn]["health"] -= damage

    swap_turn()
    turn += 1
    update_log(f"\nPlayer {player_turn}'s turn!\n", "#ff0000" if player_turn == 1 else "#00b2b2")
    start_turn()


def start_turn():
    player_info[player_turn]["block"] = 0
    player_info[player_turn]["energy"] = player_info[player_turn]["default energy"]

    if "Frost" in player_info[player_turn]["effects"]:
        player_info[player_turn]["energy"] -= player_info[player_turn]["effects"]["Frost"]
        if player_info[player_turn]["energy"] < 1:
            player_info[player_turn]["energy"] = 1

    player_info[player_turn]["cards played this turn"] = 0

    turn_label.configure(text=f"Turn {turn}")

    player_info[player_turn]["hand size"] = 4
    for card in player_info[player_turn]["hand"]:
        if "change max hand size to z" in definitions["card_definitions"][card]["details"]:
            player_info[player_turn]["hand size"] = value(definitions["card_definitions"][card]["z"])

    draw_hand()
    for card in player_info[player_turn]["hand"]:
        if "draw x if in hand" in definitions["card_definitions"][card]["details"]:
            draw_hand(value(definitions["card_definitions"][card]["x"]), card)
        if "gain y energy if in hand" in definitions["card_definitions"][card]["details"]:
            player_info[player_turn]["energy"] += value(definitions["card_definitions"][card]["y"])

    if "Poison" in player_info[player_turn]["effects"]:
        player_info[player_turn]["health"] -= player_info[player_turn]["effects"]["Poison"]
    for status in player_info[player_turn]["effects"].copy():
        if status not in ["Strength"] and isinstance(player_info[player_turn]["effects"][status], int):
            player_info[player_turn]["effects"][status] -= 1
            if not player_info[player_turn]["effects"][status]:
                del player_info[player_turn]["effects"][status]
    update_info()
    show_hand()


def play_card(card, swap=False, delay=False):
    card_name = card
    card = definitions["card_definitions"][card]
    if swap:
        swap_turn()
    if not delay:
        if player_info[player_turn]["energy"] < value(card["cost"]):
            return
        player_info[player_turn]["energy"] -= card["cost"]
        update_log(f"Player {player_turn} plays {card_name}!")
        player_info[player_turn][f"{card["type"]} cards played"] += 1
        player_info[player_turn][f"{card["type"]} cards played this turn"] += 1

    # Card effects

    if "delay" in card:
        delay_loop(card, card_name)
        player_info[player_turn]["discard"].append(card_name)
        player_info[player_turn]["hand"].remove(card_name)
        if swap:
            swap_turn()
        update_info()
        show_hand()
        return

    if "effect" in card:
        for status in card["effect"]:
            amount, target = card["effect"][status][0], get_target(card["effect"][status])
            if status not in player_info[target]["effects"]:
                player_info[target]["effects"][status] = amount
            else:
                player_info[target]["effects"][status] += amount

    if "damage" in card:
        damage, target = value(card["damage"]), get_target(card["damage"])
        if "Berserk" in player_info[player_turn]["skills"] and player_info[player_turn]["health"] <= \
                player_info[player_turn]["max health"] / 1.3:
            damage *= 2
        if "Beginner's Luck" in player_info[other_player]["skills"]:
            damage *= 0.9
        if "Weak" in player_info[player_turn]["effects"]:
            damage = round(damage / 2)
        if "Strength" in player_info[player_turn]["effects"]:
            damage += player_info[player_turn]["effects"]["Strength"]
        if "Temp Strength" in player_info[player_turn]["effects"]:
            damage += player_info[player_turn]["effects"]["Temp Strength"]
        if damage < 0:
            damage = 0
        if "ignore block" not in card["details"]:
            stored = damage
            damage -= player_info[target]["block"]
            player_info[target]["block"] -= stored
            if player_info[target]["block"] < 0:
                player_info[target]["block"] = 0
        damage = round(damage)
        player_info[target]["health"] -= damage
        if player_info[target]["health"] < 0:
            player_info[target]["health"] = 0
        update_log(f"Player {target} loses {damage} HP")

    if "block" in card:
        block, target = value(card["block"]), get_target(card["block"], True)
        player_info[target]["block"] += block
        update_log(f"Player {target} gains {block} block")

    if "energy" in card:
        energy_gained, target = value(card["energy"]), get_target(card["energy"], True)
        player_info[target]["energy"] += energy_gained
        update_log(f"Player {target} gains {energy_gained} energy")

    if "draw" in card:
        draw = value(card["draw"])
        draw_hand(draw)
        update_log(f"Player {player_turn} draws {draw} cards")

    if "health" in card:
        health = value(card["health"])
        player_info[player_turn]["health"] += health
        if player_info[player_turn]["health"] > player_info[player_turn]["max health"]:
            player_info[player_turn]["health"] = player_info[player_turn]["max health"]
        update_log(f"Player {player_turn} gains {health} HP")

    if "custom" in card:
        exec(card["custom"])

    # Card details

    if "exile on play" in card["details"]:
        player_info[player_turn]["exile"].append(card_name)
        player_info[player_turn]["hand"].remove(card_name)

    if not delay and card_name in player_info[player_turn]["hand"]:
        player_info[player_turn]["discard"].append(card_name)
        player_info[player_turn]["hand"].remove(card_name)
    if swap:
        swap_turn()
    update_info_labels()
    update_info()
    show_hand()


def update_info():
    global s_frame, player_info_label, padding, enemy_info_label, s_frame2
    [globals()[v].destroy() if v in ["s_frame", "player_info_label", 'padding',
                                     "enemy_info_label", "s_frame2"] else v for v in globals()]

    if player_info[player_turn]["skills"] or player_info[player_turn]["effects"]:
        s_frame = Label(main)
        s_frame.pack(side="bottom")
        for s in player_info[player_turn]["skills"] + list(player_info[player_turn]["effects"]):
            if s in definitions["skill_definitions"]:
                if s == "Berserk" and player_info[player_turn]["health"] > player_info[player_turn]["max health"] / 2:
                    continue
                label = Label(s_frame, text=s, foreground="#4b7dc9", font=("calibri"))
                label.pack(side="left", padx=5)
                if "tooltip" in definitions["skill_definitions"][s]:
                    CreateToolTip(label, definitions["skill_definitions"][s]["tooltip"], y_change=33, x_change=1,
                                  background="#ffffff", font=("calibri", 9))
            if s in definitions["status_definitions"]:
                label = Label(s_frame, text=f"{s} {player_info[player_turn]["effects"][s]}",
                              foreground="#de4765", font="calibri")
                label.pack(side="left", padx=5)
                if "tooltip" in definitions["status_definitions"][s]:
                    CreateToolTip(label, definitions["status_definitions"][s]["tooltip"], y_change=33, x_change=1,
                                  background="#ffffff", font=("calibri", 9))

        if len(s_frame.winfo_children()) == 0:
            s_frame.destroy()

    player_info_label = Label(main,
                              text=f"Player {player_turn} | {player_info[player_turn]["class"]} Class\n{player_info[player_turn]["health"]} / {player_info[player_turn]["max health"]} HP{f"+ {player_info[player_turn]["block"]} Block" if player_info[player_turn]["block"] else ""} | {player_info[player_turn]["energy"]} Energy",
                              font=("calibri", 10))
    player_info_label.pack(side="bottom")
    CreateToolTip(player_info_label, f"{definitions["deck_definitions"][player_info[player_turn]["class"]]["tooltip"]}",
                  y_change=33, x_change=1,
                  background="#ffffff", font=("calibri", 9))

    padding = Label(main, font=("calibri", 1))
    padding.pack(side="top")

    enemy_info_label = Label(main,
                             text=f"Player {other_player} | {player_info[other_player]["class"]} Class\n{player_info[other_player]["health"]} / {player_info[other_player]["max health"]} HP{f" + {player_info[other_player]["block"]} Block" if player_info[other_player]["block"] else ""}",
                             font=("calibri", 10))
    enemy_info_label.pack(side="top")
    CreateToolTip(enemy_info_label, f"{definitions["deck_definitions"][player_info[other_player]["class"]]["tooltip"]}",
                  y_change=33, x_change=1,
                  background="#ffffff", font=("calibri", 9))

    if player_info[other_player]["skills"] or player_info[other_player]["effects"]:
        s_frame2 = Label(main)
        s_frame2.pack(side="top")
        for s in player_info[other_player]["skills"] + list(player_info[other_player]["effects"]):
            if s in definitions["skill_definitions"]:
                if s == "Berserk" and player_info[other_player]["health"] > player_info[other_player]["max health"] / 2:
                    continue
                label = Label(s_frame2, text=s, foreground="#4b7dc9", font=("calibri"))
                label.pack(side="left", padx=5)
                if "tooltip" in definitions["skill_definitions"][s]:
                    CreateToolTip(label, definitions["skill_definitions"][s]["tooltip"], y_change=33, x_change=1,
                                  background="#ffffff", font=("calibri", 9))
            if s in definitions["status_definitions"]:
                label = Label(s_frame2, text=f"{s} {player_info[other_player]["effects"][s]}",
                              foreground="#de4765", font="calibri")
                label.pack(side="left", padx=5)
                if "tooltip" in definitions["status_definitions"][s]:
                    CreateToolTip(label, definitions["status_definitions"][s]["tooltip"], y_change=33, x_change=1,
                                  background="#ffffff", font=("calibri", 9))

        if len(s_frame2.winfo_children()) == 0:
            s_frame2.destroy()


def swap_turn():
    global player_turn, other_player
    player_turn += 1
    if player_turn > players:
        player_turn = 1
    other_player += 1
    if other_player > players:
        other_player = 1


def update_definition(object, *args):
    global definitions
    if object == "card":
        if selected_card.get() in definitions["card_definitions"]:
            tooltip = f"Costs {value(definitions["card_definitions"][selected_card.get()]["cost"])} energy{f"\n{definitions["card_definitions"][selected_card.get()]["tooltip"]}" if "tooltip" in definitions["card_definitions"][selected_card.get()] else ""}"
            CreateToolTip(card_dictionary, tooltip, y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))
    if object == "status":
        if selected_status.get() in definitions["status_definitions"]:
            tooltip = f"{definitions["status_definitions"][selected_status.get()]["tooltip"]}" if "tooltip" in \
                                                                                                  definitions[
                                                                                                      "status_definitions"][
                                                                                                      selected_status.get()] else ""
            CreateToolTip(status_dictionary, tooltip, y_change=33, x_change=1, background="#ffffff",
                          font=("calibri", 9))
    if object == "deck":
        if selected_deck.get() in definitions["deck_definitions"]:
            tooltip = f"{definitions["deck_definitions"][selected_deck.get()]["tooltip"] if "tooltip" in definitions[
                "deck_definitions"][selected_deck.get()] else ""}\n{f"{definitions["deck_definitions"][selected_deck.get()]["skill"]}: {definitions["skill_definitions"][definitions["deck_definitions"][selected_deck.get()]["skill"]]["tooltip"]}\n" if "skill" in definitions[
                "deck_definitions"][selected_deck.get()] else ""}\n{"\n".join(sorted(definitions["deck_definitions"][selected_deck.get()]["cards"]))}"
            CreateToolTip(deck_dictionary, tooltip, y_change=33, x_change=1, background="#ffffff",
                          font=("calibri", 9))


def update_log(log_message, color="black"):
    log_text.config(state="normal")
    if log_message == "clear0":
        log_text.delete("1.0", "end")
    else:
        log_text.config(state="normal")
        log_text.insert("end", log_message + "\n", f"{color}_text")
        log_text.tag_configure(f"{color}_text", foreground=color)
    log_text.see("end")
    log_text.config(state="disabled")


def value(card):
    if isinstance(card, tuple):
        card = card[0]
    return eval(str(card))


def check_if_dead(forced_death=False):
    if min(player_info[player_turn]["health"], player_info[other_player]["health"]) > 0 and not forced_death:
        main.after(1, check_if_dead)
        return
    if player_info[player_turn]["health"] > player_info[other_player]["health"]:
        winning_player = player_turn
    else:
        winning_player = other_player
    update_log("clear0")
    if not forced_death:
        messagebox.showinfo("TBSCG Player win", f"Player {winning_player} wins!\nPress OK to start a new game")
        update_log(f"Player {winning_player} wins!\nStarting a new game.\n",
                   "#ff0000" if winning_player == 1 else "#00b2b2")
    start_game()


def get_target(object, reverse=False):
    if isinstance(object, tuple):
        if len(object) >= 2:
            object = object[1]
        else:
            object = object[0]
    if not reverse:
        return player_turn if object == "self" else other_player
    else:
        return other_player if object == "opponent" else player_turn


def delay_loop(card, name, delay=None, og_player=None):
    global turn
    if not delay:
        delay = turn + card["delay"]
        print(delay)
        del card["delay"]
    if not og_player:
        og_player = player_turn
    if delay == turn:
        play_card(name, og_player != player_turn, True)
        delay = False
    if delay:
        main.after(1, lambda: delay_loop(card, name, delay, og_player))


def check_for_debug(has_added_cards=False, infinite_health=False, infinite_energy=False):
    if has_added_cards or infinite_health or infinite_energy:
        change_title_bar_windows_only(main)
        main.title(
            f"Debug settings enabled{" | Debug cards" if has_added_cards else ""}{" | Infinite health" if
            infinite_health else ""}{" | Infinite energy" if infinite_energy else ""}")
    if all(is_pressed(key) for key in ["Right Shift", "Up"]) and not has_added_cards:
        debug_cards = {
            "Example card": {"tooltip": "Example tooltip", "copies": 1, "cost": 1},
            "Long tooltip card": {"tooltip": f"Example long tooltip\nMultiple lines", "copies": 1},
            "No tooltip card": {"copies": 1},
            "Damaging card": {"copies": 1, "damage": 2, "tooltip": "Deals 2 damage"},
            "status": {"effect": {"Burn": (5, "opponent")}},
            "delay": {"delay": 1, "effect": {"Burn": (5, "self")}},
            "Mega spell": {"effect": {status: (3, "self" if status in ["Strength"] else "opponent") for status
                                      in definitions["status_definitions"]}},
            "The Everything Card": {"tooltip": "Does EVERYTHING.", "cost": 0,
                                    "effect": {
                                        status: (5, "self" if status in ["Strength", "Temp Strength"] else "opponent")
                                        for status
                                        in definitions["status_definitions"]}, "damage": 10, "copies": 2, "delay": 2,
                                    "details": ["do not discard", "gain y energy if in hand",
                                                "change max hand size to z", "exile", "draw x if in hand"], "y": 2,
                                    "z": 8, "x": 1},
        }
        debug_deck = list(debug_cards)

        for card in debug_deck.copy():
            if "copies" in debug_cards[card]:
                debug_deck.remove(card)
                if debug_cards[card]["copies"] > 0:
                    for x in range(debug_cards[card]["copies"]):
                        debug_deck.append(card)
            else:
                debug_cards[card]["copies"] = 1
            if "cost" not in debug_cards[card]:
                debug_cards[card]["cost"] = 1
            if "details" not in debug_cards[card]:
                debug_cards[card]["details"] = []
            if "type" not in card:
                debug_cards[card]["type"] = "combat"
            debug_cards[card][
                "tooltip"] = (f"{f"{debug_cards[card]["tooltip"]}\n" if "tooltip" in debug_cards[card] else ""}"
                              f"This card is intended for developer use.")

        definitions["card_definitions"].update(debug_cards)
        for p in [player_turn, other_player]:
            player_info[p]["deck"] += list(debug_cards)
        card_dictionary.set_menu(selected_card.get(), *sorted(list(definitions["card_definitions"])))
        update_info_labels()
        has_added_cards = True

    if all(is_pressed(key) for key in ["Right Shift", "Down"]) and not infinite_health:
        infinite_health = True
    if infinite_health:
        if player_info[player_turn]["health"] < 99999:
            player_info[player_turn]["health"] = 99999
            update_info()

    if all(is_pressed(key) for key in ["Right Shift", "Left"]) and not infinite_energy:
        infinite_energy = True
    if infinite_energy:
        if player_info[player_turn]["energy"] < 99999:
            player_info[player_turn]["energy"] = 99999
            update_info()

    main.after(1, lambda: check_for_debug(has_added_cards, infinite_health, infinite_energy))


def update_info_labels():
    [widget.destroy() for widget in side_bar.winfo_children()]

    deck_t = Label(side_bar, text=f"View deck ({len(player_info[player_turn]["deck"])})")
    deck_t.pack(side="top", pady=5)
    shuffled_deck = player_info[player_turn]["deck"]
    shuffle(shuffled_deck)
    CreateToolTip(deck_t, "\n".join(shuffled_deck), y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))
    discard_t = Label(side_bar, text=f"View discard \npile ({len(player_info[player_turn]["discard"])})")
    discard_t.pack(side="top", pady=5)
    shuffled_discard_pile = player_info[player_turn]["discard"]
    shuffle(shuffled_deck)
    CreateToolTip(discard_t, "\n".join(shuffled_discard_pile), y_change=33, x_change=1, background="#ffffff",
                  font=("calibri", 9))


def start_game():
    global player_info, players, turn, player_turn, other_player
    if "player_info" in globals():
        del player_info
    player_info = {}
    players = 2
    for x in range(players):
        player_info.update({x + 1: {"block": 0, "hand size": 4,
                                    "combat cards played": 0, "combat cards played this turn": 0,
                                    "magic cards played": 0, "magic cards played this turn": 0,
                                    "effects": {}, "special": [],
                                    "class": choice(list(definitions["deck_definitions"])),
                                    "deck": [], "hand": [], "discard": [], "exile": []}})

    for p in player_info:
        player_info[p]["deck"] = definitions["deck_definitions"][player_info[p]["class"]]["cards"].copy()
        if "fixed" in definitions["deck_definitions"][player_info[p]["class"]] and \
                definitions["deck_definitions"][player_info[p]["class"]]["fixed"]:
            fixed = True
        else:
            fixed = False

        for card in player_info[p]["deck"].copy():
            if not player_info[p]["deck"].count(card) >= 2 and not fixed:
                player_info[p]["deck"].remove(card)
                for x in range(definitions["card_definitions"][card]["copies"]):
                    player_info[p]["deck"].append(card)

        if "health" in definitions["deck_definitions"][player_info[p]["class"]]:
            player_info[p]["max health"] = definitions["deck_definitions"][player_info[p]["class"]]["health"]
        else:
            player_info[p]["max health"] = 50
        player_info[p]["health"] = player_info[p]["max health"]

        if "energy" in definitions["deck_definitions"][player_info[p]["class"]]:
            player_info[p]["default energy"] = definitions["deck_definitions"][player_info[p]["class"]]["energy"]
        else:
            player_info[p]["default energy"] = 3

        if "skill" in definitions["deck_definitions"][player_info[p]["class"]]:
            player_info[p]["skills"] = [definitions["deck_definitions"][player_info[p]["class"]]["skill"]]
        else:
            player_info[p]["skills"] = []

    turn = 1
    player_turn = choice(list(player_info))
    other_player = (player_turn + 1) if player_turn < players else 1
    update_log(f"Player {player_turn} starts!\n", "#ff0000" if player_turn == 1 else "#00b2b2")

    check_for_debug()
    start_turn()
    check_if_dead()


definitions = {
    "card_definitions": {
        "Slash": {"copies": 5, "damage": 4, "tooltip": "Attack the opponent, \ndealing 4 damage."},
        "Strong Slash": {"copies": 1, "damage": 10,
                         "tooltip": "Attack the opponent with a strong, \nblade dealing 10 damage.", "cost": 2},
        "Block": {"copies": 5, "block": 3, "tooltip": "Block attacks.\n+3 block"},
        "Energy core": {"type": "magic", "copies": 1, "energy": 1,
                        "tooltip": "A core of energy.\n+1 energy and draw 1 card",
                        "cost": 0,
                        "draw": 1},
        "Chance": {"type": "magic", "copies": 1, "damage": "randint(1, 12)",
                   "tooltip": "Deals a random amount of damage between 1 and 12",
                   "cost": 2},
        "Bandaid": {"type": "magic", "copies": 1, "health": 5, "block": 5, "cost": 2,
                    "tooltip": "Gain 5 HP and 5 block."},
        "Storage": {"copies": 1, "cost": 1,
                    "details": ["do not discard", "gain y energy if in hand", "change max hand size to z", "exile"],
                    "y": 1,
                    "z": 3,
                    "tooltip": "You gain 1 energy at the start of your turn if this card is in your hand.\n"
                               "You do not discard this card at the end of your turn."},
        "Flame": {"type": "magic", "copies": 3, "effect": {"Burn": (3, "opponent")},
                  "tooltip": "Apply 3 burn to the opponent."},
        "Francois": {"cost": 3, "effect": {"Burn": (2, "opponent"), "Temp Strength": (1, "self")},
                     "tooltip": "Charlie's bearded dragon Francois,\nDeal 18 damage.\nApply 2 burn to the "
                                "opponent.", "damage": 18},
        "Barricade": {"cost": 1, "tooltip": "Gain 5 block.", "block": 5},
        "Weak Magic": {"type": "magic", "copies": 1, "tooltip": "Apply 2 weak to the opponent.",
                       "effect": {"Weak": (2, "opponent")}},
        "Burn Magic": {"type": "magic", "copies": 1, "tooltip": "Apply 2 burn to the opponent.",
                       "effect": {"Burn": (2, "opponent")}},
        "Poison Magic": {"type": "magic", "copies": 1, "tooltip": "Apply 2 poison to the opponent.",
                         "effect": {"Poison": (2, "opponent")}},
        "Frost Magic": {"type": "magic", "copies": 1, "tooltip": "Apply 1 frost to the opponent.",
                        "effect": {"Frost": (1, "opponent")}},
        "Shield Breaker": {"cost": 3, "damage": 10, "details": ["ignore block"],
                           "tooltip": "Ignores enemy shield.\nDeal 10 damage."},
        "War Axe": {"tooltip": "Deals 3 damage.\nThis attack deals double damage if the opponent is below 50% health.",
                    "damage": "3 * (2 if player_info[other_player][\"health\"] <= player_info[other_player][\"max "
                              "health\"] / 2 else 1)"},
        "Demetrius": {"type": "magic", "cost": 2, "effect": {"Frost": (2, "opponent"), "Temp Strength": (1, "self")},
                      "tooltip": "Lucy's blue-tongue lizard Francois,\nDeal 13 damage.\nApply 2 frost to the "
                                 "opponent.", "damage": 13},
    },
    "status_definitions": {
        "Burn": {"tooltip": "Take X damage at the end of each turn \nwhere X is the number of burn applied."},
        "Poison": {"tooltip": "Take X damage at the start of each turn \nwhere X is the number of poison applied."},
        "Weak": {"tooltip": "Makes you deal 50% less damage."},
        "Strength": {"tooltip": "Makes you deal more damage equal to the number of strength applied."},
        "Frost": {"tooltip": "Makes you start with less energy, equal to the amount of frost (minimum 0)."},
        "Temp Strength": {"tooltip": "Makes you deal more damage equal to the number of strength applied.\nLose 1 "
                                     "Temp Strength at the end of your turn"},
    },
    "deck_definitions": {
        "Beginner": {"tooltip": "A deck built for new players.\nStart with +10 health and +1 energy.", "health": 60,
                     "energy": 4, "skill": "Beginner's Luck", "cards": [
                "Slash",
                "Slash",
                "Slash",
                "Slash",
                "Block",
                "Block",
                "Block",
                "Strong Slash",
                "Bandaid",
                "Barricade",
                "Barricade",
                "Weak Magic",
                "Weak Magic",
                "Burn Magic",
            ], "fixed": True},
        "Barbarian": {"tooltip": "A deck for the daring player.\nStart with -20 health and the Berserk skill.",
                      "health": 40, "skill": "Berserk", "cards": [
                "Slash",
                "Slash",
                "Block",
                "Block",
                "Block",
                "Strong Slash",
                "Shield Breaker",
                "Francois",
                "Demetrius",
                "War Axe",
                "War Axe",
                "War Axe",
            ]},
    },
    "skill_definitions": {
        "Berserk": {"tooltip": "Attacks deal 30% more damage while below 50% health."},
        "Beginner's Luck": {"tooltip": "Take 10% less damage from attacks."},
    },
}

definitions["deck_definitions"].update(
    {"All": {"tooltip": "A deck containing every card.", "cards": list(definitions["card_definitions"])}})

for card_name in list(definitions["card_definitions"]).copy():
    card = definitions["card_definitions"][card_name]
    if "copies" not in card or card["copies"] < 1:
        card["copies"] = 1
    if "cost" not in card:
        card["cost"] = 1
    if "details" not in card:
        card["details"] = []
    if "type" not in card:
        card["type"] = "combat"

end_button = Button(main, text=" End turn ", command=end_turn, style="Custom.TButton")
end_button.place(y=mainHeight - 59, x=mainWidth - 130)
CreateToolTip(end_button, "End your turn.", y_change=33, x_change=1, background="#ffffff", font=("calibri", 9),
              foreground="#cc0000")

restart_button = Button(main, text=" Restart ", command=lambda: check_if_dead(True), style="Custom.TButton")
restart_button.place(y=mainHeight - 59, x=10)
CreateToolTip(restart_button, "Restart the game.\nSpamming this button can\nresult in an error.", y_change=33,
              x_change=1, background="#ffffff", font=("calibri", 9),
              foreground="#cc0000")

selected_card = StringVar()
card_dictionary = OptionMenu(main, selected_card, "Card Dictionary", *sorted(list(definitions["card_definitions"])))
card_dictionary.place(x=5, y=45)
selected_card.trace("w", lambda *args: update_definition("card"))

selected_status = StringVar()
status_dictionary = OptionMenu(main, selected_status, "Status Dictionary",
                               *sorted(list(definitions["status_definitions"])))
status_dictionary.place(x=5, y=80)
selected_status.trace("w", lambda *args: update_definition("status"))

selected_deck = StringVar()
deck_dictionary = OptionMenu(main, selected_deck, "Class Dictionary", *sorted(list(definitions["deck_definitions"])))
deck_dictionary.place(x=5, y=115)
selected_deck.trace("w", lambda *args: update_definition("deck"))

label = Label(main, text="<3", font=("calibri", 8), foreground="magenta")
label.place(x=100, y=15)
CreateToolTip(label, "Game by AliaNormal, with inspiration from\nRogue Adventures and Slay the Spire.\nGitHub: "
                     "github.com/AbnormalNormality", y_change=33, x_change=1, background="#ffffff", font=("calibri", 9))

start_game()
main.mainloop()
