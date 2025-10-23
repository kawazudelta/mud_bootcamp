# basics.py
# Testing our Character class.

# import the blueprint
from characters import Warrior, Mage

#Create two characters
hero = Warrior("Ike")
enemy = Mage("Goblin Shaman")

#Let them talk
hero.speak("Prepare yourself!")
enemy.speak("Darkness take you!")

#Simple Combat Loop
turn = 1
while hero.hp > 0 and enemy.hp > 0:
    print(f"\n-- Turn {turn} --")
    hero.strike(enemy)        # hero attacks first
    if enemy.hp <= 0:
        break                 # stop when goblin dies
    enemy.cast_spell(hero)        # goblin retaliates
    turn += 1