#!/usr/bin/env bash

# compiling shell script
python train.py
sleep 5

echo -e "Well, this is the big one. One last job.\n"
sleep 3
echo -e "One train robbery and we can all retire...maybe.\n "
sleep 2
echo -e "It's going to be dangerous though, this job will test all of our intruding and cracking skills\nWe are going to have to review all of the stages of the intrusion,\nas I always have a plan.\n\nThe safe with all of the gold will be locked with 3 4-digit numbers scattered\naround different rooms of the train, so let's get to it."

sleep 10

echo -e "\n\n\nThe numbers you find may be located in a file, but you can use different commands to find them\nIt is one thing to get into the room, but another to find it,\nand they will only get harder to look for, but don't worry, I will help."

sleep 10

echo -e "\n\n\nThere are two different trains set up, with a practice train\nset up on the ports 60-65, corresponding with the order of the carts
using nc 127.0.0.1 <portnum> will let you tackle the cart. The real train uses ports 100-106
with 106 being the vault"

sleep 10

echo -e "\n\n\nSelect an option below to begin review of the different rooms of the train,\nand different intrusions you can implement in this heist.\n Once you are done reviewing run cd thePlanningRoom where all of the tools are\nIf you ever need help, select the help option, but other than that, just review\n
the intrusion plan and then we will move on to the BIG ONE.\n"
sleep 10

# --- Run Python script ---
python3 train_menu.py


