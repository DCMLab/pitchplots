"""Simple example pie using standard settings"""

from musical_plot_pie import musical_plot_pie
from musical_plot_hex import musical_plot_hex

location = r'C:\Users\Timothy\Schubert\data.csv'

musical_plot_pie(
    location,
    dataType='pc'
    convertTable=['C', 'C#', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    tpc=False,
    duration=True,
    fifth=False,
    figSize=8,
    colorGeneral='Greys')
