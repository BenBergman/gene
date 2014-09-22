#!/usr/bin/env python

#from json import dump, dumps, loads
from json import load
from copy import deepcopy
from random import randint
from random import seed
from sys import exit, argv


#def store_bots(bots, filename):
#    with open(filename, 'w') as outfile:
#        dump(serializable_bots(bots), outfile)


def serializable_bots(bots):
    new_dict = []
    for bot in bots:
        new_dict.append(deepcopy(bot.params))

    return new_dict


def load_bots(filename):
    json_data=open(filename)
    data = load(json_data)
    json_data.close()
    bots = []
    for bot_data in data:
        bots.append(Bot(bot_data))

    return bots


def get_top_bots(bots, desired):
    top_bots = []
    for bot in bots:
        if len(top_bots) == 0:
            top_bots.append(bot)
        else:
            i = 0
            for i in range(0, len(top_bots)):
                if bot.average_score() > top_bots[i].average_score():
                    top_bots.insert(i, bot)
                    break
                elif bot.average_score() == top_bots[i].average_score() and len(bot.params.get("scores", {})) > len(top_bots[i].params.get("scores", {})):
                    top_bots.insert(i, bot)
                    break
            if i == len(top_bots):
                top_bots.append(bot)

    return top_bots[:desired]


def get_most_seasoned_bot(bots):
    top_bot = None
    for bot in bots:
        if top_bot == None:
            top_bot = bot
        elif len(bot.params.get("scores", {})) > len(top_bot.params.get("scores", {})):
            top_bot = bot
        elif len(bot.params.get("scores", {})) == len(top_bot.params.get("scores", {})) and bot.average_score() > top_bot.average_score():
            top_bot = bot

    return top_bot

def get_most_seasoned_bots(bots, desired):
    top_bots = []
    for bot in bots:
        if len(top_bots) == 0:
            top_bots.append(bot)
        else:
            i = 0
            for i in range(0, len(top_bots)):
                if len(bot.params.get("scores", {})) >= len(top_bots[i].params.get("scores", {})):
                    top_bots.insert(i, bot)
                    break
            if i == len(top_bots):
                top_bots.append(bot)

    return top_bots[:desired]


class Bot:
    def __init__(self, json_params):
        self.params = json_params

    def bid(self, hand):
        return get_bid_func(self.params["bid_style"])(hand)

    def play(self, allowed_cards, lead_card, round):
        if lead_card == None:
            return get_lead_play_func(self.params["play_style"][round][0])(allowed_cards)
        else:
            return get_second_play_func(self.params["play_style"][round][1])(allowed_cards, lead_card)

    def average_score(self):
        if self.params.get("scores") == None or self.params.get("scores") == {}:
            return 0

        sum = 0
        scores = self.params["scores"]
        for game in scores:
            sum += scores[game]

        return sum / len(scores)

    def save_score(self, game, score):
        self.params.setdefault("scores", {})
        self.params["scores"].setdefault(game, score)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.params["bid_style"] == other.params["bid_style"] and self.params["play_style"] == other.params["play_style"]


def join_bot_lists(bots_a, bots_b):
    joined = []
    for bot in bots_a:
        joined.append(Bot(bot.params))

    for bot in bots_b:
        merged = False
        for i in range(0, len(joined)):
            if bot == joined[i]:
                joined[i].params.setdefault("scores", {}).update(bot.params.get("scores", {}))
                merged = True
                break
        if not merged:
            joined.append(bot)

    return joined


def get_bid_funcs(bid_style=None):
    if bid_style != None:
        (a, b) = bid_style[1:3]
    return [
        lambda h: bid_random(a, b, h),
        lambda h: bid_from_average_value(a, b, h),
        lambda h: bid_avg_of_params(a, b, h),
        ]


def get_bid_func(bid_style):
    return get_bid_funcs(bid_style)[bid_style[0]]


def bid_random(low, high, hand):
    #currently assuming valid range is 1-13
    if low < 1:
        low = 1

    if high > 13:
        high = 13

    if low > high:
        mid = low - (low - high) / 2
        low = high = mid

    return randint(low, high)


