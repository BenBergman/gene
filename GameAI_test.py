from GameAI import *
import unittest

hand = list_to_hand(["C04", "C08", "C12", "D03", "D07", "D11", "H02", "H06", "H10", "S01", "S05", "S09", "S13"])

class TestSequenceFunctions(unittest.TestCase):
    def test_random_bid_bot(self):
        bot = Bot({"bid_style":[0, 6, 6],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(hand), 6)

        bot = Bot({"bid_style":[0, 13, 30],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(hand), 13)

        bot = Bot({"bid_style":[0, 10, 8],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(hand), 9)


    def test_random_play_bot(self):
        bot = Bot({"bid_style":[0, 6, 6],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        one_card_hand = list_to_hand(["H01"])
        self.assertEqual(bot.play(one_card_hand, None, 0), Card("H01"))


    def test_average_bid_bot(self):
        bot = Bot({"bid_style":[1, 3, 2],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(hand), 6)

        one_card_hand = list_to_hand(["H01"])
        bot = Bot({"bid_style":[1, 0, 0],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(one_card_hand), 1)

        bot = Bot({"bid_style":[1, 13, 0],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(hand), 1)

        bot = Bot({"bid_style":[1, 0, 13],
                   "play_style":[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]})

        self.assertEqual(bot.bid(hand), 13)


    def test_play_lowest_winning_card(self):
        test_hand = list_to_hand(["C01", "H02"])
        lead_card = Card("H03")
        allowed_cards = get_allowed_cards(test_hand, lead_card)

        self.assertEqual(play_lowest_winning_card(allowed_cards, lead_card), Card("H02"))


    def test_get_allowed_cards(self):
        allowed = get_allowed_cards(hand, None)
        self.assertEqual(allowed, hand)

        allowed = get_allowed_cards(hand, Card("C05"))
        exp_allowed = list_to_hand(["C04", "C08", "C12", "S01", "S05", "S09", "S13"])
        self.assertEqual(allowed, exp_allowed)


    def test_lowest_winning_card(self):
        lead_card = Card("C05")

        card = lowest_winning_card(get_allowed_cards(hand, lead_card), lead_card)
        self.assertEqual(str(card), "C08")


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


    def test_generate_random_bot(self):
        seed(0)
        bot_a = generate_random_bot()
        seed(0)
        bot_b = generate_random_bot()

        self.assertEqual(bot_a, bot_b)

        bot_a = generate_random_bot()
        bot_b = generate_random_bot()

        self.assertNotEqual(bot_a, bot_b)

        self.assertEqual(len(bot_a.params), 2)
        self.assertEqual(len(bot_a.params["bid_style"]), 3)
        self.assertEqual(len(bot_a.params["play_style"]), 13)
        self.assertEqual(len(bot_a.params["play_style"][0]), 2)


    def test_mutate_bot(self):
        bot_a = generate_random_bot()
        seed(0)
        bot_b = mutate_bot(bot_a)

        self.assertNotEqual(bot_a, bot_b)

        seed(0)
        bot_c = mutate_bot(bot_a)

        self.assertNotEqual(bot_c, bot_b)


    def test_crossover_bots(self):
        bot_a = generate_random_bot()
        bot_b = generate_random_bot()
        bot_c = crossover_bots(bot_a, bot_b)

        self.assertNotEqual(bot_a, bot_c)
        self.assertNotEqual(bot_b, bot_c)


    def test_bot_average_score(self):
        bot = Bot({"scores":{12345: 40, 98760: -100}})
        self.assertEqual(bot.average_score(), -30)

        bot = Bot({"scores":{12345: 40, 98760: -10, 33333: 42}})
        self.assertEqual(bot.average_score(), 24)


    def test_updating_bot_list_scores(self):
        bots = [generate_random_bot(), generate_random_bot(), generate_random_bot()]
        bots[0].save_score(12345, 10)
        bots[0].save_score(12350, 20)
        bots[1].save_score(3, 80)
        bots[0].save_score(12250, 30)

        self.assertEqual(bots[0].average_score(), 20)
        self.assertEqual(bots[1].average_score(), 80)
        self.assertEqual(bots[2].average_score(), None)


if __name__ == '__main__':
    unittest.main()
