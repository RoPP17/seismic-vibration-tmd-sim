import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
import matplotlib.pyplot as plt

from styles.theme import C

# Configure Matplotlib fonts
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Verdana', 'Segoe UI', 'Inter', 'Arial', 'Helvetica', 'DejaVu Sans']
matplotlib.rcParams['mathtext.fontset'] = 'cm'

class MplCanvas(FigureCanvasQTAgg):
    """Canvas para embeber figuras de Matplotlib en PyQt5."""
    def __init__(self, parent=None, width=5, height=4, dpi=100, facecolor=C['bg']):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=facecolor)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

class ChartWidget(QWidget):
    """Contenedor de gráfico interactivo con toolbar."""
    def __init__(self, width=5, height=4, dpi=100, facecolor=C['bg'], parent=None, show_toolbar=True):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.canvas = MplCanvas(self, width, height, dpi, facecolor)
        self.ax = self.canvas.fig.add_subplot(111)
        
        self.layout.addWidget(self.canvas)
        
        if show_toolbar:
            self.toolbar = NavigationToolbar2QT(self.canvas, self)
            self.toolbar.setStyleSheet(f"background: {C['bg']}; border: none;")
            self.layout.addWidget(self.toolbar)

def style_axis(ax, xlabel='', ylabel='', title=''):
    """Aplica estilo profesional oscuro a un eje de gráficos."""
    ax.set_facecolor(C['bg'])
    ax.tick_params(colors=C['text_sec'], labelsize=9, which='both',
                   direction='in', length=4, width=0.8)
    for sp in ax.spines.values():
        sp.set_color(C['border'])
        sp.set_linewidth(1.0)
    
    ax.grid(True, color=C['grid'], linewidth=0.8, alpha=0.8,
            which='major', linestyle='-')
    ax.minorticks_on()
    ax.grid(True, color=C['grid'], linewidth=0.4, alpha=0.5,
            which='minor', linestyle='--')
            
    if xlabel:
        ax.set_xlabel(xlabel, color=C['text'], fontsize=11, labelpad=6, fontweight='bold')
    if ylabel:
        ax.set_ylabel(ylabel, color=C['text'], fontsize=11, labelpad=6, fontweight='bold')
    if title:
        ax.set_title(title, color=C['text_bright'], fontsize=13,
                     fontweight='bold', pad=12)
