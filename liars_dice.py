"""
liars_dice.py
Samuel Lee
05/11/2021

this is an implementation of a liars dice type game
written primarily for my discord bot
implements my simple dice rolling script
"""
import dice
import random

class Game:
    def __init__(self, mentions, game_number, dice_amount=5):
        self.players = mentions
        self.count = dice_amount
        self.game_number = game_number
        self.sides = 6
        self.player_dice = {}
        self.dice = {
            "1" : 0,
            "2" : 0,
            "3" : 0,
            "4" : 0,
            "5" : 0,
            "6" : 0
        }
        self.plurals = {
            1 : "Ones",
            2 : "Twos",
            3 : "Threes",
            4 : "Fours",
            5 : "Fives",
            6 : "Sixes"
        }
        self.player_bids = {}
        self.player_turn = None
        self.previous_bid = (0,0)
        self.previous_bid_truth = False
        self.player_index = 0
        self.stage = 1


    def roll(self, rolls, sides):
        results = []
        for i in range(rolls):
            results.append(random.randint(1, sides))
        return results


    def roll_dice(self):
        random.shuffle(self.players)
        
        try:
            for i in self.players:
                roll = self.roll(self.count, self.sides)
                for die in roll:
                    name = str(die)
                    self.dice[name] += 1
                self.player_dice[i] = roll
            self.player_turn = self.players[0]

        except Exception as e:
            return False, f"{e}"
        print(self.dice)
        self.stage = 2
        return True, f"The order of players is {self.players}"

    
    def bid(self, player, bid):
        if bid[0] <= self.previous_bid[0] and bid[1] <= self.previous_bid[1]:
            return ("ERR", f"ERR: Invalid bid, you must raise the amount of dice or the face value!")
       
        if bid[1] < 1 or bid[1] > 6:
            return "ERR", f"ERR: You bid out of range of the faces on a six sided die!"

        self.previous_bid = bid
        
        amount = bid[0]
        number = str(bid[1])
        if self.dice[number] >= amount:
            self.previous_bid_truth = True
        else:
            self.previous_bid_truth = False
        
        if self.player_index == len(self.players):
            self.player_index = 0
            self.player_turn = self.players[self.player_index]
        else:
            self.player_index += 1
            self.player_turn = self.players[self.player_index]
        
        if bid[0] == 1:
            return "BID", player, bid, f"{player} bid that there is at least One {bid[1]}"

        return "BID", player, bid, f"{player} bid that there are at least {bid[0]} {self.plurals[bid[1]]}"
        
    
    def accuse(self, player):
        if self.previous_bid is None:
            return ("ERR", f"ERR: There is no previous bid!")
        if self.previous_bid_truth:
            return "END", self.game_end(player, self.players[self.player_index - 1], True)
        return "END", self.game_end(player, self.players[self.player_index - 1], False)


    def game_end(self, player, accused, accurate):
        self.game_over = True
        if accurate:
            return player, f"{player} wrongly accused {accused} of lying! {player} lost!", self.player_dice
        return player, f"{player} correctly accused {accused} of lying! {accused} lost!", self.player_dice

if __name__ == "__main__":
    TEST_GAME = Game(["clarice", "bill", "lecter", "sterling", "buffalo", "hannibal"], 0)
    print(TEST_GAME.roll_dice())
    print(TEST_GAME.bid(TEST_GAME.players[TEST_GAME.player_index], (4,4)))
    print(TEST_GAME.accuse(TEST_GAME.players[TEST_GAME.player_index]))
