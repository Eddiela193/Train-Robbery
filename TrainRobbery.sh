#!/usr/bin/env bash

echo -e "Well, this is the big one. One last job.\n"
sleep 3
echo -e "One train robbery and we can all retire...maybe.\n "
sleep 2
echo -e "It's going to be dangerous though, this job will test all of our intruding and cracking skills.\nWe are going to have to review all of the stages of the intrusion,\nas I always have a plan.\n\nThe safe with all of the gold will be locked with 3 4-digit numbers scattered\naround different rooms of the train, so let's get to it."

sleep 10

echo -e "\n\n\nThe numbers you find may be located in a chest, but you can use different commands to find them.\nIt is one thing to get into the room, but another to find it,\nand they will only get harder to look for, but don't worry, I will help."

sleep 10

echo -e "\n\n\nSelect an option below to begin review of the different rooms of the train,\nand different intrusions you can implement in this heist.\nIf you ever need help, select the help option, but other than that, just review\n
the intrusion plan and then we will move on to the BIG ONE.\n"
sleep 10

# --- Run Python script ---
python3 train_menu.py

# Capture the exit code
exit_code=$?

# --- Act based on Python return code ---
case $exit_code in
    0)
        echo "Lets try practicing DDOS. To the nuclear engine room!"
        ./engine_room.sh
        ;;
    1)
        echo "Lets try practicing buffer overflows. To the quantum cargo hold!"
        ./passenger_car.sh
        ;;
    2)
        echo "You’re going for the Cargo Hold."
        ./cargo_hold.sh
        ;;
    3)
        echo "You asked for help. Let’s show the instructions again."
        ./help_menu.sh
        ;;
    *)
        echo "Unexpected choice ($exit_code). Exiting."
        exit 1
        ;;
esac
