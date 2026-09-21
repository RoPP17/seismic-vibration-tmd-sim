import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QHBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from models.parameters import PARAMS, T_SIM, DT
from styles.theme import C
from simulation.solver import solve_system, seismic_acceleration
from plots.charts import ChartWidget, style_axis
from plots.building_renderer import draw_building
from widgets.results_panel import ResultsPanel
from widgets.controls import ControlsPanel
from utils.exports import export_to_csv

class SimulationTab(QWidget):
    """Pestaña principal con edificio animado, gráficos interactivos y controles."""
    paramsReset = pyqtSignal()

    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.params = params
        self.frame = 0
        
        self.t_vec = []
        self.x_vec = []
        self.v_vec = []
        self.xd_vec = []
        self.seis_vec = []
        
        self._setup_ui()
        self._solve()
        self._init_plots()

        # Timer de animación (7ms ≈ 144 fps)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(7)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Barra superior con Controles y Exportación
        top_bar = QHBoxLayout()
        self.controls = ControlsPanel()
        self.controls.toggleTMD.connect(self._toggle_tmd)
        self.controls.togglePause.connect(self._toggle_pause)
        self.controls.triggerReset.connect(self._reset)
        self.controls.speedChanged.connect(self._change_speed)
        
        btn_export = QPushButton("📥 Exportar CSV")
        btn_export.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['bg']}; color: {C['blue']};
                border: 1px solid {C['blue']}; border-radius: 6px;
                padding: 8px 16px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {C['blue']}; color: white; }}
        """)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.clicked.connect(self._export_data)

        top_bar.addWidget(self.controls)
        top_bar.addStretch()
        top_bar.addWidget(btn_export)
        main_layout.addLayout(top_bar)

        # Área principal (Splitter Horizontal)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{ background-color: {C['border']}; width: 2px; }}
        """)

        # Panel Izquierdo: Edificio
        self.bld_chart = ChartWidget(width=4, height=5, facecolor=C['bg'], show_toolbar=False)
        self.bld_chart.canvas.fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.01)
        splitter.addWidget(self.bld_chart)

        # Panel Central: Gráficos
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(8)

        self.disp_chart = ChartWidget(width=7, height=3, facecolor=C['bg_light'], show_toolbar=True)
        self.disp_chart.canvas.fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.16)
        charts_layout.addWidget(self.disp_chart)

        self.seis_chart = ChartWidget(width=7, height=3, facecolor=C['bg_light'], show_toolbar=True)
        self.seis_chart.canvas.fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.20)
        charts_layout.addWidget(self.seis_chart)

        splitter.addWidget(charts_widget)

        # Panel Derecho: Resultados (Max, RMS, Energía)
        self.results_panel = ResultsPanel()
        splitter.addWidget(self.results_panel)

        # Proporciones
        splitter.setSizes([350, 700, 300])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 6)
        splitter.setStretchFactor(2, 2)

        main_layout.addWidget(splitter, 1)

    def _solve(self):
        t, x, v, xd = solve_system(self.params)
        self.t_vec = t
        self.x_vec = x
        self.v_vec = v
        self.xd_vec = xd
        
        self.seis_vec = np.array([
            seismic_acceleration(ti, self.params['A'], self.params['omega_s'], self.params['alpha'])
            for ti in t
        ])

        self.results_panel.update_metrics(self.params, self.x_vec, self.v_vec)

    def _init_plots(self):
        # Desplazamiento
        ax_disp = self.disp_chart.ax
        style_axis(ax_disp, ylabel='Desplazamiento [m]', title='Respuesta Dinámica: x(t)')
        self.line_x, = ax_disp.plot(self.t_vec, self.x_vec, color=C['line_disp'], lw=1.8, label='Edificio x(t)', zorder=3)
        
        if self.xd_vec is not None:
            self.line_xd, = ax_disp.plot(self.t_vec, self.xd_vec, color=C['line_tmd'], lw=1.5, ls='--', alpha=0.9, label='TMD xd(t)', zorder=3)
        else:
            self.line_xd, = ax_disp.plot([], [], color=C['line_tmd'], lw=1.5, ls='--', label='TMD xd(t)', zorder=3)

        # Damage zones (Light theme friendly)
        ax_disp.axhspan(0.05, 0.20, alpha=0.08, color=C['warning'], zorder=1)
        ax_disp.axhspan(-0.20, -0.05, alpha=0.08, color=C['warning'], zorder=1)
        ax_disp.axhspan(0.10, 0.20, alpha=0.10, color=C['danger'], zorder=1)
        ax_disp.axhspan(-0.20, -0.10, alpha=0.10, color=C['danger'], zorder=1)
        for th, col in [(0.05, C['safe']), (0.10, C['warning']), (0.20, C['danger'])]:
            ax_disp.axhline(th, color=col, lw=1.0, ls=':', alpha=0.6)
            ax_disp.axhline(-th, color=col, lw=1.0, ls=':', alpha=0.6)

        ax_disp.legend(loc='upper right', facecolor=C['bg_light'], edgecolor=C['border'], labelcolor=C['text'], fontsize=9, framealpha=0.9)

        # Time indicators
        self.vline1 = ax_disp.axvline(0, color=C['blue'], lw=1.5, alpha=0.6, zorder=5)
        self.vline2 = self.seis_chart.ax.axvline(0, color=C['blue'], lw=1.5, alpha=0.6, zorder=5)

        # Sismo
        ax_seis = self.seis_chart.ax
        style_axis(ax_seis, xlabel='Tiempo [s]', ylabel='Aceleración [m/s²]', title='Excitación Sísmica: a_suelo(t)')
        self.line_s, = ax_seis.plot(self.t_vec, self.seis_vec, color=C['line_seis'], lw=1.5, zorder=3)
        self.fill_s = ax_seis.fill_between(self.t_vec, self.seis_vec, 0, color=C['line_seis'], alpha=0.15, zorder=2)

        self._update_lims()
        
        self.bld_chart.canvas.draw()
        self.disp_chart.canvas.draw()
        self.seis_chart.canvas.draw()

    def _update_lims(self):
        xm = max(0.04, np.max(np.abs(self.x_vec))) * 1.35
        self.disp_chart.ax.set_xlim(0, T_SIM)
        self.disp_chart.ax.set_ylim(-xm, xm)
        am = max(0.5, np.max(np.abs(self.seis_vec))) * 1.2
        self.seis_chart.ax.set_xlim(0, T_SIM)
        self.seis_chart.ax.set_ylim(-am, am)

    def _animate(self):
        n = len(self.t_vec)
        if n == 0: return

        if not self.controls.paused:
            self.frame = (self.frame + 1) % n

        x_now  = self.x_vec[self.frame]
        xd_now = self.xd_vec[self.frame] if self.xd_vec is not None else None
        t_now  = self.t_vec[self.frame]

        # Draw building
        # State color update
        xi = abs(x_now)
        state_col = C['safe'] if xi < 0.05 else C['warning'] if xi < 0.10 else C['danger']
        
        draw_building(self.bld_chart.ax, x_now, xd_now, self.params, state_col, t_now)
        self.bld_chart.canvas.draw_idle()

        # Update lines
        self.vline1.set_xdata([t_now, t_now])
        self.vline2.set_xdata([t_now, t_now])
        self.line_x.set_color(state_col)

        self.disp_chart.canvas.draw_idle()
        self.seis_chart.canvas.draw_idle()

    def refresh(self):
        """Re-resuelve y actualiza todos los gráficos."""
        self._solve()
        self.frame = 0
        
        self.line_x.set_data(self.t_vec, self.x_vec)
        if self.xd_vec is not None:
            self.line_xd.set_data(self.t_vec, self.xd_vec)
        else:
            self.line_xd.set_data([], [])

        self.line_s.set_data(self.t_vec, self.seis_vec)
        self.fill_s.remove()
        self.fill_s = self.seis_chart.ax.fill_between(self.t_vec, self.seis_vec, 0, color=C['line_seis'], alpha=0.15, zorder=2)

        self._update_lims()
        
        self.disp_chart.canvas.draw_idle()
        self.seis_chart.canvas.draw_idle()

    def _toggle_tmd(self):
        self.params['tmd_active'] = not self.params['tmd_active']
        self.refresh()
        self.paramsReset.emit()

    def _toggle_pause(self):
        pass # Handled by controls panel state

    def _change_speed(self, value):
        # Slider is inverted: value 10 to 100. Let's make it intuitive.
        # Wait, the slider provides delay in ms.
        self.timer.setInterval(value)

    def _reset(self):
        for k, v in PARAMS.items():
            self.params[k] = v
        self.controls.tmd_active = True
        self.controls._style_tmd_btn(True)
        self.refresh()
        self.paramsReset.emit()

    def _export_data(self):
        was_paused = self.controls.paused
        self.controls.paused = True
        export_to_csv(self, self.t_vec, self.x_vec, self.v_vec, self.seis_vec, self.xd_vec)
        self.controls.paused = was_paused
