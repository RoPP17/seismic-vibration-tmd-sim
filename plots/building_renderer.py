import numpy as np
import matplotlib.colors
from matplotlib.patches import FancyBboxPatch, Polygon

from styles.theme import C, STRESS_CMAP
from simulation.solver import seismic_acceleration

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

def draw_building(ax, x_disp, x_tmd_disp, params, state_color, t_now):
    """Renderiza el edificio con deformación dinámica y TMD (Dark Theme)."""
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
    F_t = seismic_acceleration(t_now, params['A'],
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
    ax.text(0, lbl_y, f'x = {disp_cm:+.2f} cm',
            ha='center', va='bottom', color=state_color,
            fontsize=11, fontweight='bold', zorder=15,
            bbox=dict(facecolor=C['bg_light'], edgecolor=state_color,
                      boxstyle='round,pad=0.3', alpha=0.9))

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
                    color=state_color, alpha=0.5, zorder=5)
    ax.scatter([bar_x], [ind_y], s=40, color=state_color, zorder=6,
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
    ax.set_title('Modelo Estructural 2DOF', color=C['text'], fontsize=11,
                 pad=10, fontweight='bold')
