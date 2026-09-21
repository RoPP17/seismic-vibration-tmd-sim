"""
================================================================================
  SIMULACIÓN SÍSMICA PROFESIONAL v3.0
  Análisis Matemático II — Ecuaciones Diferenciales
================================================================================

  Sistema Masa-Resorte-Amortiguador con TMD (Tuned Mass Damper)

  MODELO MATEMÁTICO:
    SDOF:   m·x'' + c·x' + k·x = F(t)
            F(t) = -m · A · sin(ws·t) · exp(-a·t)

    2DOF:   m·x''  + c·x'  + k·x  - cd·(xd'-x') - kd·(xd-x) = F(t)
            md·xd'' + cd·(xd'-x') + kd·(xd-x)               = 0

  Solución numérica: scipy.integrate.solve_ivp  (RK45)

  Autor: Simulación Educativa — Ecuaciones Diferenciales
================================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, Circle
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from scipy.integrate import solve_ivp
import warnings

warnings.filterwarnings('ignore')
matplotlib.rcParams['toolbar'] = 'None'
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Helvetica',
                                           'DejaVu Sans']
matplotlib.rcParams['mathtext.fontset'] = 'cm'

# =============================================================================
# PALETA DE COLORES — Tema Oscuro Premium v3
# =============================================================================

C = {
    # —— Fondos ——
    'bg':             '#0B0F19',
    'bg_light':       '#111827',
    'bg_card':        '#1F2937',
    'bg_input':       '#0F172A',

    # —— Bordes ——
    'border':         '#1E293B',
    'border_light':   '#334155',

    # —— Texto ——
    'text':           '#E2E8F0',
    'text_sec':       '#94A3B8',
    'text_muted':     '#64748B',
    'text_bright':    '#F8FAFC',

    # —— Acentos ——
    'blue':           '#3B82F6',
    'cyan':           '#06B6D4',
    'emerald':        '#10B981',
    'amber':          '#F59E0B',
    'red':            '#EF4444',
    'rose':           '#F43F5E',
    'purple':         '#8B5CF6',
    'gold':           '#FBBF24',
    'indigo':         '#6366F1',

    # —— Estado ——
    'safe':           '#10B981',
    'warning':        '#F59E0B',
    'danger':         '#EF4444',
    'collapse':       '#991B1B',

    # —— Edificio ——
    'building_base':  '#1E3A5C',
    'window':         '#60A5FA',
    'window_glow':    '#93C5FD',
    'ground':         '#1A1628',
    'ground_line':    '#475569',
    'roof':           '#0F172A',

    # —— TMD ——
    'tmd':            '#F59E0B',
    'tmd_light':      '#FCD34D',
    'tmd_dark':       '#B45309',

    # —— Gráficos ——
    'line_disp':      '#3B82F6',
    'line_tmd':       '#F59E0B',
    'line_seis':      '#F43F5E',
    'grid':           '#1E293B',

    # —— Controles ——
    'slider':         '#2563EB',
    'slider_bg':      '#0F172A',

    # —— Teoría ——
    'th_bg':          '#0B0F19',
    'th_card':        '#111827',
    'th_eq':          '#BFDBFE',
    'th_eq_hi':       '#FDE68A',
}

# Colormap de estrés estructural: azul → cian → ámbar → rojo
STRESS_CMAP = LinearSegmentedColormap.from_list('stress', [
    (0.00, '#1E3A5C'),
    (0.30, '#0E7490'),
    (0.55, '#D97706'),
    (0.80, '#DC2626'),
    (1.00, '#991B1B'),
])

# =============================================================================
# PARÁMETROS INICIALES DEL SISTEMA (sin cambios)
# =============================================================================

PARAMS = {
    'm':          50000.0,      # Masa estructural [kg]
    'c':          15000.0,      # Amortiguamiento estructural [N·s/m]
    'k':        2000000.0,      # Rigidez estructural [N/m]
    'A':              3.0,      # Amplitud aceleración suelo [m/s²]
    'omega_s':       6.28,      # Frecuencia angular sísmica [rad/s]
    'alpha':         0.15,      # Decaimiento exponencial [1/s]
    'm_d':         2500.0,      # Masa TMD [kg]
    'c_d':         1200.0,      # Amortiguamiento TMD [N·s/m]
    'k_d':       100000.0,      # Rigidez TMD [N/m]
    'tmd_active':    True,
}

T_SIM = 20.0    # Duración simulación [s]
DT    = 0.02    # Paso temporal [s]

# =============================================================================
# MODELO MATEMÁTICO — EDOs (INTACTO)
# =============================================================================

def seismic_acceleration(t, A, omega_s, alpha):
    """
    Aceleración del suelo:
        x''_ground(t) = A · sin(ωs · t) · exp(−α · t)
    """
    return A * np.sin(omega_s * t) * np.exp(-alpha * t)


def ode_sdof(t, y, m, c, k, A, omega_s, alpha):
    """
    Sistema SDOF: y = [x, x']
        dy0/dt = y1
        dy1/dt = (F − c·y1 − k·y0) / m
    """
    x, v = y
    F = -m * seismic_acceleration(t, A, omega_s, alpha)
    return [v, (F - c * v - k * x) / m]


def ode_tmd(t, y, m, c, k, m_d, c_d, k_d, A, omega_s, alpha):
    """
    Sistema 2DOF + TMD: y = [x, x', xd, xd']
        m·x''  + c·x'  + k·x  − cd·(xd'−x') − kd·(xd−x) = F(t)
        md·xd'' + cd·(xd'−x') + kd·(xd−x)                = 0
    """
    x, v, x_d, v_d = y
    F       = -m * seismic_acceleration(t, A, omega_s, alpha)
    delta_x = x_d - x
    delta_v = v_d - v
    return [
        v,
        (F - c * v - k * x + c_d * delta_v + k_d * delta_x) / m,
        v_d,
        (-c_d * delta_v - k_d * delta_x) / m_d,
    ]


def solve_system(params):
    """Resuelve las EDOs con scipy.integrate.solve_ivp (método RK45)."""
    m, c, k          = params['m'], params['c'], params['k']
    A, ws, al        = params['A'], params['omega_s'], params['alpha']
    m_d, c_d, k_d    = params['m_d'], params['c_d'], params['k_d']
    t_eval = np.arange(0.0, T_SIM, DT)

    if params['tmd_active']:
        sol = solve_ivp(ode_tmd, (0, T_SIM), [0]*4,
                        args=(m, c, k, m_d, c_d, k_d, A, ws, al),
                        method='RK45', t_eval=t_eval, rtol=1e-6, atol=1e-8)
        return sol.t, sol.y[0], sol.y[2]
    else:
        sol = solve_ivp(ode_sdof, (0, T_SIM), [0, 0],
                        args=(m, c, k, A, ws, al),
                        method='RK45', t_eval=t_eval, rtol=1e-6, atol=1e-8)
        return sol.t, sol.y[0], None


def classify_state(x_max):
    """Clasifica el estado estructural según desplazamiento máximo."""
    if x_max < 0.05:
        return 'safe',     C['safe'],     'ESTRUCTURA ESTABLE'
    elif x_max < 0.10:
        return 'warning',  C['warning'],  'VIBRACION MODERADA'
    elif x_max < 0.20:
        return 'danger',   C['danger'],   'RIESGO ESTRUCTURAL'
    else:
        return 'collapse', C['collapse'], 'COLAPSO PROBABLE'


# =============================================================================
# UTILIDADES DE DIBUJO
# =============================================================================

def _draw_spring(ax, x1, x2, y, color, n_coils=10, amp=0.05, lw=1.5):
    """Resorte en zigzag horizontal."""
    n = n_coils * 4 + 2
    t = np.linspace(0, 1, n)
    xs = x1 + (x2 - x1) * t
    mask = (t > 0.04) & (t < 0.96)
    ys = y + amp * np.where(mask, np.sin(t * n_coils * 2 * np.pi), 0.0)
    ax.plot(xs, ys, color=color, lw=lw, zorder=9, alpha=0.9,
            solid_capstyle='round')


def _draw_damper(ax, x1, x2, y, color='#94A3B8', lw=1.8):
    """Amortiguador viscoso simplificado."""
    xm = (x1 + x2) / 2
    hw = abs(x2 - x1) * 0.12
    ax.plot([x1, xm - hw], [y, y], color=color, lw=lw, zorder=9)
    ax.plot([xm + hw, x2], [y, y], color=color, lw=lw, zorder=9)
    rect = FancyBboxPatch(
        (xm - hw, y - 0.04), 2 * hw, 0.08,
        boxstyle="square,pad=0", facecolor=C['bg_light'],
        edgecolor=color, lw=lw * 0.8, zorder=10
    )
    ax.add_patch(rect)
    ax.plot([xm + hw * 0.3, xm + hw * 0.8], [y, y],
            color=color, lw=lw * 1.4, zorder=11, solid_capstyle='butt')


# =============================================================================
# RENDERIZADO DEL EDIFICIO (REDISEÑADO)
# =============================================================================

def draw_building(ax, x_disp, x_tmd_disp, params, state_color, frame_idx):
    """Renderiza el edificio con deformación dinámica y TMD."""
    ax.clear()
    ax.set_facecolor(C['bg'])

    # —— Geometría ——
    scale    = 3.0
    bw       = 1.4
    bh       = 4.5
    n_floors = 8
    ground_y = 0.55
    x_vis    = float(np.clip(x_disp * scale, -2.2, 2.2))

    # —— Cielo con gradiente sutil ——
    for i in range(20):
        frac = i / 20.0
        alpha_sky = 0.015 * (1.0 - frac)
        ax.axhspan(ground_y + bh * frac, ground_y + bh * (frac + 0.05),
                   color=C['blue'], alpha=alpha_sky, zorder=0)

    # —— Suelo ——
    ax.fill_between([-3.5, 3.5], [ground_y - 0.40] * 2, [ground_y] * 2,
                    color=C['ground'], zorder=1, alpha=0.95)
    for xi in np.linspace(-3.2, 3.2, 28):
        ax.plot([xi, xi + 0.10], [ground_y - 0.32, ground_y - 0.06],
                color='#2D2640', lw=0.7, zorder=2, alpha=0.6)
    ax.axhline(ground_y, color=C['ground_line'], lw=2.5, zorder=3)

    # —— Cimentación ——
    cx = 0.0
    fw = bw + 0.30
    ax.fill(
        [cx - fw/2, cx + fw/2, cx + fw/2, cx - fw/2],
        [ground_y - 0.10, ground_y - 0.10, ground_y + 0.06, ground_y + 0.06],
        color='#0F1D2F', alpha=0.9, zorder=4
    )
    ax.plot([cx - fw/2, cx + fw/2], [ground_y + 0.06, ground_y + 0.06],
            color=C['border_light'], lw=1.0, zorder=4, alpha=0.5)

    # —— Estrés ——
    stress = min(abs(x_disp) / 0.20, 1.0)

    # —— Pisos ——
    for i in range(n_floors):
        fb = i / n_floors
        ft = (i + 1) / n_floors
        yb = ground_y + fb * bh
        yt = ground_y + ft * bh
        xb = x_vis * fb
        xt = x_vis * ft

        floor_stress = stress * (0.4 + 0.6 * ft)
        fc_rgba = STRESS_CMAP(floor_stress)
        fc = matplotlib.colors.to_hex(fc_rgba)

        xs_poly = [xb - bw/2, xb + bw/2, xt + bw/2, xt - bw/2]
        ys_poly = [yb, yb, yt, yt]

        # Sombra del piso
        ax.fill([x + 0.04 for x in xs_poly],
                [y - 0.02 for y in ys_poly],
                color='#000000', alpha=0.15, zorder=4)

        # Piso principal
        ax.fill(xs_poly, ys_poly, color=fc, alpha=0.92, zorder=5)
        ax.plot(xs_poly + [xs_poly[0]], ys_poly + [ys_poly[0]],
                color=state_color, lw=0.7, alpha=0.35, zorder=6)

        # Losa entre pisos
        slab_y = yt
        sx = xt
        ax.fill(
            [sx - bw/2 - 0.06, sx + bw/2 + 0.06,
             sx + bw/2 + 0.06, sx - bw/2 - 0.06],
            [slab_y - 0.03, slab_y - 0.03, slab_y + 0.03, slab_y + 0.03],
            color='#0C1929', alpha=0.85, zorder=7
        )

        # Ventanas (2 por piso)
        wc_x = (xb + xt) / 2
        wc_y = (yb + yt) / 2
        for woff in [-bw/4 - 0.02, bw/4 + 0.02]:
            wx = wc_x + woff
            wd, wh = 0.18, 0.20
            win_alpha = 0.4 + 0.45 * (1.0 - floor_stress)
            win_c = C['window_glow'] if floor_stress < 0.4 else C['window']

            # Glow detrás de la ventana
            ax.fill(
                [wx - wd/2 - 0.02, wx + wd/2 + 0.02,
                 wx + wd/2 + 0.02, wx - wd/2 - 0.02],
                [wc_y - wh/2 - 0.02, wc_y - wh/2 - 0.02,
                 wc_y + wh/2 + 0.02, wc_y + wh/2 + 0.02],
                color=win_c, alpha=win_alpha * 0.15, zorder=7
            )

            # Ventana
            win = Polygon(
                [[wx - wd/2, wc_y - wh/2], [wx + wd/2, wc_y - wh/2],
                 [wx + wd/2, wc_y + wh/2], [wx - wd/2, wc_y + wh/2]],
                closed=True, facecolor=win_c, edgecolor='#1E293B',
                alpha=win_alpha, lw=0.5, zorder=8
            )
            ax.add_patch(win)

            # Cruz de la ventana
            ax.plot([wx - wd/2, wx + wd/2], [wc_y, wc_y],
                    color='#1E293B', lw=0.4, alpha=0.5, zorder=9)
            ax.plot([wx, wx], [wc_y - wh/2, wc_y + wh/2],
                    color='#1E293B', lw=0.4, alpha=0.5, zorder=9)

    # —— Techo ——
    roof_y = ground_y + bh
    rx = x_vis
    ov = 0.14
    ax.fill(
        [rx - bw/2 - ov, rx + bw/2 + ov,
         rx + bw/2 + ov - 0.04, rx - bw/2 - ov + 0.04],
        [roof_y, roof_y, roof_y + 0.14, roof_y + 0.14],
        color=C['roof'], alpha=0.95, zorder=8
    )
    ax.plot([rx - bw/2 - ov, rx + bw/2 + ov],
            [roof_y, roof_y], color=C['border_light'], lw=1.0,
            zorder=8, alpha=0.6)

    # —— Antena en el techo ——
    ant_x = rx + bw/4
    ax.plot([ant_x, ant_x], [roof_y + 0.14, roof_y + 0.40],
            color=C['border_light'], lw=1.2, zorder=9, alpha=0.5)
    ax.scatter([ant_x], [roof_y + 0.42], s=12, color=C['red'],
              alpha=0.7, zorder=9)

    # —— TMD ——
    if params['tmd_active'] and x_tmd_disp is not None:
        xtd = float(np.clip(x_tmd_disp * scale, -2.8, 2.8))
        tmd_y   = roof_y + 0.32
        tmd_w   = 0.65
        tmd_h   = 0.32
        sp_y    = roof_y + 0.12
        dm_y    = sp_y + 0.16

        # Resorte
        _draw_spring(ax, rx, xtd, sp_y, C['tmd_light'],
                     n_coils=10, amp=0.055, lw=1.4)
        # Amortiguador
        _draw_damper(ax, rx, xtd, dm_y, color=C['tmd_dark'], lw=1.5)

        # Masa TMD con sombra
        ax.fill(
            [xtd - tmd_w/2 + 0.03, xtd + tmd_w/2 + 0.03,
             xtd + tmd_w/2 + 0.03, xtd - tmd_w/2 + 0.03],
            [tmd_y - 0.02, tmd_y - 0.02,
             tmd_y + tmd_h - 0.02, tmd_y + tmd_h - 0.02],
            color='#000', alpha=0.2, zorder=11
        )

        tmd_patch = FancyBboxPatch(
            (xtd - tmd_w/2, tmd_y), tmd_w, tmd_h,
            boxstyle="round,pad=0.04",
            facecolor=C['tmd'], edgecolor=C['tmd_light'],
            linewidth=2.0, zorder=12, alpha=0.95
        )
        ax.add_patch(tmd_patch)

        # Reflejo superior
        ax.fill(
            [xtd - tmd_w/2 + 0.06, xtd + tmd_w/2 - 0.06,
             xtd + tmd_w/2 - 0.10, xtd - tmd_w/2 + 0.10],
            [tmd_y + tmd_h * 0.70, tmd_y + tmd_h * 0.70,
             tmd_y + tmd_h * 0.92, tmd_y + tmd_h * 0.92],
            color='#FEF3C7', alpha=0.20, zorder=13
        )

        ax.text(xtd, tmd_y + tmd_h / 2, 'TMD', ha='center', va='center',
                color='#1C1100', fontsize=9, fontweight='bold', zorder=14)

        ax.text(xtd, tmd_y + tmd_h + 0.12,
                f'xd = {x_tmd_disp*100:.1f} cm',
                ha='center', va='bottom', color=C['tmd_light'],
                fontsize=7.5, fontweight='bold', zorder=14)

    # —— Flecha de fuerza sísmica ——
    F_t = seismic_acceleration(frame_idx * DT, params['A'],
                               params['omega_s'], params['alpha'])
    if abs(F_t) > 0.05 * params['A']:
        alen = float(np.clip(F_t * 0.25, -1.3, 1.3))
        mid_y = ground_y + bh * 0.42
        ax.annotate(
            '', xy=(x_vis + alen, mid_y), xytext=(x_vis, mid_y),
            arrowprops=dict(arrowstyle='-|>', color=C['cyan'],
                            lw=2.2, mutation_scale=16),
            zorder=15
        )
        ax.text(x_vis + alen * 0.5, mid_y + 0.14, 'F(t)',
                ha='center', color=C['cyan'], fontsize=7.5,
                fontweight='bold', zorder=15)

    # —— Indicador de desplazamiento ——
    lbl_y = roof_y + (0.90 if (params['tmd_active'] and
                               x_tmd_disp is not None) else 0.28)
    disp_cm = x_disp * 100
    _, sc, _ = classify_state(abs(x_disp))
    ax.text(0, lbl_y, f'x = {disp_cm:+.2f} cm',
            ha='center', va='bottom', color=sc,
            fontsize=10, fontweight='bold', zorder=15)

    # —— Barra lateral de desplazamiento ——
    bar_x = 2.50
    bar_h = bh * 0.75
    bar_y0 = ground_y + bh * 0.12

    ax.fill_between([bar_x - 0.06, bar_x + 0.06],
                    [bar_y0] * 2, [bar_y0 + bar_h] * 2,
                    color=C['bg_light'], alpha=0.8, zorder=4)
    ax.plot([bar_x - 0.06, bar_x - 0.06], [bar_y0, bar_y0 + bar_h],
            color=C['border'], lw=0.8, zorder=5)
    ax.plot([bar_x + 0.06, bar_x + 0.06], [bar_y0, bar_y0 + bar_h],
            color=C['border'], lw=0.8, zorder=5)

    # Marcas de umbral
    for thresh, col, lbl in [(0.05, C['safe'], '5'),
                              (0.10, C['warning'], '10'),
                              (0.20, C['danger'], '20')]:
        norm_th = thresh / 0.25
        ty_pos = bar_y0 + bar_h / 2 + norm_th * bar_h / 2
        ty_neg = bar_y0 + bar_h / 2 - norm_th * bar_h / 2
        for ty in [ty_pos, ty_neg]:
            if bar_y0 <= ty <= bar_y0 + bar_h:
                ax.plot([bar_x - 0.08, bar_x + 0.08], [ty, ty],
                        color=col, lw=0.6, ls=':', alpha=0.6, zorder=5)

    ax.axhline(bar_y0 + bar_h / 2, xmin=0.88, xmax=0.96,
               color=C['border_light'], lw=0.5, alpha=0.4, zorder=4)

    norm_d = np.clip(x_disp / 0.25, -1, 1)
    ind_y = bar_y0 + bar_h / 2 + norm_d * bar_h / 2
    ax.fill_between([bar_x - 0.05, bar_x + 0.05],
                    [bar_y0 + bar_h / 2] * 2, [ind_y] * 2,
                    color=sc, alpha=0.5, zorder=5)
    ax.scatter([bar_x], [ind_y], s=40, color=sc, zorder=6,
              edgecolors='white', lw=0.6, alpha=0.9)

    # —— Etiqueta suelo ——
    ax.text(0, ground_y - 0.58, 'SUELO',
            ha='center', color=C['text_muted'], fontsize=7,
            zorder=12, alpha=0.6, fontweight='bold')

    # —— Ejes ——
    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-0.1, 7.0)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(C['border'])
        sp.set_linewidth(0.6)
    ax.set_title('Modelo Estructural', color=C['text'], fontsize=11,
                 pad=10, fontweight='bold')


# =============================================================================
# ESTILO DE EJES CIENTÍFICOS
# =============================================================================

def style_axis(ax, xlabel='', ylabel='', title=''):
    """Aplica estilo profesional oscuro a un eje de gráficos."""
    ax.set_facecolor(C['bg'])
    ax.tick_params(colors=C['text_sec'], labelsize=8, which='both',
                   direction='in', length=3, width=0.6)
    for sp in ax.spines.values():
        sp.set_color(C['border'])
        sp.set_linewidth(0.7)
    ax.grid(True, color=C['grid'], linewidth=0.5, alpha=0.6,
            which='major', linestyle='--')
    ax.minorticks_on()
    ax.grid(True, color=C['grid'], linewidth=0.3, alpha=0.3,
            which='minor', linestyle=':')
    if xlabel:
        ax.set_xlabel(xlabel, color=C['text_sec'], fontsize=9, labelpad=5)
    if ylabel:
        ax.set_ylabel(ylabel, color=C['text_sec'], fontsize=9, labelpad=5)
    if title:
        ax.set_title(title, color=C['text'], fontsize=10.5,
                     fontweight='bold', pad=8)


# =============================================================================
# PANEL DE MÉTRICAS (REDISEÑADO CON TARJETAS)
# =============================================================================

def draw_info_panel(ax, params, t_vec, x_vec, state_label, state_color):
    """Panel de métricas en tiempo real con diseño de tarjetas."""
    ax.clear()
    ax.set_facecolor(C['bg_light'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(C['border'])
        sp.set_linewidth(0.8)

    m, c, k = params['m'], params['c'], params['k']
    omega_n = np.sqrt(k / m)
    f_n     = omega_n / (2.0 * np.pi)
    c_crit  = 2.0 * np.sqrt(m * k)
    zeta    = c / c_crit
    omega_d = omega_n * np.sqrt(max(0.0, 1.0 - zeta ** 2))
    beta    = params['omega_s'] / omega_n
    x_max   = np.max(np.abs(x_vec)) if len(x_vec) > 0 else 0.0
    T_n     = 2.0 * np.pi / omega_n

    kw = dict(transform=ax.transAxes, fontfamily='monospace')
    y = 0.96
    dy_header = 0.055
    dy_row    = 0.042

    def header(text, color, yy):
        ax.fill_between([0.04, 0.96], [yy - 0.003] * 2, [yy + 0.032] * 2,
                        color=color, alpha=0.08, zorder=1)
        ax.text(0.06, yy + 0.014, text, color=color, fontsize=8.5,
                fontweight='bold', va='center', **kw)
        ax.plot([0.04, 0.96], [yy - 0.003, yy - 0.003],
                color=color, lw=0.5, alpha=0.3)

    def row(label, value, yy, vc=C['text']):
        ax.text(0.08, yy, label, color=C['text_sec'], fontsize=7.5,
                va='top', **kw)
        ax.text(0.94, yy, value, color=vc, fontsize=7.5,
                va='top', ha='right', **kw)

    # —— Parámetros del edificio ——
    header('ESTRUCTURA', C['blue'], y)
    y -= dy_header
    row('m  Masa', f'{m/1000:.0f} t', y)
    y -= dy_row
    row('c  Amort.', f'{c/1000:.1f} kN·s/m', y)
    y -= dy_row
    row('k  Rigidez', f'{k/1e6:.2f} MN/m', y)
    y -= dy_row * 1.2

    # —— Frecuencias ——
    header('FRECUENCIAS', C['cyan'], y)
    y -= dy_header
    row('\u03c9\u2099', f'{omega_n:.3f} rad/s', y, C['th_eq'])
    y -= dy_row
    row('f\u2099', f'{f_n:.4f} Hz', y, C['th_eq'])
    y -= dy_row
    row('T\u2099', f'{T_n:.3f} s', y, C['th_eq'])
    y -= dy_row
    zeta_c = C['warning'] if zeta < 0.05 else C['safe']
    row('\u03b6', f'{zeta:.4f} ({zeta*100:.1f}%)', y, zeta_c)
    y -= dy_row
    row('\u03c9d', f'{omega_d:.3f} rad/s', y, C['th_eq'])
    y -= dy_row

    # —— Resonancia ——
    beta_c = C['danger'] if 0.85 < beta < 1.15 else C['text']
    row('\u03b2 = \u03c9s/\u03c9\u2099', f'{beta:.3f}', y, beta_c)
    y -= dy_row * 1.2

    # —— TMD ——
    if params['tmd_active']:
        header('TMD ACTIVO', C['tmd'], y)
        y -= dy_header
        omega_tmd = np.sqrt(params['k_d'] / params['m_d'])
        mu = params['m_d'] / m
        sinc = omega_tmd / omega_n
        row('m_d', f"{params['m_d']/1000:.2f} t", y)
        y -= dy_row
        row('\u03c9_TMD', f'{omega_tmd:.3f} r/s', y)
        y -= dy_row
        sinc_c = C['safe'] if 0.95 < sinc < 1.05 else C['warning']
        row('Sinton.', f'{sinc:.4f}', y, sinc_c)
        y -= dy_row
        row('\u03bc = md/m', f'{mu:.4f}', y)
        y -= dy_row * 1.2
    else:
        header('TMD INACTIVO', C['text_muted'], y)
        y -= dy_header + dy_row * 1.5

    # —— Estado estructural ——
    header('ESTADO', state_color, y)
    y -= dy_header
    row('x_max', f'{x_max*100:.2f} cm', y, state_color)
    y -= dy_row * 1.1

    # Barra de estado
    bar_y = y
    bar_h = 0.018
    norm = min(x_max / 0.25, 1.0)
    ax.fill_between([0.06, 0.94], [bar_y] * 2, [bar_y + bar_h] * 2,
                    color=C['bg'], alpha=0.8)
    ax.fill_between([0.06, 0.06 + 0.88 * norm],
                    [bar_y] * 2, [bar_y + bar_h] * 2,
                    color=state_color, alpha=0.6)

    # Marcas de umbral en la barra
    for th_val, th_col in [(0.05, C['safe']), (0.10, C['warning']),
                            (0.20, C['danger'])]:
        th_x = 0.06 + 0.88 * min(th_val / 0.25, 1.0)
        ax.plot([th_x, th_x], [bar_y - 0.005, bar_y + bar_h + 0.005],
                color=th_col, lw=0.8, alpha=0.5)

    y -= dy_row * 1.3
    ax.text(0.50, y, state_label, ha='center', va='top',
            color=state_color, fontsize=9, fontweight='bold',
            transform=ax.transAxes)

    # —— Método numérico ——
    y -= dy_row * 1.5
    ax.text(0.50, y, 'RK45 · rtol=1e-6 · atol=1e-8',
            ha='center', va='top', color=C['text_muted'], fontsize=6.5,
            transform=ax.transAxes, style='italic')


# =============================================================================
# VENTANA DE FUNDAMENTOS MATEMÁTICOS (NUEVA — 9 PÁGINAS)
# =============================================================================

class TheoryWindow:
    """Ventana secundaria con teoría expandida — navegación por páginas."""

    PAGE_TITLES = [
        'Que es una Ecuacion Diferencial',
        'Sistema Masa-Resorte-Amortiguador',
        'Significado Fisico de Cada Termino',
        'Modelo de Excitacion Sismica',
        'Frecuencias Naturales y Amortiguamiento',
        'Resonancia Estructural',
        'TMD — Amortiguador de Masa Sintonizado',
        'Reduccion de Orden y Metodo RK45',
        'Energia y Clasificacion Estructural',
    ]

    def __init__(self):
        self.fig = None
        self.ax_content = None
        self.current_page = 0
        self.btn_prev = None
        self.btn_next = None
        self._pages = [
            self._page_0, self._page_1, self._page_2,
            self._page_3, self._page_4, self._page_5,
            self._page_6, self._page_7, self._page_8,
        ]

    def show(self):
        if self.fig is not None:
            try:
                if plt.fignum_exists(self.fig.number):
                    return
            except Exception:
                pass
        self._create()

    def _create(self):
        self.fig = plt.figure(figsize=(14, 9), facecolor=C['th_bg'])
        self.fig.canvas.manager.set_window_title(
            'Fundamentos Matematicos — Ecuaciones Diferenciales')

        self.ax_content = self.fig.add_axes(
            [0.03, 0.08, 0.94, 0.88], facecolor=C['th_bg'])

        # Botones de navegación
        ax_prev = self.fig.add_axes([0.03, 0.015, 0.10, 0.045],
                                     facecolor=C['bg_card'])
        self.btn_prev = Button(ax_prev, 'Anterior',
                               color=C['bg_card'], hovercolor=C['border'])
        self.btn_prev.label.set_color(C['text_sec'])
        self.btn_prev.label.set_fontsize(9)
        self.btn_prev.on_clicked(self._go_prev)

        ax_next = self.fig.add_axes([0.87, 0.015, 0.10, 0.045],
                                     facecolor=C['bg_card'])
        self.btn_next = Button(ax_next, 'Siguiente',
                               color=C['bg_card'], hovercolor=C['border'])
        self.btn_next.label.set_color(C['text_sec'])
        self.btn_next.label.set_fontsize(9)
        self.btn_next.on_clicked(self._go_next)

        self.current_page = 0
        self._render()
        plt.show(block=False)

    def _go_prev(self, event):
        if self.current_page > 0:
            self.current_page -= 1
            self._render()

    def _go_next(self, event):
        if self.current_page < len(self._pages) - 1:
            self.current_page += 1
            self._render()

    def _render(self):
        ax = self.ax_content
        ax.clear()
        ax.set_facecolor(C['th_bg'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

        self._pages[self.current_page](ax)

        # Indicador de página
        total = len(self._pages)
        self.fig.texts = [t for t in self.fig.texts]  # clear old
        for t in list(self.fig.texts):
            t.remove()
        self.fig.text(0.50, 0.030,
                      f'Pagina {self.current_page + 1} de {total}  —  '
                      f'{self.PAGE_TITLES[self.current_page]}',
                      ha='center', va='center', color=C['text_sec'],
                      fontsize=9, fontweight='bold')

        self.fig.canvas.draw_idle()

    # —— Helpers de página ——

    def _hdr(self, ax, y, text, color=C['blue']):
        ax.text(0.50, y, text, ha='center', va='top', color=color,
                fontsize=14, fontweight='bold', transform=ax.transAxes)
        ax.axhline(y - 0.020, xmin=0.10, xmax=0.90,
                   color=color, lw=1.0, alpha=0.4, transform=ax.transAxes)

    def _sub(self, ax, y, text, color=C['cyan']):
        ax.text(0.05, y, text, va='top', color=color,
                fontsize=11, fontweight='bold', transform=ax.transAxes)

    def _txt(self, ax, y, text, color=C['text'], size=9.5):
        ax.text(0.06, y, text, va='top', color=color,
                fontsize=size, transform=ax.transAxes, linespacing=1.6)

    def _eq(self, ax, y, latex, size=14):
        ax.text(0.50, y, latex, ha='center', va='top',
                color=C['th_eq'], fontsize=size, transform=ax.transAxes)

    def _eq_hi(self, ax, y, latex, size=15):
        ax.fill_between([0.08, 0.92], [y - 0.040] * 2, [y + 0.010] * 2,
                        color=C['blue'], alpha=0.06, transform=ax.transAxes)
        ax.text(0.50, y, latex, ha='center', va='top',
                color=C['th_eq_hi'], fontsize=size,
                fontweight='bold', transform=ax.transAxes)

    def _div(self, ax, y):
        ax.axhline(y, xmin=0.05, xmax=0.95, color=C['border'],
                   lw=0.6, alpha=0.5, transform=ax.transAxes)

    def _bullet(self, ax, y, text, color=C['text_sec'], size=9):
        ax.text(0.08, y, f'\u2022  {text}', va='top', color=color,
                fontsize=size, transform=ax.transAxes)

    # —— PÁGINA 0: ¿Qué es una EDO? ——

    def _page_0(self, ax):
        self._hdr(ax, 0.96, 'Que es una Ecuacion Diferencial?')
        y = 0.90
        self._sub(ax, y, 'Definicion')
        y -= 0.05
        self._txt(ax, y,
            'Una ecuacion diferencial es una ecuacion matematica que relaciona\n'
            'una funcion desconocida con sus derivadas. Aparecen naturalmente\n'
            'al modelar fenomenos fisicos que cambian con el tiempo.')
        y -= 0.11
        self._eq(ax, y, r'$F\left(t,\, y,\, \frac{dy}{dt},\, '
                        r'\frac{d^2y}{dt^2},\, \ldots\right) = 0$')

        y -= 0.09
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'EDO vs EDP', C['amber'])
        y -= 0.05
        self._bullet(ax, y,
            'EDO (Ecuacion Diferencial Ordinaria): una sola variable independiente (t)')
        y -= 0.04
        self._bullet(ax, y,
            'EDP (Ecuacion en Derivadas Parciales): multiples variables (x, y, t, ...)')
        y -= 0.04
        self._bullet(ax, y,
            'Nuestro sistema sismico es una EDO — solo depende del tiempo t',
            C['emerald'])

        y -= 0.07
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Orden de una EDO', C['purple'])
        y -= 0.05
        self._txt(ax, y,
            'El ORDEN de una EDO es la derivada de mayor orden que aparece.')
        y -= 0.06
        self._bullet(ax, y, "1er orden:  dy/dt = f(t, y)")
        y -= 0.04
        self._bullet(ax, y, "2do orden:  d2y/dt2 = f(t, y, dy/dt)  <-- Nuestro sistema",
                     C['amber'])
        y -= 0.04
        self._bullet(ax, y, "n-esimo orden:  dny/dtn = f(t, y, ..., d(n-1)y/dt(n-1))")

        y -= 0.07
        self._txt(ax, y,
            'Nuestro modelo sismico es una EDO lineal de 2do orden con\n'
            'coeficientes constantes y fuerza externa variable.',
            C['emerald'], 10)

    # —— PÁGINA 1: Sistema MRA ——

    def _page_1(self, ax):
        self._hdr(ax, 0.96, 'Sistema Masa-Resorte-Amortiguador')
        y = 0.90
        self._sub(ax, y, 'Modelo Fisico')
        y -= 0.05
        self._txt(ax, y,
            'Un edificio sometido a un sismo se modela como un sistema de\n'
            'un grado de libertad (SDOF), donde:')
        y -= 0.08
        self._bullet(ax, y, 'Una MASA (m) concentra la inercia del edificio')
        y -= 0.04
        self._bullet(ax, y, 'Un RESORTE (k) representa la rigidez lateral')
        y -= 0.04
        self._bullet(ax, y, 'Un AMORTIGUADOR (c) modela la disipacion de energia')
        y -= 0.04
        self._bullet(ax, y, 'Una FUERZA EXTERNA F(t) representa la excitacion sismica')

        y -= 0.07
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Segunda Ley de Newton', C['amber'])
        y -= 0.05
        self._txt(ax, y, 'Aplicando la 2da Ley de Newton sobre la masa:')
        y -= 0.05
        self._eq(ax, y, r'$\sum F = m\ddot{x}$', 13)
        y -= 0.06
        self._txt(ax, y, 'Las fuerzas que actuan sobre la masa son:')
        y -= 0.05
        self._bullet(ax, y, 'Fuerza elastica (resorte):   F_k = -k·x')
        y -= 0.04
        self._bullet(ax, y, 'Fuerza disipativa (amort.):  F_c = -c·x\'')
        y -= 0.04
        self._bullet(ax, y, 'Fuerza sismica:              F(t) = -m·a_suelo(t)')

        y -= 0.07
        self._sub(ax, y, 'Ecuacion del Movimiento', C['emerald'])
        y -= 0.05
        self._eq_hi(ax, y, r'$m\ddot{x} + c\dot{x} + kx = F(t)$', 16)

    # —— PÁGINA 2: Significado de cada término ——

    def _page_2(self, ax):
        self._hdr(ax, 0.96, 'Significado Fisico de Cada Termino')

        y = 0.88
        self._sub(ax, y, r'Termino Inercial:  m · x\'\'', C['blue'])
        y -= 0.05
        self._txt(ax, y,
            'Resistencia de la estructura a cambiar su estado de movimiento.\n'
            'Mayor masa = mayor inercia = mas dificil de acelerar/frenar.\n'
            'Unidad: kg. Rango tipico para edificios: 20,000 - 200,000 kg')

        y -= 0.11
        self._div(ax, y)
        y -= 0.02
        self._sub(ax, y, r'Termino Disipativo:  c · x\'', C['cyan'])
        y -= 0.05
        self._txt(ax, y,
            'Energia que el edificio disipa por friccion interna, materiales\n'
            'viscoelasticos y conexiones. Proporcional a la velocidad.\n'
            'Unidad: N·s/m. Edificios reales: zeta = 2-5% del critico')

        y -= 0.11
        self._div(ax, y)
        y -= 0.02
        self._sub(ax, y, 'Termino Elastico:  k · x', C['emerald'])
        y -= 0.05
        self._txt(ax, y,
            'Fuerza restauradora que tiende a devolver la estructura a su\n'
            'posicion de equilibrio. Proporcional al desplazamiento.\n'
            'Unidad: N/m. Determina la frecuencia natural del edificio.')

        y -= 0.11
        self._div(ax, y)
        y -= 0.02
        self._sub(ax, y, 'Fuerza Externa:  F(t)', C['rose'])
        y -= 0.05
        self._txt(ax, y,
            "Fuerza de inercia de d'Alembert debida al movimiento del suelo.\n"
            'F(t) = -m · a_suelo(t). Depende del tiempo y de la masa.')
        y -= 0.07
        self._eq(ax, y, r"$F(t) = -m \cdot A\sin(\omega_s t)\,e^{-\alpha t}$", 13)

    # —— PÁGINA 3: Excitación sísmica ——

    def _page_3(self, ax):
        self._hdr(ax, 0.96, 'Modelo de Excitacion Sismica')
        y = 0.89
        self._sub(ax, y, 'Aceleracion del Suelo')
        y -= 0.05
        self._txt(ax, y,
            'La excitacion sismica se modela como una oscilacion sinusoidal\n'
            'con envolvente exponencial decreciente:')
        y -= 0.08
        self._eq_hi(ax, y,
            r'$\ddot{x}_{suelo}(t) = A \cdot \sin(\omega_s \, t) '
            r'\cdot e^{-\alpha \, t}$', 15)

        y -= 0.08
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Parametros de la Excitacion', C['amber'])
        y -= 0.05
        self._bullet(ax, y,
            'A  [m/s2]: Amplitud maxima de la aceleracion. A=9.81 = 1g (muy severo)')
        y -= 0.05
        self._bullet(ax, y,
            'ws [rad/s]: Frecuencia angular dominante. ws=2pi = 1 Hz. Rango: 2-15 r/s')
        y -= 0.05
        self._bullet(ax, y,
            'alpha [1/s]: Tasa de decaimiento. Controla cuanto dura el sismo')

        y -= 0.07
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, "Fuerza de Inercia (Principio de d'Alembert)", C['purple'])
        y -= 0.05
        self._txt(ax, y,
            'La fuerza que siente el edificio es la reaccion inercial\n'
            'al movimiento del suelo (fuerza ficticia de referencia no inercial):')
        y -= 0.07
        self._eq(ax, y, r'$F(t) = -m \cdot \ddot{x}_{suelo}(t)$', 14)
        y -= 0.07
        self._txt(ax, y,
            'El signo negativo indica que la fuerza se opone al movimiento\n'
            'del suelo (principio de inercia).', C['text_sec'])

    # —— PÁGINA 4: Frecuencias y amortiguamiento ——

    def _page_4(self, ax):
        self._hdr(ax, 0.96, 'Frecuencias Naturales y Amortiguamiento')
        y = 0.89
        self._sub(ax, y, 'Frecuencia Natural No Amortiguada')
        y -= 0.05
        self._txt(ax, y,
            'Es la frecuencia a la que el sistema oscila libremente\n'
            'sin amortiguamiento ni fuerza externa:')
        y -= 0.07
        self._eq_hi(ax, y,
            r'$\omega_n = \sqrt{\frac{k}{m}} \qquad '
            r'f_n = \frac{\omega_n}{2\pi} \qquad '
            r'T_n = \frac{2\pi}{\omega_n}$', 14)

        y -= 0.08
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Amortiguamiento Critico y Fraccion', C['amber'])
        y -= 0.05
        self._eq(ax, y,
            r'$c_{cr} = 2\sqrt{mk} \qquad '
            r'\zeta = \frac{c}{c_{cr}} = \frac{c}{2\sqrt{mk}}$', 13)
        y -= 0.07
        self._bullet(ax, y, 'zeta < 1: SUBAMORTIGUADO — oscila y decae (edificios reales)',
                     C['emerald'])
        y -= 0.04
        self._bullet(ax, y, 'zeta = 1: CRITICAMENTE AMORTIGUADO — decae sin oscilar')
        y -= 0.04
        self._bullet(ax, y, 'zeta > 1: SOBREAMORTIGUADO — decae lentamente sin oscilar')

        y -= 0.07
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Frecuencia Amortiguada', C['cyan'])
        y -= 0.05
        self._eq(ax, y,
            r'$\omega_d = \omega_n \sqrt{1 - \zeta^2}$', 14)
        y -= 0.06
        self._txt(ax, y,
            'Es la frecuencia REAL de oscilacion del sistema amortiguado.\n'
            'Para edificios (zeta << 1): wd es casi igual a wn.', C['text_sec'])

    # —— PÁGINA 5: Resonancia ——

    def _page_5(self, ax):
        self._hdr(ax, 0.96, 'Resonancia Estructural', C['danger'])
        y = 0.89
        self._sub(ax, y, 'Razon de Frecuencias')
        y -= 0.05
        self._eq_hi(ax, y,
            r'$\beta = \frac{\omega_s}{\omega_n}$', 16)
        y -= 0.07
        self._txt(ax, y,
            'Cuando la frecuencia del sismo (ws) coincide con la frecuencia\n'
            'natural del edificio (wn), ocurre la RESONANCIA.')

        y -= 0.08
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Factor de Amplificacion Dinamica', C['amber'])
        y -= 0.05
        self._eq(ax, y,
            r'$D = \frac{1}{\sqrt{(1 - \beta^2)^2 + (2\zeta\beta)^2}}$', 14)
        y -= 0.08
        self._bullet(ax, y,
            'beta << 1:  Cuasiestatico. El edificio sigue al suelo.', C['safe'])
        y -= 0.04
        self._bullet(ax, y,
            'beta = 1:   RESONANCIA. D -> infinito si zeta -> 0', C['danger'])
        y -= 0.04
        self._bullet(ax, y,
            'beta >> 1:  Inercial. El edificio "no siente" el sismo.', C['safe'])

        y -= 0.07
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Peligro de la Resonancia', C['danger'])
        y -= 0.05
        self._txt(ax, y,
            'En resonancia, la energia del sismo se transfiere con maxima\n'
            'eficiencia al edificio. Los desplazamientos crecen enormemente\n'
            'y pueden causar colapso estructural.\n\n'
            'El TMD es una solucion ingenieril para EVITAR la resonancia\n'
            'introduciendo un segundo modo de vibracion.', C['text'])

    # —— PÁGINA 6: TMD ——

    def _page_6(self, ax):
        self._hdr(ax, 0.96, 'TMD — Amortiguador de Masa Sintonizado', C['tmd'])
        y = 0.89
        self._sub(ax, y, 'Concepto Fisico')
        y -= 0.05
        self._txt(ax, y,
            'Un TMD (Tuned Mass Damper) es una masa secundaria conectada\n'
            'al edificio mediante un resorte y un amortiguador. Absorbe\n'
            'y disipa la energia de vibracion del edificio principal.')

        y -= 0.10
        self._sub(ax, y, 'Ecuaciones del Sistema Acoplado (2DOF)', C['amber'])
        y -= 0.05
        self._eq_hi(ax, y,
            r'$m\ddot{x} + c\dot{x} + kx '
            r'- c_d(\dot{x}_d - \dot{x}) - k_d(x_d - x) = F(t)$', 12)
        y -= 0.06
        self._eq_hi(ax, y,
            r'$m_d\ddot{x}_d + c_d(\dot{x}_d - \dot{x}) '
            r'+ k_d(x_d - x) = 0$', 12)

        y -= 0.07
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Sintonizacion Optima (Den Hartog)', C['emerald'])
        y -= 0.05
        self._eq(ax, y,
            r'$\omega_{TMD}^{opt} = \frac{\omega_n}{1 + \mu} '
            r'\qquad \mu = \frac{m_d}{m}$', 13)
        y -= 0.07
        self._txt(ax, y,
            'Cuando w_TMD es cercana a wn, el TMD "absorbe" la vibracion\n'
            'del modo principal, reduciendo desplazamientos un 40-60%.\n\n'
            'Ejemplo real: el Taipei 101 tiene un TMD de 660 toneladas.',
            C['text_sec'])

    # —— PÁGINA 7: Reducción de orden y RK45 ——

    def _page_7(self, ax):
        self._hdr(ax, 0.96, 'Reduccion de Orden y Metodo RK45')
        y = 0.89
        self._sub(ax, y, 'Por que Reducir a Primer Orden?')
        y -= 0.05
        self._txt(ax, y,
            'Los metodos numericos estandar (como RK45) resuelven sistemas\n'
            'de EDOs de PRIMER orden. Nuestra EDO es de 2do orden, asi que\n'
            'la transformamos definiendo el vector de estado:')
        y -= 0.09
        self._eq(ax, y,
            r'$\mathbf{y} = \begin{bmatrix} x \\ \dot{x} \end{bmatrix}'
            r'\quad \Rightarrow \quad'
            r'\dot{\mathbf{y}} = \begin{bmatrix} \dot{x} \\ \ddot{x} '
            r'\end{bmatrix}$', 13)

        y -= 0.08
        self._sub(ax, y, 'Sistema Equivalente de 1er Orden', C['amber'])
        y -= 0.05
        self._eq_hi(ax, y,
            r'$\dot{y}_0 = y_1 \qquad '
            r'\dot{y}_1 = \frac{F(t) - c\,y_1 - k\,y_0}{m}$', 13)

        y -= 0.08
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Metodo Runge-Kutta 4/5 (RK45)', C['cyan'])
        y -= 0.05
        self._txt(ax, y,
            'El metodo RK45 (Dormand-Prince) calcula dos estimaciones de\n'
            'diferente orden (4 y 5) en cada paso. La diferencia entre\n'
            'ambas estima el ERROR LOCAL y ajusta el paso automaticamente.')
        y -= 0.10
        self._eq(ax, y,
            r'$\mathbf{y}_{n+1} = \mathbf{y}_n + h \sum_{i=1}^{s} '
            r'b_i \, \mathbf{k}_i$', 12)

        y -= 0.07
        self._sub(ax, y, 'solve_ivp de scipy', C['emerald'])
        y -= 0.05
        self._txt(ax, y,
            'scipy.integrate.solve_ivp() es la interfaz de Python para\n'
            'resolver problemas de valor inicial. Parametros clave:\n'
            '  method="RK45"  |  rtol=1e-6  |  atol=1e-8', C['text_sec'])

    # —— PÁGINA 8: Energía y clasificación ——

    def _page_8(self, ax):
        self._hdr(ax, 0.96, 'Energia y Clasificacion Estructural')
        y = 0.89
        self._sub(ax, y, 'Balance Energetico')
        y -= 0.05
        self._eq(ax, y,
            r'$E_k = \frac{1}{2}m\dot{x}^2 \qquad '
            r'E_p = \frac{1}{2}kx^2 \qquad '
            r'\dot{E}_{dis} = c\dot{x}^2$', 12)
        y -= 0.07
        self._txt(ax, y,
            'La energia total del sistema se conserva cuando no hay fuerzas\n'
            'externas ni amortiguamiento. Con amortiguamiento, la energia\n'
            'se disipa gradualmente en forma de calor.')
        y -= 0.09
        self._eq(ax, y,
            r'$\frac{d}{dt}(E_k + E_p) = F(t)\dot{x} - c\dot{x}^2$', 13)

        y -= 0.08
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Criterios de Dano Estructural', C['amber'])
        y -= 0.05

        damage = [
            (C['safe'],     'x_max < 5 cm',    'Estable — sin dano'),
            (C['warning'],  '5 cm < x < 10 cm', 'Vibracion moderada — revision'),
            (C['danger'],   '10 cm < x < 20 cm', 'Riesgo estructural — evacuacion'),
            (C['collapse'], 'x_max > 20 cm',    'Colapso probable — falla critica'),
        ]
        for col, rng, desc in damage:
            ax.fill_between([0.06, 0.08], [y - 0.005] * 2,
                            [y + 0.025] * 2, color=col, alpha=0.8,
                            transform=ax.transAxes)
            ax.text(0.10, y + 0.010, rng, color=C['text'], fontsize=9,
                    va='center', transform=ax.transAxes)
            ax.text(0.55, y + 0.010, desc, color=col, fontsize=9,
                    va='center', fontweight='bold', transform=ax.transAxes)
            y -= 0.05

        y -= 0.04
        self._div(ax, y)
        y -= 0.03
        self._sub(ax, y, 'Rol del TMD en la Energia', C['emerald'])
        y -= 0.05
        self._txt(ax, y,
            'El TMD reduce x_max al absorber energia del modo principal\n'
            'y disiparla mediante su propio amortiguador. La masa del TMD\n'
            'oscila en CONTRAFASE con el edificio, cancelando parcialmente\n'
            'la vibracion. Reduccion tipica: 40-60% del desplazamiento max.',
            C['text_sec'])


# =============================================================================
# CONSTRUCCIÓN DEL LAYOUT PRINCIPAL (SIMPLIFICADO 2 FILAS)
# =============================================================================

def build_figure():
    """
    Layout:
    ┌─────────────┬────────────────────────────┬─────────────┐
    │  EDIFICIO   │  Gráfico desplazamiento    │  MÉTRICAS   │
    │  ANIMACIÓN  ├────────────────────────────┤  EN TIEMPO  │
    │             │  Gráfico sísmica           │  REAL       │
    ├─────────────┴────────────────────────────┴─────────────┤
    │                  CONTROLES                              │
    └─────────────────────────────────────────────────────────┘
    """
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(18.5, 11), facecolor=C['bg'])
    fig.canvas.manager.set_window_title(
        'Simulacion Sismica Profesional v3.0 — Ecuaciones Diferenciales')

    # Título
    fig.text(0.50, 0.990,
             'SIMULACION SISMICA  ·  Sistema Masa-Resorte-Amortiguador con TMD',
             ha='center', va='top', color=C['text_bright'],
             fontsize=14, fontweight='bold')
    fig.text(0.50, 0.973,
             'Analisis Matematico II  ·  Ecuaciones Diferenciales  ·  RK45',
             ha='center', va='top', color=C['text_muted'], fontsize=9)

    # Grid principal: 2 filas
    outer = gridspec.GridSpec(
        2, 1, figure=fig,
        height_ratios=[7.0, 2.8],
        hspace=0.08,
        top=0.958, bottom=0.015,
        left=0.01, right=0.99
    )

    # Fila superior: edificio | gráficos | métricas
    top_gs = gridspec.GridSpecFromSubplotSpec(
        1, 3, subplot_spec=outer[0],
        width_ratios=[1.20, 2.40, 0.95],
        wspace=0.04
    )

    # Gráficos centrales (2 filas)
    center_gs = gridspec.GridSpecFromSubplotSpec(
        2, 1, subplot_spec=top_gs[1],
        hspace=0.35
    )

    ax_building = fig.add_subplot(top_gs[0])
    ax_disp     = fig.add_subplot(center_gs[0])
    ax_seismic  = fig.add_subplot(center_gs[1])
    ax_info     = fig.add_subplot(top_gs[2])

    # Estilo
    style_axis(ax_disp, ylabel='Desplazamiento [m]',
               title='Solucion EDO:  x(t)')
    style_axis(ax_seismic, xlabel='Tiempo [s]',
               ylabel='Aceleracion [m/s2]',
               title='Excitacion Sismica:  a_suelo(t)')

    for ax in [ax_building, ax_info]:
        ax.set_facecolor(C['bg'])
        for sp in ax.spines.values():
            sp.set_color(C['border'])
            sp.set_linewidth(0.7)

    # Posición del panel de controles
    ctrl_rect = outer[1].get_position(fig)

    return fig, ax_building, ax_disp, ax_seismic, ax_info, ctrl_rect


# =============================================================================
# CONTROLES (REDISEÑADOS — LABELS ARRIBA, SIN OVERLAP)
# =============================================================================

def build_controls(fig, ctrl_rect):
    """
    Controles organizados en 4 columnas:
      [ESTRUCTURA]  [SISMO]  [TMD]  [ACCIONES]
    Labels posicionados ARRIBA de cada slider.
    """
    L = ctrl_rect.x0 + 0.012
    B = ctrl_rect.y0 + 0.008
    W = ctrl_rect.width - 0.024
    H = ctrl_rect.height - 0.016

    # Columnas
    col_w     = W * 0.235
    col_gap   = W * 0.020
    btn_col_w = W * 0.235

    col_x = [
        L,
        L + col_w + col_gap,
        L + 2 * (col_w + col_gap),
        L + 3 * (col_w + col_gap),
    ]

    # Filas de sliders (3 por columna)
    sl_h    = 0.022
    sl_gap  = 0.005
    lbl_h   = 0.014
    row_total = sl_h + sl_gap + lbl_h
    row_tops = [
        B + H - 0.008,
        B + H - 0.008 - row_total,
        B + H - 0.008 - 2 * row_total,
    ]

    cat_style = dict(fontsize=9, fontweight='bold', va='bottom')

    # Fondo del panel de controles
    ctrl_bg = FancyBboxPatch(
        (ctrl_rect.x0, ctrl_rect.y0), ctrl_rect.width, ctrl_rect.height,
        boxstyle="round,pad=0.003", facecolor=C['bg_light'],
        edgecolor=C['border'], linewidth=0.8,
        transform=fig.transFigure, zorder=0
    )
    fig.patches.append(ctrl_bg)

    def make_slider(col, row, label, vmin, vmax, vinit, vstep,
                    slider_color=C['slider'], label_color=C['text_sec']):
        """Crea un slider con label posicionado arriba."""
        x = col_x[col]
        top = row_tops[row]
        sw = col_w - 0.005

        # Label arriba del slider
        fig.text(x + sw / 2, top, label,
                 ha='center', va='bottom', color=label_color,
                 fontsize=7.5, fontfamily='monospace')

        # Slider
        sl_y = top - lbl_h - sl_h
        ax_sl = fig.add_axes([x, sl_y, sw, sl_h], facecolor=C['slider_bg'])
        sl = Slider(ax_sl, '', vmin, vmax, valinit=vinit,
                    valstep=vstep, color=slider_color)
        sl.valtext.set_color(C['text'])
        sl.valtext.set_fontsize(8)
        sl.valtext.set_fontfamily('monospace')
        ax_sl.tick_params(colors=C['text_muted'], labelsize=5.5)
        for sp in ax_sl.spines.values():
            sp.set_color(C['border'])
            sp.set_linewidth(0.4)
        return sl

    sliders = {}

    # —— ESTRUCTURA (columna 0) ——
    fig.text(col_x[0] + col_w / 2, B + H + 0.004, 'ESTRUCTURA',
             ha='center', **cat_style, color=C['blue'])

    sliders['m_t']  = make_slider(0, 0, 'm — Masa [t]',
                                   10, 200, 50, 1.0)
    sliders['c_k']  = make_slider(0, 1, 'c — Amortiguamiento [kN·s/m]',
                                   1, 50, 15, 0.5)
    sliders['k_M']  = make_slider(0, 2, 'k — Rigidez [MN/m]',
                                   0.5, 10, 2.0, 0.1)

    # —— SISMO (columna 1) ——
    fig.text(col_x[1] + col_w / 2, B + H + 0.004, 'SISMO',
             ha='center', **cat_style, color=C['rose'])

    sliders['A']    = make_slider(1, 0, 'A — Amplitud [m/s2]',
                                   0.5, 15, 3.0, 0.1,
                                   slider_color='#BE123C')
    sliders['ws']   = make_slider(1, 1, 'ws — Frecuencia [rad/s]',
                                   1.0, 20, 6.28, 0.1,
                                   slider_color='#BE123C')
    sliders['al']   = make_slider(1, 2, 'a — Decaimiento [1/s]',
                                   0.0, 1.0, 0.15, 0.01,
                                   slider_color='#BE123C')

    # —— TMD (columna 2) ——
    fig.text(col_x[2] + col_w / 2, B + H + 0.004, 'TMD',
             ha='center', **cat_style, color=C['tmd'])

    sliders['md_t'] = make_slider(2, 0, 'md — Masa TMD [t]',
                                   0.5, 20, 2.5, 0.1,
                                   slider_color=C['tmd_dark'],
                                   label_color=C['tmd_light'])
    sliders['cd']   = make_slider(2, 1, 'cd — Amort. TMD [N·s/m]',
                                   100, 5000, 1200, 50,
                                   slider_color=C['tmd_dark'],
                                   label_color=C['tmd_light'])
    sliders['kd_k'] = make_slider(2, 2, 'kd — Rigidez TMD [kN/m]',
                                   10, 500, 100, 5,
                                   slider_color=C['tmd_dark'],
                                   label_color=C['tmd_light'])

    # —— BOTONES (columna 3) ——
    fig.text(col_x[3] + btn_col_w / 2, B + H + 0.004, 'ACCIONES',
             ha='center', **cat_style, color=C['text_muted'])

    btn_w = btn_col_w * 0.90
    btn_h = 0.032
    btn_gap = 0.008
    btn_x = col_x[3] + (btn_col_w - btn_w) / 2

    # TMD toggle
    btn_y = row_tops[0] - lbl_h - btn_h + 0.005
    ax_tmd = fig.add_axes([btn_x, btn_y, btn_w, btn_h],
                           facecolor='#052E16')
    btn_tmd = Button(ax_tmd, 'TMD: ON', color='#052E16',
                     hovercolor='#064E3B')
    btn_tmd.label.set_fontsize(9)
    btn_tmd.label.set_color(C['safe'])
    btn_tmd.label.set_fontweight('bold')

    # Pausa
    btn_y -= btn_h + btn_gap
    ax_pause = fig.add_axes([btn_x, btn_y, btn_w, btn_h],
                             facecolor=C['bg_card'])
    btn_pause = Button(ax_pause, 'Pausa', color=C['bg_card'],
                       hovercolor=C['border'])
    btn_pause.label.set_fontsize(9)
    btn_pause.label.set_color(C['text'])

    # Resonancia
    btn_y -= btn_h + btn_gap
    ax_res = fig.add_axes([btn_x, btn_y, btn_w / 2 - 0.003, btn_h],
                           facecolor='#451A03')
    btn_res = Button(ax_res, 'Resonancia', color='#451A03',
                     hovercolor='#78350F')
    btn_res.label.set_fontsize(7.5)
    btn_res.label.set_color(C['warning'])

    # Sismo suave
    ax_soft = fig.add_axes(
        [btn_x + btn_w / 2 + 0.003, btn_y, btn_w / 2 - 0.003, btn_h],
        facecolor='#042F2E')
    btn_soft = Button(ax_soft, 'Suave', color='#042F2E',
                      hovercolor='#134E4A')
    btn_soft.label.set_fontsize(7.5)
    btn_soft.label.set_color(C['emerald'])

    # Reset y Teoría
    btn_y -= btn_h + btn_gap
    ax_rst = fig.add_axes([btn_x, btn_y, btn_w / 2 - 0.003, btn_h],
                           facecolor=C['bg_card'])
    btn_rst = Button(ax_rst, 'Reset', color=C['bg_card'],
                     hovercolor=C['border'])
    btn_rst.label.set_fontsize(8)
    btn_rst.label.set_color(C['text_sec'])

    ax_th = fig.add_axes(
        [btn_x + btn_w / 2 + 0.003, btn_y, btn_w / 2 - 0.003, btn_h],
        facecolor='#1E1B4B')
    btn_theory = Button(ax_th, 'Teoria', color='#1E1B4B',
                        hovercolor='#312E81')
    btn_theory.label.set_fontsize(8)
    btn_theory.label.set_color(C['indigo'])
    btn_theory.label.set_fontweight('bold')

    return (sliders, btn_tmd, btn_pause, btn_res, btn_soft,
            btn_rst, btn_theory)


# =============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN (REFACTORIZADA)
# =============================================================================

class SeismicApp:
    """
    Controlador principal: resuelve EDOs → anima → grafica → controla.
    """

    def __init__(self):
        self.params = dict(PARAMS)
        self.frame  = 0
        self.paused = False
        self._theory = TheoryWindow()

        # Construir la figura
        (self.fig,
         self.ax_bld, self.ax_disp,
         self.ax_seis, self.ax_info,
         ctrl_rect) = build_figure()

        # Construir controles
        (self.sliders,
         self.btn_tmd, self.btn_pause,
         self.btn_res, self.btn_soft,
         self.btn_rst, self.btn_theory) = build_controls(self.fig, ctrl_rect)

        # Resolver y dibujar
        self._solve()
        self._init_plots()
        self._connect()

        # Animación
        self.anim = FuncAnimation(
            self.fig, self._animate,
            interval=35, blit=False, cache_frame_data=False
        )

    # —— Solver ——

    def _solve(self):
        t, x, xd = solve_system(self.params)
        self.t_vec    = t
        self.x_vec    = x
        self.xd_vec   = xd
        x_max = np.max(np.abs(x)) if len(x) > 0 else 0.0
        self.state, self.state_color, self.state_label = classify_state(x_max)
        self.seis_vec = np.array([
            seismic_acceleration(ti, self.params['A'],
                                 self.params['omega_s'],
                                 self.params['alpha'])
            for ti in t
        ])

    # —— Plots iniciales ——

    def _init_plots(self):
        # Desplazamiento
        self.line_x, = self.ax_disp.plot(
            self.t_vec, self.x_vec, color=C['line_disp'], lw=1.6,
            label='Edificio x(t)', zorder=3, alpha=0.95)

        if self.xd_vec is not None:
            self.line_xd, = self.ax_disp.plot(
                self.t_vec, self.xd_vec, color=C['line_tmd'], lw=1.2,
                ls='--', alpha=0.8, label='TMD xd(t)', zorder=3)
        else:
            self.line_xd, = self.ax_disp.plot(
                [], [], color=C['line_tmd'], lw=1.2, ls='--',
                label='TMD xd(t)', zorder=3)

        # Zonas de daño
        self._draw_damage_zones()

        # Leyenda
        self.ax_disp.legend(
            loc='upper right', facecolor=C['bg_light'],
            edgecolor=C['border'], labelcolor=C['text'],
            fontsize=8, framealpha=0.9)

        # Indicador de tiempo
        self.vline1 = self.ax_disp.axvline(
            0, color=C['blue'], lw=1.0, alpha=0.6, zorder=5)
        self.vline2 = self.ax_seis.axvline(
            0, color=C['blue'], lw=1.0, alpha=0.6, zorder=5)

        # Sísmica
        self.line_s, = self.ax_seis.plot(
            self.t_vec, self.seis_vec, color=C['line_seis'], lw=1.4, zorder=3)
        self.fill_s = self.ax_seis.fill_between(
            self.t_vec, self.seis_vec, 0,
            color=C['line_seis'], alpha=0.10, zorder=2)

        self._update_lims()
        draw_info_panel(self.ax_info, self.params, self.t_vec,
                        self.x_vec, self.state_label, self.state_color)

    def _draw_damage_zones(self):
        ax = self.ax_disp
        ax.axhspan(0.05, 0.20, alpha=0.04, color=C['warning'], zorder=1)
        ax.axhspan(-0.20, -0.05, alpha=0.04, color=C['warning'], zorder=1)
        ax.axhspan(0.10, 0.20, alpha=0.05, color=C['danger'], zorder=1)
        ax.axhspan(-0.20, -0.10, alpha=0.05, color=C['danger'], zorder=1)
        for th, col in [(0.05, C['safe']), (0.10, C['warning']),
                         (0.20, C['danger'])]:
            ax.axhline(th, color=col, lw=0.6, ls=':', alpha=0.4)
            ax.axhline(-th, color=col, lw=0.6, ls=':', alpha=0.4)

    def _update_lims(self):
        xm = max(0.04, np.max(np.abs(self.x_vec))) * 1.35
        self.ax_disp.set_xlim(0, T_SIM)
        self.ax_disp.set_ylim(-xm, xm)
        am = max(0.5, np.max(np.abs(self.seis_vec))) * 1.2
        self.ax_seis.set_xlim(0, T_SIM)
        self.ax_seis.set_ylim(-am, am)

    # —— Animación ——

    def _animate(self, frame_num):
        n = len(self.t_vec)
        if n == 0:
            return

        if not self.paused:
            self.frame = frame_num % n

        x_now  = self.x_vec[self.frame]
        xd_now = self.xd_vec[self.frame] if self.xd_vec is not None else None
        t_now  = self.t_vec[self.frame]

        draw_building(self.ax_bld, x_now, xd_now,
                      self.params, self.state_color, self.frame)

        self.vline1.set_xdata([t_now, t_now])
        self.vline2.set_xdata([t_now, t_now])

        xi = abs(x_now)
        self.line_x.set_color(
            C['safe'] if xi < 0.05 else
            C['warning'] if xi < 0.10 else C['danger']
        )

    # —— Refresh ——

    def _refresh(self):
        self._solve()
        self.frame = 0
        self.line_x.set_data(self.t_vec, self.x_vec)
        if self.xd_vec is not None:
            self.line_xd.set_data(self.t_vec, self.xd_vec)
        else:
            self.line_xd.set_data([], [])
        self.line_s.set_data(self.t_vec, self.seis_vec)

        self.fill_s.remove()
        self.fill_s = self.ax_seis.fill_between(
            self.t_vec, self.seis_vec, 0,
            color=C['line_seis'], alpha=0.10, zorder=2)

        self._update_lims()
        draw_info_panel(self.ax_info, self.params, self.t_vec,
                        self.x_vec, self.state_label, self.state_color)
        self.fig.canvas.draw_idle()

    # —— Callbacks ——

    def _connect(self):
        sl = self.sliders

        def on_change(val):
            self.params['m']       = sl['m_t'].val * 1000.0
            self.params['c']       = sl['c_k'].val * 1000.0
            self.params['k']       = sl['k_M'].val * 1e6
            self.params['A']       = sl['A'].val
            self.params['omega_s'] = sl['ws'].val
            self.params['alpha']   = sl['al'].val
            self.params['m_d']     = sl['md_t'].val * 1000.0
            self.params['c_d']     = sl['cd'].val
            self.params['k_d']     = sl['kd_k'].val * 1000.0
            self._refresh()

        for s in sl.values():
            s.on_changed(on_change)

        def on_tmd(event):
            self.params['tmd_active'] = not self.params['tmd_active']
            if self.params['tmd_active']:
                self.btn_tmd.label.set_text('TMD: ON')
                self.btn_tmd.label.set_color(C['safe'])
                self.btn_tmd.color = '#052E16'
                self.btn_tmd.ax.set_facecolor('#052E16')
            else:
                self.btn_tmd.label.set_text('TMD: OFF')
                self.btn_tmd.label.set_color(C['danger'])
                self.btn_tmd.color = '#450A0A'
                self.btn_tmd.ax.set_facecolor('#450A0A')
            self._refresh()

        self.btn_tmd.on_clicked(on_tmd)

        def on_pause(event):
            self.paused = not self.paused
            if self.paused:
                self.btn_pause.label.set_text('Reanudar')
                self.btn_pause.label.set_color(C['safe'])
            else:
                self.btn_pause.label.set_text('Pausa')
                self.btn_pause.label.set_color(C['text'])
            self.fig.canvas.draw_idle()

        self.btn_pause.on_clicked(on_pause)

        def on_resonance(event):
            omega_n = np.sqrt(self.params['k'] / self.params['m'])
            sl['ws'].set_val(round(omega_n, 2))
            sl['A'].set_val(5.0)
            sl['al'].set_val(0.05)

        self.btn_res.on_clicked(on_resonance)

        def on_soft(event):
            sl['A'].set_val(1.0)
            sl['ws'].set_val(3.14)
            sl['al'].set_val(0.30)

        self.btn_soft.on_clicked(on_soft)

        def on_reset(event):
            for k, v in PARAMS.items():
                self.params[k] = v
            sl['m_t'].set_val(50.0)
            sl['c_k'].set_val(15.0)
            sl['k_M'].set_val(2.0)
            sl['A'].set_val(3.0)
            sl['ws'].set_val(6.28)
            sl['al'].set_val(0.15)
            sl['md_t'].set_val(2.5)
            sl['cd'].set_val(1200.0)
            sl['kd_k'].set_val(100.0)
            self.params['tmd_active'] = True
            self.btn_tmd.label.set_text('TMD: ON')
            self.btn_tmd.label.set_color(C['safe'])
            self.btn_tmd.color = '#052E16'
            self.btn_tmd.ax.set_facecolor('#052E16')
            self._refresh()

        self.btn_rst.on_clicked(on_reset)

        def on_theory(event):
            self._theory.show()

        self.btn_theory.on_clicked(on_theory)

    def run(self):
        plt.show()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == '__main__':
    banner = """
+--------------------------------------------------------------------------+
|     SIMULACION SISMICA PROFESIONAL v3.0                                  |
|     Analisis Matematico II  -  Ecuaciones Diferenciales                  |
+--------------------------------------------------------------------------+
|  SDOF:   m*x'' + c*x' + k*x = F(t)                                      |
|  F(t) = -m*A*sin(ws*t)*exp(-a*t)                                        |
|  2DOF:   m*x'' + c*x' + k*x - cd*(xd'-x') - kd*(xd-x) = F(t)          |
|          md*xd'' + cd*(xd'-x') + kd*(xd-x) = 0                         |
|  Metodo: scipy.integrate.solve_ivp  [RK45]                              |
+--------------------------------------------------------------------------+
"""
    try:
        print(banner)
        print('  Iniciando interfaz grafica profesional...\n')
    except UnicodeEncodeError:
        print('  Iniciando simulacion sismica v3.0...\n')

    app = SeismicApp()
    app.run()
