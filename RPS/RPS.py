import os
import time
import random
from enum import Enum

class Choices(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


def main():
        # Clears screen on Windows ('cls') or Unix/Linux/macOS ('clear')
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\n-----------------------------")
    print("\n--------START  GAME----------")
    print("\n-----------------------------")
    print("You know the rules, press q to quit")

    usr_input = input("\nEnter a choice (rock, paper, scissors): ").lower()
    
# using try allows for attempting an action and taking a different path if the action is invalid. In this case, the action is defined from the usr_input variable against the Choices class
    try:
        usr_action = Choices(usr_input)
    except ValueError:
        print("\nInvalid choice! Please try again")
        return

    ai_action = random.choice(list(Choices))

    print(f"\nYou chose: {usr_action.value}")
    print(f"\nAI chose: {ai_action.value}")

    if usr_action == ai_action:
        print(f"\n\nBoth players selected {usr_action.value}. It's a tie!")

    elif usr_action == Choices.ROCK:
        if ai_action == Choices.SCISSORS:
            print("\n\nRock smashes scissors, you win!")

        else:
            print("\n\nPaper covers rock! you lose.")

    elif usr_action == Choices.PAPER:
        if ai_action == Choices.ROCK:
            print("\n\nPaper covers rock, you win!")

        else:
            print("\n\nScissors cuts paper! you lose.")

    elif usr_action == Choices.SCISSORS:
        if ai_action == Choices.PAPER:
            print("\n\nScissors cuts paper, you win!")

        else:
            print("\n\nRock smashes scissors! you lose.")
    
main()
