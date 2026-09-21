from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QGroupBox, QFrame, QDialog, QDoubleSpinBox, QSlider, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import numpy as np

from models.parameters import PARAM_CONFIG, PARAMS
from styles.theme import C

class EditDialog(QDialog):
    """Diálogo estilizado para editar valores numéricos (opción manual)."""
    def __init__(self, title, description, value, min_val, max_val,
                 decimals, unit, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Editar: {title}')
        self.setFixedWidth(400)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {C['bg_card']}; }}
            QLabel {{ color: {C['text']}; font-size: 13px; }}
            QDoubleSpinBox {{
                background-color: {C['bg_input']};
                color: {C['text_bright']};
                border: 1px solid {C['blue']};
                border-radius: 6px;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 24px; border: none; background-color: {C['bg']}; }}
            QPushButton#okBtn {{
                background-color: {C['blue']}; color: white; border: none; border-radius: 6px; padding: 10px 28px; font-weight: bold; font-size: 13px;
            }}
            QPushButton#okBtn:hover {{ background-color: #2563EB; }}
            QPushButton#cancelBtn {{
                background-color: {C['bg']}; color: {C['text_sec']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 10px 28px; font-size: 13px;
            }}
            QPushButton#cancelBtn:hover {{ background-color: {C['border']}; }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {C['text_bright']}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {C['text_sec']}; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        self.spin = QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setDecimals(decimals)
        self.spin.setValue(value)
        step = 10 ** (-decimals) if decimals > 0 else 1.0
        self.spin.setSingleStep(step)
        self.spin.setSuffix(f'  {unit}')
        self.spin.setAlignment(Qt.AlignCenter)
        self.spin.setMinimumHeight(48)
        layout.addWidget(self.spin)

        range_lbl = QLabel(f'Rango válido: {min_val} — {max_val} {unit}')
        range_lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 11px;")
        range_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(range_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        cancel_btn = QPushButton('Cancelar')
        cancel_btn.setObjectName('cancelBtn')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton('✓  Aplicar')
        ok_btn.setObjectName('okBtn')
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        ok_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def get_value(self):
        return self.spin.value()

class ParameterCard(QFrame):
    """Tarjeta interactiva para mostrar y editar un parámetro, incluye barra de volumen (Slider)."""
    valueChanged = pyqtSignal(str, float)

    def __init__(self, key, config, initial_value, parent=None):
        super().__init__(parent)
        self.key = key
        self.config = config
        self.display_value = initial_value
        self.setObjectName('paramCard')
        self.setMinimumHeight(110)
        self._setup_ui()

    def _setup_ui(self):
        accent = self.config['accent']
        self.setStyleSheet(f"""
            QFrame#paramCard {{
                background-color: {C['bg_card']};
                border: 1px solid {C['border']};
                border-left: 4px solid {accent};
                border-radius: 8px;
            }}
            QFrame#paramCard:hover {{
                background-color: {C['bg']};
                border-color: {accent};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header with Name and Edit Button
        header_layout = QHBoxLayout()
        self.name_label = QLabel(self.config['label'])
        self.name_label.setStyleSheet(f"color: {C['text_sec']}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        
        self.edit_btn = QPushButton('✎')
        self.edit_btn.setFixedSize(26, 26)
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['bg_input']};
                color: {accent};
                border: 1px solid {C['border']};
                border-radius: 13px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {accent};
                color: white;
            }}
        """)
        self.edit_btn.clicked.connect(self._open_editor)
        header_layout.addWidget(self.edit_btn)
        layout.addLayout(header_layout)

        # Value Row
        value_layout = QHBoxLayout()
        dec = self.config['decimals']
        self.value_label = QLabel(f'{self.display_value:.{dec}f}')
        self.value_label.setStyleSheet(
            f"color: {C['text_bright']}; font-size: 22px; font-weight: bold; font-family: 'Consolas', 'Courier New', monospace; border: none; background: transparent;")
        value_layout.addWidget(self.value_label)

        self.unit_label = QLabel(self.config['unit'])
        self.unit_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 14px; border: none; background: transparent;")
        value_layout.addWidget(self.unit_label)
        value_layout.addStretch()
        layout.addLayout(value_layout)

        # Volume Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setCursor(Qt.PointingHandCursor)
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {C['border']};
                height: 4px;
                background: {C['slider_bg']};
                margin: 2px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {accent};
                border: 1px solid {C['bg']};
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}
        """)
        self._update_slider_from_value()
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)

    def _update_slider_from_value(self):
        """Calculates slider position based on the current value."""
        v_min, v_max = self.config['min'], self.config['max']
        # Evitar división por 0
        if v_max > v_min:
            pos = int(((self.display_value - v_min) / (v_max - v_min)) * 1000)
            self.slider.blockSignals(True)
            self.slider.setValue(np.clip(pos, 0, 1000))
            self.slider.blockSignals(False)

    def _on_slider_changed(self, value):
        """Calculates value based on the slider position."""
        v_min, v_max = self.config['min'], self.config['max']
        new_val = v_min + (value / 1000.0) * (v_max - v_min)
        # Apply decimals
        new_val = round(new_val, self.config['decimals'])
        self.display_value = new_val
        self._update_label()
        self.valueChanged.emit(self.key, new_val)

    def _open_editor(self):
        dlg = EditDialog(
            title=self.config['label'], description=self.config['description'],
            value=self.display_value, min_val=self.config['min'],
            max_val=self.config['max'], decimals=self.config['decimals'],
            unit=self.config['unit'], parent=self.window()
        )
        if dlg.exec_() == QDialog.Accepted:
            new_val = dlg.get_value()
            self.set_value(new_val)
            self.valueChanged.emit(self.key, new_val)

    def _update_label(self):
        dec = self.config['decimals']
        self.value_label.setText(f'{self.display_value:.{dec}f}')

    def set_value(self, value):
        self.display_value = value
        self._update_label()
        self._update_slider_from_value()


class ParameterPanel(QWidget):
    """Panel completo de parámetros organizados por categoría."""
    parametersChanged = pyqtSignal()

    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.params = params
        self.cards = {}
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        header = QLabel('Configuración del Modelo (Controles Activos)')
        header.setStyleSheet(f"color: {C['text_bright']}; font-size: 22px; font-weight: bold;")
        main_layout.addWidget(header)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Personalizado...",
            "Estructura estable",
            "Vibración moderada",
            "Colapso probable"
        ])
        self.preset_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {C['bg_input']};
                color: {C['text_bright']};
                border: 1px solid {C['blue']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {C['bg_card']};
                color: {C['text']};
                selection-background-color: {C['blue']};
                selection-color: white;
            }}
        """)
        self.preset_combo.currentIndexChanged.connect(self._apply_preset)
        main_layout.addWidget(self.preset_combo)

        grid = QGridLayout()
        grid.setSpacing(20)

        categories = [
            ('ESTRUCTURA', C['blue'], 'estructura', 0),
            ('EXCITACIÓN SÍSMICA', C['rose'], 'sismo', 1),
            ('SISTEMA TMD', C['amber'], 'tmd', 2),
        ]

        for cat_name, cat_color, cat_key, col in categories:
            group = QGroupBox(cat_name)
            group.setStyleSheet(f"""
                QGroupBox {{
                    color: {cat_color};
                    border: 1px solid {C['border']};
                    border-radius: 10px;
                    margin-top: 18px;
                    padding: 24px 16px 16px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    background-color: {C['bg']};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 4px 16px;
                    background-color: {C['bg_light']};
                    color: {cat_color};
                    border: 1px solid {C['border']};
                    border-radius: 6px;
                }}
            """)
            group_layout = QVBoxLayout(group)
            group_layout.setSpacing(12)

            for key, cfg in PARAM_CONFIG.items():
                if cfg['category'] != cat_key: continue
                internal_val = self.params[cfg['param_key']]
                display_val = internal_val / cfg['factor']
                card = ParameterCard(key, cfg, display_val, self)
                card.valueChanged.connect(self._on_card_changed)
                self.cards[key] = card
                group_layout.addWidget(card)
            
            group_layout.addStretch()
            grid.addWidget(group, 0, col)

        main_layout.addLayout(grid)
        main_layout.addStretch()

    def _on_card_changed(self, key, display_value):
        cfg = PARAM_CONFIG[key]
        internal_value = display_value * cfg['factor']
        self.params[cfg['param_key']] = internal_value
        self.preset_combo.blockSignals(True)
        self.preset_combo.setCurrentIndex(0) # Personalizado
        self.preset_combo.blockSignals(False)
        self.parametersChanged.emit()

    def _apply_preset(self, index):
        if index == 0: return # Personalizado
        
        if index == 1: # Estructura estable
            self.params['A'] = 1.5
            self.params['k'] = 4000000.0
            self.params['c'] = 30000.0
        elif index == 2: # Vibración moderada
            self.params['A'] = 3.0
            self.params['k'] = 2000000.0
            self.params['c'] = 15000.0
        elif index == 3: # Colapso probable
            self.params['A'] = 8.0
            self.params['k'] = 1000000.0
            self.params['c'] = 5000.0
            # Aproximar a resonancia para asegurar gran desplazamiento
            self.params['omega_s'] = float(np.sqrt(self.params['k'] / self.params['m']))
            
        self.update_display()
        self.parametersChanged.emit()

    def update_display(self):
        for key, card in self.cards.items():
            cfg = PARAM_CONFIG[key]
            internal_value = self.params[cfg['param_key']]
            display_value = internal_value / cfg['factor']
            card.set_value(display_value)
