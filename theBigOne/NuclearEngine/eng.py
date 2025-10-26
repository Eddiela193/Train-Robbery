
LOCO_ART = r'''
                                     (@@@)     (@@@@@)
                               (@@)     (@@@@@@@)        (@@@@@@@)
                         (@@@@@@@)   (@@@@@)       (@@@@@@@@@@@)
                    (@@@)     (@@@@@@@)   (@@@@@@)             (@@@)
               (@@@@@@)    (@@@@@@)                (@)
           (@@@)  (@@@@)           (@@)
        (@@)              (@@@)
       .-.               
       ] [    .-.      _    .-----.                                                                         
     ."   """"   """""" """"| .--`                                              _/\_ 
    (:--:--:--:--:--:--:--:-| [___    .------------------------.           ,~~_  () 
     |C&O  :  :  :  :  :  : [_9_] |'='|.---- NuclearEngine ---.|           |/\ =_//_ ~  
    /|.___________________________|___|'--.___.--.___.--.___.-'|            _( )_( )\~~ 
   / ||_.--.______.--.______.--._ |---\'--\-.-/==\-.-/==\-.-/-'/            \,\  _|\ \~~~
  /__;^=(==)======(==)======(==)=^~^^^ ^^^^(-)^^^^(-)^^^^(-)^^aac              \    \
~~~^~~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~~~~^~~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~~^~~
'''
print(LOCO_ART)

#----Function for Drawing Train work -----------------------------

from IPython.display import display, HTML
import time

def show_ascii_frame(ascii_text, bg="#0b0f17", fg="#e6e6e6", font_size="12px"):
    """Return an HTML block (string) for one frame"""
    return f"""
    <div style="background:{bg}; color:{fg};
                font-family: monospace; white-space: pre;
                padding:10px; border-radius:8px; line-height:1;
                font-size:{font_size};">
        {ascii_text}
    </div>
    """

def animate_ascii(ascii_text, width=80, speed=0.05, loops=2):
    lines = ascii_text.strip("\n").splitlines()
    art_w = max(len(l) for l in lines)
    max_shift = max(0, width - art_w)
    
    #disp = display(HTML(show_ascii_frame(ascii_text)), display_id=True)
    for _ in range(loops):
        for shift in range(0, max_shift):
            pad = "&nbsp;" * shift  # non-breaking spaces for indentation in HTML
            frame = "\n".join(pad + l for l in lines)
            disp.update(HTML(show_ascii_frame(frame)))
            time.sleep(speed)
        for shift in range(max_shift, 0, -1):
            pad = "&nbsp;" * shift
            frame = "\n".join(pad + l for l in lines)
            disp.update(HTML(show_ascii_frame(frame)))
            time.sleep(speed)

animate_ascii(LOCO_ART, width=100, speed=0.03, loops=3)
