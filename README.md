# 🏢 SeismicDynamics — Simulador de Dinámica Sísmica Estructural (SDOF & 2DOF + TMD)

[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![NumPy](https://img.shields.io/badge/NumPy-Math-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-RK45%20Solver-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> **Simulador dinámico y laboratorio computacional de vibraciones estructurales** desarrollado para el estudio de **Ecuaciones Diferenciales Ordinarias** y **Dinámica de Estructuras** en la **Universidad Técnica de Ambato (UTA)**.

---

## 🔬 Fundamentos Físicos y Modelado Matemático

El sistema resuelve numéricamente la respuesta dinámica no estacionaria de una edificación sometida a excitación sísmica en la base mediante el algoritmo de **Runge-Kutta-Fehlberg adaptativo de orden 4(5) (RK45)** vía `scipy.integrate.solve_ivp`.

### 1. Sistema de 1 Grado de Libertad (SDOF)
$$m \ddot{x}(t) + c \dot{x}(t) + k x(t) = F(t)$$

Donde la excitación sísmica modulada en la base se modela como:
$$F(t) = -m A \sin(\omega_s t) e^{-lpha t}$$

* $m$: Masa de la estructura principal.
* $k$: Rigidez lateral del pórtico.
* $c = 2 \zeta \sqrt{k m}$: Coeficiente de amortiguamiento viscoso.
* $A, \omega_s, lpha$: Amplitud, frecuencia dominante y factor de atenuación sísmica.

### 2. Sistema de 2 Grados de Libertad con Disipador TMD (2DOF + TMD)
Para mitigar la resonancia destructiva, se incorpora en la corona del edificio un **Amortiguador de Masa Sintonizada (Tuned Mass Damper - TMD)**:

$$egin{cases}
m \ddot{x} + c \dot{x} + k x - c_d (\dot{x}_d - \dot{x}) - k_d (x_d - x) = F(t) \
m_d \ddot{x}_d + c_d (\dot{x}_d - \dot{x}) + k_d (x_d - x) = 0
\end{cases}$$

Reducción de orden al espacio de estados para integración continua:
$$\mathbf{z} = [x, \dot{x}, x_d, \dot{x}_d]^T \implies \dot{\mathbf{z}} = \mathbf{A} \mathbf{z} + \mathbf{B}(t)$$

---

## 🌟 Características de la Aplicación

1. **Simulación Temporal Continua:** Comparación lado a lado de la estructura libre vs. estructura protegida con TMD.
2. **Animación en Tiempo Real:** Renderizado interactivo de la deflexión lateral del pórtico y oscilación en contrafase del disipador inercial.
3. **Espectro de Frecuencia & Planos de Fase:** Curvas de respuesta en frecuencia (Magnificación Dinámica vs. $\omega/\omega_n$) y trayectorias en el espacio de fases $(x, \dot{x})$.
4. **Control Paramétrico:** Ajuste de masa, amortiguamiento, rigidez, masa del TMD y relación de frecuencias de sintonización.
5. **Modos de Ejecución:**
   * **Suite Modular PyQt5 (`main.py`):** Interfaz gráfica completa con pestañas de teoría, parámetros, gráficas y animación.
   * **Versión Standalone (`standalone_interactive_sismo.py`):** Script único de 1,750+ líneas en Matplotlib interactivo para ejecución rápida en cualquier entorno.

---

## 🚀 Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/RoPP17/seismic-vibration-tmd-sim.git
cd seismic-vibration-tmd-sim

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el simulador modular PyQt5
python main.py

# O ejecutar la versión standalone interactiva en Matplotlib
python standalone_interactive_sismo.py
```

---

## 📄 Documentación Académica

El repositorio incluye en [`docs/`](docs/) el informe oficial de investigación:
* **`Proyecto_Analisis_Dinamica_Sismica.pdf`**: Derivación analítica paso a paso de las ecuaciones diferenciales, solución homogénea y particular, análisis de resonancia y cálculo del factor de sintonía óptimo de Den Hartog.

---

## 👨‍💻 Autor

* **Roberto Andrés Pepe Sánchez** — Facultad de Ingeniería Civil y Mecánica, [Universidad Técnica de Ambato (UTA)](https://uta.edu.ec/)

## 📜 Licencia

Distribuido bajo la Licencia [MIT](LICENSE).
