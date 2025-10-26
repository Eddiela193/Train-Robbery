#!/usr/bin/env bash

# Greet the user
echo "Hi! Welcome to the selection menu."
echo

# Define the available options and their corresponding files
declare -A OPTIONS
OPTIONS=(
    ["1"]="bufMaps.txt"
    ["2"]="basicSQL.txt"
    ["3"]="dependencies.txt"
    ["4"]="tool_usage.txt"
)

# Show the menu
echo "Please choose an option:"
for key in "${!OPTIONS[@]}"; do
    echo " $key) ${OPTIONS[$key]}"
done
echo " q) Quit"
echo

# Read the user input
read -rp "Enter your choice: " choice

# Handle the choice
if [[ "$choice" == "q" ]]; then
    echo "Goodbye!"
    exit 0
elif [[ -n "${OPTIONS[$choice]}" ]]; then
    file="${OPTIONS[$choice]}"
    if [[ -f "$file" ]]; then
        echo "Displaying contents of $file:"
        echo "----------------------------"
        cat "$file"
    else
        echo "Error: $file not found."
    fi
else
    echo "Invalid option."
fi
