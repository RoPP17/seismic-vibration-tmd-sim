from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from styles.theme import C

class ControlsPanel(QFrame):
    """Panel de controles de simulación (reproducción, velocidad)."""
    
    toggleTMD = pyqtSignal()
    togglePause = pyqtSignal()
    triggerReset = pyqtSignal()
    speedChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tmd_active = True
        self.paused = False
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C['bg_light']};
                border: 1px solid {C['border']};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Estilos base de botones para el tema oscuro
        btn_style = f"""
            QPushButton {{
                background-color: {C['bg_card']};
                color: {C['text']};
                border: 1px solid {C['border_light']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {C['bg']};
                border: 1px solid {C['blue']};
            }}
        """

        # Botón TMD
        self.btn_tmd = QPushButton('TMD: ON')
        self.btn_tmd.setCursor(Qt.PointingHandCursor)
        self._style_tmd_btn(self.tmd_active)
        self.btn_tmd.clicked.connect(self._on_tmd_click)
        layout.addWidget(self.btn_tmd)
        
        # Botón Pausa
        self.btn_pause = QPushButton('⏸  Pausa')
        self.btn_pause.setStyleSheet(btn_style)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.clicked.connect(self._on_pause_click)
        layout.addWidget(self.btn_pause)
        
        # Botón Reset
        self.btn_reset = QPushButton('↺  Reiniciar')
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.triggerReset.emit)
        layout.addWidget(self.btn_reset)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"border: 1px solid {C['border']};")
        layout.addWidget(sep)
        
        # Velocidad de simulación
        lbl_speed = QLabel("Velocidad:")
        lbl_speed.setStyleSheet(f"color: {C['text_sec']}; font-size: 13px; font-weight: bold; border: none;")
        layout.addWidget(lbl_speed)
        
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(2, 100)
        self.slider_speed.setValue(7) # Default a 7ms (~144 FPS)
        self.slider_speed.setInvertedAppearance(True) # Mayor valor visual = menor ms = más rápido
        self.slider_speed.setFixedWidth(120)
        self.slider_speed.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {C['border']};
                height: 6px;
                background: {C['slider_bg']};
                margin: 2px 0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {C['slider']};
                border: 1px solid {C['blue']};
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
        """)
        self.slider_speed.valueChanged.connect(self.speedChanged.emit)
        layout.addWidget(self.slider_speed)
        
        layout.addStretch()
        
    def _on_tmd_click(self):
        self.tmd_active = not self.tmd_active
        self._style_tmd_btn(self.tmd_active)
        self.toggleTMD.emit()
        
    def _on_pause_click(self):
        self.paused = not self.paused
        if self.paused:
            self.btn_pause.setText('▶  Reanudar')
            self.btn_pause.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C['blue']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #2563EB; }}
            """)
        else:
            self.btn_pause.setText('⏸  Pausa')
            self.btn_pause.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C['bg_card']};
                    color: {C['text']};
                    border: 1px solid {C['border_light']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {C['bg']}; border: 1px solid {C['blue']}; }}
            """)
        self.togglePause.emit()

    def _style_tmd_btn(self, active):
        if active:
            self.btn_tmd.setText('TMD: ON')
            self.btn_tmd.setStyleSheet(f"""
                QPushButton {{
                    background-color: #064E3B;
                    color: {C['safe']};
                    border: 1px solid {C['safe']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #047857; }}
            """)
        else:
            self.btn_tmd.setText('TMD: OFF')
            self.btn_tmd.setStyleSheet(f"""
                QPushButton {{
                    background-color: #7F1D1D;
                    color: {C['danger']};
                    border: 1px solid {C['danger']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: #991B1B; }}
            """)
