import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from styles.theme import C
from models.parameters import classify_state

class ResultsPanel(QWidget):
    """Panel lateral moderno para mostrar resultados, métricas y estado en tiempo real."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        self.setFixedWidth(300)
        self.setStyleSheet(f"background-color: {C['bg_light']}; border-left: 1px solid {C['border']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 20, 16, 20)
        main_layout.setSpacing(16)
        
        # Header
        title = QLabel("Métricas Dinámicas")
        title.setStyleSheet(f"color: {C['text_bright']}; font-size: 18px; font-weight: bold; border: none;")
        main_layout.addWidget(title)
        
        # State Card
        self.state_card = QFrame()
        self.state_layout = QVBoxLayout(self.state_card)
        self.state_lbl = QLabel("ESTADO DESCONOCIDO")
        self.state_lbl.setAlignment(Qt.AlignCenter)
        self.state_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.state_val = QLabel("Max: 0.0 cm")
        self.state_val.setAlignment(Qt.AlignCenter)
        self.state_val.setStyleSheet("font-size: 20px; font-weight: bold; color: white; font-family: 'Consolas', monospace;")
        self.state_layout.addWidget(self.state_lbl)
        self.state_layout.addWidget(self.state_val)
        main_layout.addWidget(self.state_card)

        # Frequencies Group
        freq_group = self._create_group("Análisis Modal")
        self.lbl_wn = self._create_row(freq_group, "ωₙ Natural:", "0.0 rad/s")
        self.lbl_fn = self._create_row(freq_group, "fₙ Frecuencia:", "0.0 Hz")
        self.lbl_zeta = self._create_row(freq_group, "ζ Amortiguamiento:", "0.0 %")
        self.lbl_beta = self._create_row(freq_group, "β Resonancia:", "0.0")
        main_layout.addWidget(freq_group)
        
        # TMD Group
        self.tmd_group = self._create_group("Sintonización TMD")
        self.lbl_wntmd = self._create_row(self.tmd_group, "ω_tmd:", "0.0 rad/s")
        self.lbl_sinc = self._create_row(self.tmd_group, "Sintonización:", "0.0")
        self.lbl_mu = self._create_row(self.tmd_group, "μ Razón masa:", "0.0")
        main_layout.addWidget(self.tmd_group)
        
        # Energy and Kinematics Group
        kin_group = self._create_group("Cinemática y Energía")
        self.lbl_rms = self._create_row(kin_group, "Despl. RMS:", "0.0 cm")
        self.lbl_vmax = self._create_row(kin_group, "Velocidad Max:", "0.0 m/s")
        self.lbl_emax = self._create_row(kin_group, "Energía Max:", "0.0 kJ")
        main_layout.addWidget(kin_group)

        main_layout.addStretch()

    def _create_group(self, title_text):
        group = QFrame()
        group.setStyleSheet(f"""
            QFrame {{
                background-color: {C['bg']};
                border: 1px solid {C['border']};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel(title_text)
        title.setStyleSheet(f"color: {C['text_sec']}; font-size: 12px; font-weight: bold; border: none; padding-bottom: 4px; border-bottom: 1px solid {C['border']};")
        layout.addWidget(title)
        
        return group
        
    def _create_row(self, group, label_text, val_text):
        row = QWidget()
        row.setStyleSheet("border: none; background: transparent;")
        r_layout = QHBoxLayout(row)
        r_layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 12px;")
        val = QLabel(val_text)
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        val.setStyleSheet(f"color: {C['text_bright']}; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        r_layout.addWidget(lbl)
        r_layout.addWidget(val)
        group.layout().addWidget(row)
        return val

    def update_metrics(self, params, x_vec, v_vec):
        m, c, k = params['m'], params['c'], params['k']
        
        # Max/RMS
        x_max = np.max(np.abs(x_vec)) if len(x_vec) > 0 else 0.0
        v_max = np.max(np.abs(v_vec)) if len(v_vec) > 0 else 0.0
        x_rms = np.sqrt(np.mean(np.square(x_vec))) if len(x_vec) > 0 else 0.0
        
        # Energy
        energy = 0.5 * k * np.square(x_vec) + 0.5 * m * np.square(v_vec)
        e_max = np.max(energy) if len(energy) > 0 else 0.0

        # Frequencies
        omega_n = np.sqrt(k / m)
        f_n = omega_n / (2.0 * np.pi)
        c_cr = 2.0 * np.sqrt(m * k)
        zeta = c / c_cr
        beta = params['omega_s'] / omega_n
        
        # State
        state_key, state_color, state_label = classify_state(x_max, C)
        self.state_card.setStyleSheet(f"background-color: {state_color}; border-radius: 8px;")
        self.state_lbl.setText(state_label)
        self.state_val.setText(f"Max: {x_max*100:.2f} cm")

        # Update texts
        self.lbl_wn.setText(f"{omega_n:.2f} rad/s")
        self.lbl_fn.setText(f"{f_n:.2f} Hz")
        
        # Zeta formatting
        zc = C['warning'] if zeta < 0.05 else C['safe']
        self.lbl_zeta.setText(f"{zeta*100:.1f} %")
        self.lbl_zeta.setStyleSheet(f"color: {zc}; font-size: 13px; font-weight: bold;")
        
        # Beta formatting
        bc = C['danger'] if 0.85 < beta < 1.15 else C['text_bright']
        self.lbl_beta.setText(f"{beta:.2f}")
        self.lbl_beta.setStyleSheet(f"color: {bc}; font-size: 13px; font-weight: bold;")
        
        # TMD
        if params['tmd_active']:
            self.tmd_group.show()
            omega_tmd = np.sqrt(params['k_d'] / params['m_d'])
            sinc = omega_tmd / omega_n
            mu = params['m_d'] / m
            self.lbl_wntmd.setText(f"{omega_tmd:.2f} rad/s")
            
            sc = C['safe'] if 0.95 < sinc < 1.05 else C['warning']
            self.lbl_sinc.setText(f"{sinc:.3f}")
            self.lbl_sinc.setStyleSheet(f"color: {sc}; font-size: 13px; font-weight: bold;")
            self.lbl_mu.setText(f"{mu:.4f}")
        else:
            self.tmd_group.hide()
            
        # Kinematics
        self.lbl_rms.setText(f"{x_rms*100:.2f} cm")
        self.lbl_vmax.setText(f"{v_max:.2f} m/s")
        self.lbl_emax.setText(f"{e_max/1000:.1f} kJ")
