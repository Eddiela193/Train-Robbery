GOLD_ART = r'''
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⡏⠻⣿⣿⣿⣿⠏⠀⢸⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⡀⠙⢿⣿⣿⣿⡇⠀⠈⢿⣿⠋⠀⠀⠸⣿⣿⠟⢡⣿⣿⣿⠿⢫⣿⣿
⣿⣿⣿⣿⣧⠀⠀⠙⢿⣿⡇⠀⢀⣀⣁⣀⣀⡀⠀⠛⠁⢠⣿⠿⠋⠁⢀⣿⣿⣿
⣿⣿⠙⢿⣿⣇⠀⠀⠀⠉⠀⢠⡟⠉⠉⠉⠉⢻⡄⠀⠀⠋⠀⠀⠀⠀⣾⣿⣿⣿
⣿⣿⡆⠀⠈⠻⡄⠀⢀⣶⠶⠾⠷⢶⣶⣶⡶⠾⠷⠶⣶⡀⠀⠀⠀⣼⠟⠋⠁⣿
⣿⣿⣧⠀⠀⢀⣀⣀⣼⣇⣀⣀⣀⣀⣿⣿⣀⣀⣀⣀⣸⣧⣀⣀⡈⠀⠀⠀⠀⣿
⣿⠉⠋⠀⠀⣾⠋⠉⠉⠉⠙⣿⡟⠉⠉⠉⠉⢻⣿⠋⠉⠉⠉⠙⣷⠀⠀⠀⠀⣿
⣿⠀⣼⠟⠛⠛⠛⢿⣿⡿⠛⠛⠛⠻⣿⣿⠟⠛⠛⠛⢿⣿⡿⠛⠛⠛⠻⣧⠀⣿
⣿⣴⣿⣤⣤⣤⣤⣼⣿⣧⣤⣤⣤⣤⣿⣿⣤⣤⣤⣤⣼⣿⣧⣤⣤⣤⣤⣿⣦⣿
⣿⠀⠀⠀⣿⣿⡁⠀⠀⠀⢈⣿⣏⠀⠀⠀⠀⣹⣿⡁⠀⠀⠀⢈⣿⣿⠀⠀⠀⣿
⣿⣿⣿⠋⠉⠉⠉⢻⣿⡟⠉⠉⠉⠙⣿⣿⠋⠉⠉⠉⢻⣿⡟⠉⠉⠉⠙⣿⣿⣿
⣿⣿⣿⣶⣶⣶⣶⣾⣿⣷⣶⣶⣶⣶⣿⣿⣶⣶⣶⣶⣾⣿⣷⣶⣶⣶⣶⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
'''

print(GOLD_ART)

# Function of ASCII Gold in python
from IPython.display import display, HTML

def show_ascii(ascii_text, bg="#0b0f17", fg="#e6e6e6", font_size="12px"):
    html = f"""
    <div style="background:{bg}; color:{fg};
                font-family: monospace; white-space: pre;
                padding:4px; border-radius:8px; line-height:1;">
        {ascii_text}
    </div>
    """
    

# Display it
show_ascii(GOLD_ART)
