from GameAI import *
import unittest

hand = list_to_hand(["C04", "C08", "C12", "D03", "D07", "D11", "H02", "H06", "H10", "S01", "S05", "S09", "S13"])

class TestSequenceFunctions(unittest.TestCase):
    def test_random_bid_bot(self):
        bot = Bot({"bid_style":[0, 6, 6],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(hand), 6)

        bot = Bot({"bid_style":[0, 13, 30],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(hand), 13)

        bot = Bot({"bid_style":[0, 10, 8],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(hand), 9)


    def test_random_play_bot(self):
        bot = Bot({"bid_style":[0, 6, 6],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        one_card_hand = list_to_hand(["H01"])
        self.assertEqual(bot.play(one_card_hand, None, 0), Card("H01"))


    def test_average_bid_bot(self):
        bot = Bot({"bid_style":[1, 3, 2],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(hand), 6)

        one_card_hand = list_to_hand(["H01"])
        bot = Bot({"bid_style":[1, 0, 0],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(one_card_hand), 1)

        bot = Bot({"bid_style":[1, 13, 0],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(hand), 1)

        bot = Bot({"bid_style":[1, 0, 13],
                   "play_style":[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})

        self.assertEqual(bot.bid(hand), 13)


    def test_get_allowed_cards(self):
        allowed = get_allowed_cards(hand, None)
        self.assertEqual(allowed, hand)

        allowed = get_allowed_cards(hand, Card("C05"))
        exp_allowed = list_to_hand(["C04", "C08", "C12", "S01", "S05", "S09", "S13"])
        self.assertEqual(allowed, exp_allowed)

#    def test_lowest_winning_card(self):
#        lead_card = Card("C05")
#
#        card = lowest_winning_card(get_allowed_cards(hand, lead_card), lead_card)
#        self.assertEqual(str(card), "C08")


    def test_lowest_winning_same_suit(self):
        lead_card = Card("C05")

        card = lowest_winning_same_suit(get_allowed_cards(hand, lead_card), lead_card)
        self.assertEqual(str(card), "C08")


    def test_lowest_non_trump(self):
        lead_card = Card("C05")

        card = lowest_non_trump(get_allowed_cards(list_to_hand(["D01", "D13", "D10", "H04", "H09"]), lead_card))
        self.assertEqual(str(card), "D01")


    def test_lowest_trump(self):
        lead_card = Card("C05")

        card = lowest_trump(get_allowed_cards(list_to_hand(["S02", "S13", "S10", "H04", "H09"]), lead_card))
        self.assertEqual(str(card), "S02")


if __name__ == '__main__':
    unittest.main()
