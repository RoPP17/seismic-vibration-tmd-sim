from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar, QFrame, QLabel
from PyQt5.QtCore import Qt

from models.parameters import PARAMS, T_SIM, DT
from styles.theme import C
from ui.simulation_tab import SimulationTab
from widgets.parameter_panel import ParameterPanel
from ui.theory_tab import TheoryTab

class MainWindow(QMainWindow):
    """Ventana principal con sistema de pestañas moderno."""

    def __init__(self):
        super().__init__()
        self.params = dict(PARAMS)
        self.setWindowTitle('Simulación Sísmica Profesional — Análisis Matemático II')
        self.resize(1440, 960)
        self.setMinimumSize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ——— Encabezado ———
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {C['bg_light']};
                border-bottom: 1px solid {C['border']};
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 16, 0, 16)
        header_layout.setSpacing(4)

        title = QLabel('SIMULACIÓN SÍSMICA PROFESIONAL')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {C['text_bright']}; font-size: 20px; font-weight: bold; background: transparent; border: none;")
        header_layout.addWidget(title)

        subtitle = QLabel('Sistema Masa-Resorte-Amortiguador con TMD  ·  RK45')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; background: transparent; border: none;")
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # ——— Pestañas ———
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {C['bg']};
            }}
            QTabBar::tab {{
                background-color: {C['bg_card']};
                color: {C['text_sec']};
                padding: 14px 40px;
                margin-right: 2px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {C['bg']};
                color: {C['blue']};
                border-bottom: 3px solid {C['blue']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {C['bg_input']};
                color: {C['text_bright']};
            }}
        """)

        # Tab 1: Simulación
        self.sim_tab = SimulationTab(self.params)
        self.tabs.addTab(self.sim_tab, '📊  Simulación')

        # Tab 2: Parámetros
        param_scroll = QWidget()
        param_scroll_layout = QVBoxLayout(param_scroll)
        param_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.param_panel = ParameterPanel(self.params)
        param_scroll_layout.addWidget(self.param_panel)
        self.tabs.addTab(param_scroll, '⚙️  Configuración')

        # Tab 3: Teoría
        self.theory_tab = TheoryTab()
        self.tabs.addTab(self.theory_tab, '📐  Fundamentos Matemáticos')

        main_layout.addWidget(self.tabs)

        # ——— Barra de estado ———
        status_bar = QStatusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {C['bg_light']};
                color: {C['text_muted']};
                font-size: 12px;
                border-top: 1px solid {C['border']};
                padding: 6px 16px;
            }}
        """)
        status_bar.showMessage(
            f"  Resolución Numérica: RK45 (Dormand-Prince)  |  T={T_SIM}s  |  dt={DT}s  |  Tolerancias: rtol=1e-6, atol=1e-8"
        )
        self.setStatusBar(status_bar)

        # Conexiones
        self.param_panel.parametersChanged.connect(self._on_params_changed)
        self.sim_tab.paramsReset.connect(self.param_panel.update_display)

    def _on_params_changed(self):
        self.sim_tab.refresh()
