import numpy as np

# Initial System Parameters
PARAMS = {
    'm':          50000.0,      # Structural mass [kg]
    'c':          15000.0,      # Structural damping [N·s/m]
    'k':        2000000.0,      # Structural stiffness [N/m]
    'A':              3.0,      # Seismic acceleration amplitude [m/s²]
    'omega_s':       6.28,      # Seismic angular frequency [rad/s]
    'alpha':         0.15,      # Exponential decay [1/s]
    'm_d':         2500.0,      # TMD mass [kg]
    'c_d':         1200.0,      # TMD damping [N·s/m]
    'k_d':       100000.0,      # TMD stiffness [N/m]
    'tmd_active':    True,
}

T_SIM = 20.0    # Simulation duration [s]
DT    = 0.02    # Time step [s]

PARAM_CONFIG = {
    'm_t': {
        'label': 'm — Masa estructural',
        'description': 'Masa concentrada del edificio.\nRepresenta la inercia total de la estructura.',
        'unit': 't',
        'min': 10.0, 'max': 200.0, 'decimals': 1,
        'default': 50.0,
        'param_key': 'm',
        'factor': 1000.0,
        'category': 'estructura',
        'accent': '#2563EB',
    },
    'c_k': {
        'label': 'c — Amortiguamiento',
        'description': 'Coeficiente de amortiguamiento viscoso.\nModela la disipación de energía por fricción.',
        'unit': 'kN·s/m',
        'min': 1.0, 'max': 50.0, 'decimals': 1,
        'default': 15.0,
        'param_key': 'c',
        'factor': 1000.0,
        'category': 'estructura',
        'accent': '#2563EB',
    },
    'k_M': {
        'label': 'k — Rigidez',
        'description': 'Rigidez lateral de la estructura.\nDetermina la frecuencia natural del edificio.',
        'unit': 'MN/m',
        'min': 0.5, 'max': 10.0, 'decimals': 2,
        'default': 2.0,
        'param_key': 'k',
        'factor': 1e6,
        'category': 'estructura',
        'accent': '#2563EB',
    },
    'A': {
        'label': 'A — Amplitud sísmica',
        'description': 'Amplitud máxima de la aceleración del suelo.\nA = 9.81 m/s² equivale a 1g (muy severo).',
        'unit': 'm/s²',
        'min': 0.5, 'max': 15.0, 'decimals': 1,
        'default': 3.0,
        'param_key': 'A',
        'factor': 1.0,
        'category': 'sismo',
        'accent': '#E11D48',
    },
    'ws': {
        'label': 'ωs — Frecuencia sísmica',
        'description': 'Frecuencia angular dominante del sismo.\nRango típico: 2 — 15 rad/s.',
        'unit': 'rad/s',
        'min': 1.0, 'max': 20.0, 'decimals': 2,
        'default': 6.28,
        'param_key': 'omega_s',
        'factor': 1.0,
        'category': 'sismo',
        'accent': '#E11D48',
    },
    'al': {
        'label': 'α — Decaimiento',
        'description': 'Tasa de decaimiento exponencial del sismo.\nControla la duración efectiva del terremoto.',
        'unit': '1/s',
        'min': 0.0, 'max': 1.0, 'decimals': 2,
        'default': 0.15,
        'param_key': 'alpha',
        'factor': 1.0,
        'category': 'sismo',
        'accent': '#E11D48',
    },
    'md_t': {
        'label': 'md — Masa TMD',
        'description': 'Masa del amortiguador de masa sintonizado.\nTípicamente 1-5% de la masa del edificio.',
        'unit': 't',
        'min': 0.5, 'max': 20.0, 'decimals': 2,
        'default': 2.5,
        'param_key': 'm_d',
        'factor': 1000.0,
        'category': 'tmd',
        'accent': '#D97706',
    },
    'cd': {
        'label': 'cd — Amortiguamiento TMD',
        'description': 'Coeficiente de amortiguamiento del TMD.\nControla la disipación de energía del TMD.',
        'unit': 'N·s/m',
        'min': 100.0, 'max': 5000.0, 'decimals': 0,
        'default': 1200.0,
        'param_key': 'c_d',
        'factor': 1.0,
        'category': 'tmd',
        'accent': '#D97706',
    },
    'kd_k': {
        'label': 'kd — Rigidez TMD',
        'description': 'Rigidez del resorte del TMD.\nDetermina la frecuencia de sintonización.',
        'unit': 'kN/m',
        'min': 10.0, 'max': 500.0, 'decimals': 1,
        'default': 100.0,
        'param_key': 'k_d',
        'factor': 1000.0,
        'category': 'tmd',
        'accent': '#D97706',
    },
}

def classify_state(x_max, theme_colors):
    """Clasifica el estado estructural según desplazamiento máximo."""
    if x_max < 0.05:
        return 'safe',     theme_colors['safe'],     'ESTRUCTURA ESTABLE'
    elif x_max < 0.10:
        return 'warning',  theme_colors['warning'],  'VIBRACIÓN MODERADA'
    elif x_max < 0.20:
        return 'danger',   theme_colors['danger'],   'RIESGO ESTRUCTURAL'
    else:
        return 'collapse', theme_colors['collapse'], 'COLAPSO PROBABLE'
