import sys
import warnings

# Use Qt5Agg as requested explicitly by the original script
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from ui.main_window import MainWindow
from styles.theme import GLOBAL_STYLESHEET

warnings.filterwarnings('ignore')

def main():
    banner = """
======================================================================
  SIMULACIÓN SÍSMICA PROFESIONAL v5.0  —  PyQt5
  Análisis Matemático II  -  Ecuaciones Diferenciales
======================================================================
  SDOF:   m*x'' + c*x' + k*x = F(t)
  F(t) = -m*A*sin(ws*t)*exp(-a*t)
  
  Método: scipy.integrate.solve_ivp  [RK45]
  GUI:    PyQt5 + Matplotlib Interactivo
======================================================================
"""
    try:
        print(banner)
        print('Iniciando interfaz gráfica PyQt5 con tema claro premium...\n')
    except UnicodeEncodeError:
        print('Iniciando simulación sísmica v5.0...\n')

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(GLOBAL_STYLESHEET)

    # Fuente global
    font = QFont('Verdana', 11)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