def bid_from_average_value(decrease, increase, hand):
    #currently assuming valid range is 1-13
    change = increase - decrease
    sum = 0
    for card in hand:
        sum += card.value

    bid = sum / len(hand) + change
    if bid < 1:
        bid = 1
    elif bid > 13:
        bid = 13

    return bid


def bid_avg_of_params(a, b, hand):
    return (a + b) / 2


def get_lead_play_funcs():
    return [
        lambda a: play_random(a, None),
        lambda a: play_lowest_card(a),
        lambda a: play_four(a, None),
        ]


def get_lead_play_func(play_style):
    return get_lead_play_funcs()[play_style]


def get_second_play_funcs():
    return [
        lambda a, l: play_random(a, l),
        lambda a, l: play_lowest_winning_card(a, l),
        lambda a, l: play_four(a, l),
        ]


def get_second_play_func(play_style):
    return get_second_play_funcs()[play_style]


def play_random(allowed_cards, lead_card):
    idx = randint(0, len(allowed_cards) - 1)
    return list(allowed_cards)[idx]


def play_lowest_winning_card(allowed_cards, lead_card):
    card = lowest_winning_card(allowed_cards, lead_card)
    if card != None:
        return card
    return lowest_non_trump(allowed_cards)


def lowest_winning_card(allowed_cards, lead_card):
    card = lowest_winning_same_suit(allowed_cards, lead_card)
    if card != None:
        return card
    card = lowest_trump(allowed_cards)
    if card != None:
        return card
    return None


def lowest_winning_same_suit(allowed_cards, lead_card):
    candidate_card = None
    for card in allowed_cards:
        if card.suit == lead_card.suit:
            if candidate_card == None:
                candidate_card = card
                continue
            if card.value > lead_card.value:
                if card.value < candidate_card.value:
                    candidate_card = card
    return candidate_card


def lowest_non_trump(allowed_cards):
    candidate_card = None
    for card in allowed_cards:
        if card.suit == "SPADES":
            continue
        if candidate_card == None:
            candidate_card = card
            continue
        if card.value < candidate_card.value:
            candidate_card = card
    return candidate_card


def lowest_trump(allowed_cards):
    candidate_card = None
    for card in allowed_cards:
        if card.suit != "SPADES":
            continue
        if candidate_card == None:
            candidate_card = card
            continue
        if card.value < candidate_card.value:
            candidate_card = card
    return candidate_card


def play_lowest_card(allowed_cards):
    candidate_card = None
    for card in allowed_cards:
        if candidate_card == None:
            candidate_card = card
            continue
        if card.value < candidate_card.value:
            candidate_card = card
    return candidate_card


def play_four(allowed_cards, lead_card):
    if len(allowed_cards) < 4:
        return list(allowed_cards)[-1]
    return list(allowed_cards)[3]



def failure(msg):
    print("!! " + msg)
    exit(1)

def info(msg):
   print("** " + msg)


def main(argv):
    if len(argv) != 2:
        info("usage: " + argv[0] + " <filename>")
        quit

    filename = argv[1]
    try:
        bots = load_bots(filename)
    except:
        info("Could not load file " + filename)
        quit

    top_score = 0
    top_game = 0
    games_played = 0
    total = 0
    for bot in bots:
        scores = bot.params.get("scores", {})
        for game in bot.params.get("scores", {}):
            score = scores[game]
            total += score
            games_played += 1
            if score >= top_score:
                top_score = score
                top_game = game


    print("Bots generated: " + str(len(bots)))
    print("Games played: " + str(games_played))
    print("Top score: " + str(top_score) + "\t in game " + str(top_game))
    print("Combined scores: " + str(total))
    print()
    print("Top bots:")
    top_bots = list(get_top_bots(bots, 5))
    for top_bot in top_bots:
        print("Best bot's average score: " + str(top_bot.average_score()) + "\t games played: " + str(len(top_bot.params.get("scores", {}))))

    print()
    print("Most seasoned bots:")
    most_seasoned_bots = get_most_seasoned_bots(bots, 5)
    for most_seasoned_bot in most_seasoned_bots:
        print("Most games played by single bot: " + str(len(most_seasoned_bot.params.get("scores", {}))) + "\t average score: " + str(most_seasoned_bot.average_score()))


if __name__ == "__main__":
    seed()
    try:
        main(argv)
    except KeyboardInterrupt:
        info("Exiting as requested.")
