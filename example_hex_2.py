"""Example hex with different settings"""

from musical_plot_pie import musical_plot_pie
from musical_plot_hex import musical_plot_hex

location = r'C:\Users\Timothy\Schubert\data.csv'

musical_plot_hex(
    location,
    convertTable=['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    size=5,
    hexSize=1.2
    textSize=0.9,
    figSize=6,
    colorGeneral='Reds',
    centerNote='C#')
