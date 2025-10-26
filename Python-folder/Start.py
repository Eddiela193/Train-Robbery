pip install pyfiglet

from PIL import Image
import pyfiglet

#ipywidget UI
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output, FileLink
from pathlib import Path
import io, time

# Character ramps (dark->light)
DEFAULT_CHARS = "@%#*+=-:. "
DENSE_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def max_pixel_to_char(pixel_value, chars):
  idx = int((pixel_value / 255) * (len(chars) - 1))
  return chars[idx]

def image_to_ascii(
    img: Image.Image,
    width: int = 100,
    chars: str = DEFAULT_CHARS,
    invert: bool = False, 
    aspect_correction: float = 0.55
) -> str:

  gray = img.convert("L")
  w = max(1, width)
  h = max(1, int(gray.height * (w / gray.width) * aspect_correction))
  gray = gray.resize((w, h))
  if invert:
    gray = Image.eval(gray, lambda p: 255 - p)
  pixels = gray.getdata()
  lines = []
  for y in range(h):
      row = ''.join(map_pixel_to_char(pixels[y * w + x], chars) for x in range(w))
      lines.append(row)
  return "\n".join(lines)

def text_to_ascii(text: str, font: str = "standard") -> str:
    return pyfiglet.figlet_format(text, font=font)

def show_ascii(ascii_text: str, bg="#0b0f17", fg="#e6e6e6", font_size="12px"):
    html = f"""
    <div style="background: {bg}; color: {fg}; 
                font-family: monospace; white-space: pre; 
                padding: 10px; border-radius: 8px; 
                font-size: {font_size}; line-height: 1;">
{ascii_text}
    </div>
    """
    display(HTML(html)) 

banner = text_to_ascii("START", font="slant")
show_ascii(banner, font_size="11px")
