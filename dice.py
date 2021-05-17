"""
dice.py
Samuel Lee
3/29/2021

This is a script that simulates the rolling
of any amount of any sided dice

can be run from the command line with the 
number of sides of dice and amount of rolls 
as the first and second arguments respectively
"""
import random
import sys


def get_user_input(argument, key):
    # gets user input or command line arguments for a specified key
    try:
        user_input = int(sys.argv[argument])
        if user_input > 0:
            return user_input
    except:
        pass
    return input(f"No valid {key} argument detected. Please enter a positive integer number of {key}: ")

def roll(rolls, sides):
    # simulates rolls rolls of sides sided dice
    results = []
    for i in range(rolls):
        results.append(random.randint(1, sides))
    return results


def output(results):
    # outputs the results of the list results
    if len(results) == 1:
        print("Here is the result:")
    else:
        print("Here are the results")
    for i, roll in enumerate(results):
        print(f"roll {i+1} is {roll}")


if __name__ == "__main__":
    # runs this script when called as __main__
    sides = 0
    rolls = 0
    while(True):
        sides = get_user_input(1, "sides")
        rolls = get_user_input(2, "rolls")
        if type(sides) == str and type(rolls) == str:
            if sides.isdigit() and rolls.isdigit():
                if int(sides) > 0 and int(rolls) > 0:
                    sides = int(sides)
                    rolls = int(rolls)
                    break
        else:
            if sides > 0 and rolls > 0:
                break
    results = roll(rolls, sides)
    output(results)
    

