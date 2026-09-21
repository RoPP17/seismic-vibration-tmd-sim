from matplotlib.colors import LinearSegmentedColormap

# Professional Dark Theme (Reverted to Original)
C = {
    # Fondos
    'bg':             '#0B0F19',
    'bg_light':       '#111827',
    'bg_card':        '#1F2937',
    'bg_input':       '#0F172A',

    # Bordes
    'border':         '#1E293B',
    'border_light':   '#334155',

    # Texto
    'text':           '#E2E8F0',
    'text_sec':       '#94A3B8',
    'text_muted':     '#64748B',
    'text_bright':    '#F8FAFC',

    # Acentos
    'blue':           '#3B82F6',
    'cyan':           '#06B6D4',
    'emerald':        '#10B981',
    'amber':          '#F59E0B',
    'red':            '#EF4444',
    'rose':           '#F43F5E',
    'purple':         '#8B5CF6',
    'gold':           '#FBBF24',
    'indigo':         '#6366F1',

    # Estado
    'safe':           '#10B981',
    'warning':        '#F59E0B',
    'danger':         '#EF4444',
    'collapse':       '#991B1B',

    # Edificio
    'building_base':  '#1E3A5C',
    'window':         '#60A5FA',
    'window_glow':    '#93C5FD',
    'ground':         '#1A1628',
    'ground_line':    '#475569',
    'roof':           '#0F172A',

    # TMD
    'tmd':            '#F59E0B',
    'tmd_light':      '#FCD34D',
    'tmd_dark':       '#B45309',

    # Gráficos
    'line_disp':      '#3B82F6',
    'line_tmd':       '#F59E0B',
    'line_seis':      '#F43F5E',
    'grid':           '#1E293B',

    # Controles
    'slider':         '#2563EB',
    'slider_bg':      '#0F172A',

    # Teoría
    'th_bg':          '#0B0F19',
    'th_card':        '#111827',
    'th_eq':          '#BFDBFE',
    'th_eq_hi':       '#FDE68A',
}

# Colormap de estrés estructural
STRESS_CMAP = LinearSegmentedColormap.from_list('stress', [
    (0.00, '#1E3A5C'),
    (0.30, '#0E7490'),
    (0.55, '#D97706'),
    (0.80, '#DC2626'),
    (1.00, '#991B1B'),
])

GLOBAL_STYLESHEET = f"""
    QMainWindow {{
        background-color: {C['bg']};
    }}
    QWidget {{
        background-color: {C['bg']};
        color: {C['text']};
        font-family: 'Verdana', 'Segoe UI', sans-serif;
    }}
    QScrollBar:vertical {{
        background-color: {C['bg_light']};
        width: 12px;
        border-radius: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {C['border_light']};
        border-radius: 6px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: #475569;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
    
    QScrollBar:horizontal {{
        background-color: {C['bg_light']};
        height: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {C['border_light']};
        border-radius: 6px;
        min-width: 30px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
    
    QToolTip {{
        background-color: {C['bg_card']};
        color: {C['text']};
        border: 1px solid {C['border']};
        border-radius: 4px;
        padding: 6px;
        font-size: 13px;
    }}
"""
