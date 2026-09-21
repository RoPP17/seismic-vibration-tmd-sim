import numpy as np
from scipy.integrate import solve_ivp
from models.parameters import T_SIM, DT

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
        return sol.t, sol.y[0], sol.y[1], sol.y[2]
    else:
        sol = solve_ivp(ode_sdof, (0, T_SIM), [0, 0],
                        args=(m, c, k, A, ws, al),
                        method='RK45', t_eval=t_eval, rtol=1e-6, atol=1e-8)
        return sol.t, sol.y[0], sol.y[1], None
