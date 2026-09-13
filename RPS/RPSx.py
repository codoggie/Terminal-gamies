#!/bin/bash

import os
import time
import random
from enum import Enum

class Choices(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

def clear_screen():
    # Clears screen on Windows ('cls') or Unix/Linux/macOS ('clear')
    os.system('cls' if os.name == 'nt' else 'clear')

print("\n-----------------------------")
print("\n--------START  GAME----------")
print("\n-----------------------------")
print("You know the rules, press q to quit")

def main():
    score = {
            "aiscore": 0,
            "playerscore": 0
            
            }
    # Dictionary defines what beats what
    BEATS = {
        Choices.ROCK: Choices.SCISSORS,
        Choices.PAPER: Choices.ROCK,
        Choices.SCISSORS: Choices.PAPER
    }

    # Defines win messages
    MESSAGES = {
    Choices.ROCK: "Rock smashes scissors",
    Choices.PAPER: "Paper covers rock",
    Choices.SCISSORS: "Scissors cuts paper"
    }

    while True:
        clear_screen()

        print("---------------------------------------------")
        print(f"  AI SCORE: {score['aiscore']}   |   YOUR SCORE: {score['playerscore']}")
        print("---------------------------------------------")
        print(" Rules: Rock, Paper, Scissors. Press 'q' to quit.")
        print("---------------------------------------------")

        usr_input = input("\nEnter a choice (rock, paper, scissors): ").lower().strip()

        # Handle the quit option
        if usr_input == 'q':
            print("\n-------------------")
            print("AI's FINAL SCORE:")
            print(score["aiscore"])
            print("-------------------")
            print("YOUR FINAL SCORE:")
            print(score["playerscore"])
            print("-------------------")
            print("\nThanks for playing! Goodbye.")
            break
    
# using try allows for attempting an action and taking a different path if the action is invalid. In this case, the action is defined from the usr_input variable against the Choices class
        try:
            usr_action = Choices(usr_input)
        except ValueError:
            print("\nInvalid choice! Please try again")
            continue

        ai_action = random.choice(list(Choices))

        if usr_action == ai_action:
            print(f"\nboth players chose {usr_action.value}, it's a tie!")

        elif BEATS[usr_action] == ai_action:
            print(f"\n{MESSAGES[usr_action]}, you win!")
            score["playerscore"] += 1

        else:
            print(f"\n{MESSAGES[ai_action]}, you lose!") 
            score["aiscore"] += 1
        time.sleep(1.5)
main()
