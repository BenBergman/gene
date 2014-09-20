#!/usr/bin/env python

from json import dumps, loads
from random import randint
from time import sleep
from sys import exit, argv

import urllib2

base = "http://gameai.skullspace.ca/api/"

class Card:
    def __init__(self, abbr):
        # Store the abbreviated string used to identify the card, as it's needed
        # when interfacing with the server.
        self.abbr = abbr

        # Parse out the card's suit.
        self.suit = {
            "C": "CLUBS",
            "D": "DIAMONDS",
            "H": "HEARTS",
            "S": "SPADES"
        }[abbr[0]]

        # Parse out the card's value.
        self.value = int(abbr[1:])

    def __str__(self):
        return self.abbr

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.abbr == other.abbr

    def __hash__(self):
        return hash(self.abbr)


class Bot:
    def __init__(self, json_params):
        self.params = json_params

    def bid(self, hand):
        return get_bid_func(self.params["bid_style"])(hand)

    def play(self, allowed_cards, lead_card, round):
        return get_play_func(self.params["play_style"], round)(allowed_cards, lead_card)


def get_bid_funcs(bid_style):
    (a, b) = bid_style[1:3]
    return [
        lambda h: bid_random(a, b, h),
        lambda h: bid_from_average_value(a, b, h),
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


def get_play_funcs():
    return [
        lambda a, l: play_random(a, l)
        ]


def get_play_func(play_style, round):
    return get_play_funcs()[play_style[round]]


def play_random(allowed_cards, lead_card):
    idx = randint(0, len(allowed_cards) - 1)
    return list(allowed_cards)[idx]


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



def failure(msg):
    print("!! " + msg)
    exit(1)

def info(msg):
   print("** " + msg)

def rawapi(method, **params):
    # Collect parameters into a JSON object.
    json = dumps(params)

    # Create the URL of the endpoint.
    url = base + method + "/"

    # Create a new HTTP request to the endpoint.
    req = urllib2.Request(url, json, {"Content-Type": "application/json"})

    # Send the HTTP request.
    stream = urllib2.urlopen(req)
    res = stream.read()
    stream.close()

    return loads(res)

def api(method, **params):
    json = rawapi(method, **params)
    if json["result"] == "failure":
        failure(json["reason"])

    return json

def main(argv):
    # Ensure we've been given a name and a password.
    if len(argv) != 3:
        print("Enter your bot's name:"),
        name = raw_input()
        print("Enter your bot's password:"),
        password = raw_input()
    else:
        name = argv[1]
        password = argv[2]

    # Register the name, which will have no effect if you've already done it.
    rawapi("register", name=name, password=password)

    # Login with the name and password.
    info("Logging in to the server...")
    json = api("login", name=name, password=password)
    info("Logged in.")

    # Store the session from the login for future use.
    session = json["session"]
    info("Received session '" + session + "'.")
    bot_id = json["id"]
    info("Received id '" + str(bot_id) + "'.")

    while True:
        play_a_game(session)

def play_a_game(session):
    # Ask to be given an opponent to play against.
    info("Attempting to start a new game...")
    json = api("new-game", session=session)

    # If there's nobody to play against, start the loop from the top after
    # waiting 5 seconds.
    if json["result"] == "retry":
        print("?? " + json["reason"])
        sleep(5)
        return

    game_id = json["game"]
    info("Starting game " + str(game_id))

    # Create an object to represent the cards we have been dealt.
    cards = json["cards"]
    info("We have started a new game, and have been dealt: " + ", ".join(cards) + ".")
    hand = set([Card(card) for card in cards])

    # Run the game AI.
    new_game(session, hand)

    # Cleanup from our game.
    info("Our role in this game is over, but we need to be sure the server has ended the game before we start a new one.")
    info("If we try to start a new game without the old one being done, the server will reject our request.")
    while True:
        info("Waiting for our game to be over...")
        json = api("status", session=session)
        if json["game"] is None:
            break
        info("The server has ended our game.")
        sleep(5)

def new_game(session, hand):
    # Make a bid, which we'll do randomly, by choosing a number between 1 and
    # 13.
    bid = randint(1, 13)

    # Register our bid with the server.
    info("Attempting to bid " + str(bid) + ".")
    api("bid", session=session, bid=bid)
    info("Our bid has been accepted.")

    # Check the status repeatedly, and if it's our turn play a card, until all
    # cards have been played and the game ends.
    while hand:
        # Always wait 1 second, it may not seem like much but it helps avoid
        # pinning the client's CPU and flooding the server.
        sleep(1)

        # Request the game's status from the server.
        info("Requesting the status of our game...")
        json = api("status", session=session)
        info("Status received.")

        # If the game has ended prematurely, due to a forfeit from your opponent
        # or some other reason, rejoice and find a new opponent.
        if json["game"] is None:
            info("Our game appears to have ended.")
            return

        # If we're still in the bidding process, it's nobody's turn.
        if json["your-turn"] is None:
            info("Our game is still in the bidding phase, we need to wait for our opponent.")
            continue

        # If not it's not our turn yet, jump back to the top of the loop to
        # check the status again.
        if json["your-turn"] == False:
            info("It is currently our opponent's turn, we need to wait for our opponent.")
            continue

        # Finally, it's our turn. First, we have to determine if another card
        # was played first in this round. If so, it restricts our choices.
        if json["opponent-current-card"] is None:
            # We can play any card we want, since we're going first in this
            # round. So all the cards in our hand are allowed.
            allowed_cards = hand
            info("We have the lead this round, so we may choose any card.")
        else:
            # We can only play cards that match the suit of the lead card, since
            # we're going second in this round. Gather together all the cards in
            # our hand that have the appropriate suit.
            allowed_cards = set()
            lead_card = Card(json["opponent-current-card"])
            info("Our opponent has lead this round, so we must try to play a card that matches the lead card's suit: " + lead_card.suit + ".")

            for card in hand:
                if card.suit == lead_card.suit:
                    allowed_cards.add(card)

            # Check if we actually found any cards in our hand with the
            # appropriate suit. If we don't have any, there are no restrictions
            # on the card we can then play.
            if not allowed_cards:
                info("We have no " + lead_card.suit + " in our hand, so we can play any suit we choose.")
                allowed_cards = hand

        # Among the cards that we have determined are valid, according to the
        # rules, choose one to play at random.
        idx = randint(0, len(allowed_cards) - 1)
        card = list(allowed_cards)[idx]
        info("We have randomly chosen " + str(card) + ".")

        # Now that the card has been chosen, play it.
        info("Attempting to play " + str(card) + "...")
        api("play", session=session, card=str(card))
        info("Card has been played.")

        # Remove the card from our hand.
        hand.remove(card)


def list_to_hand(list):
    return set([Card(card) for card in list])


def get_allowed_cards(hand, lead_card):
    if lead_card == None:
        return hand

    allowed_cards = set()
    for card in hand:
        if card.suit == lead_card.suit:
            allowed_cards.add(card)
        elif card.suit == "SPADES":
            allowed_cards.add(card)

    # Check if we actually found any cards in our hand with the
    # appropriate suit. If we don't have any, there are no restrictions
    # on the card we can then play.
    if not allowed_cards:
        allowed_cards = hand

    return allowed_cards


if __name__ == "__main__":
    try:
        main(argv)
    except KeyboardInterrupt:
        info("Exiting as requested.")
