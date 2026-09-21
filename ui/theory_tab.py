from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from styles.theme import C

class TheoryTab(QWidget):
    """Pestaña con teoría matemática exhaustiva y rigurosa, adaptada al tema oscuro con márgenes elegantes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {C['bg']};
                color: {C['text']};
                border: none;
                selection-background-color: {C['blue']};
                selection-color: white;
            }}
        """)
        self.browser.setHtml(self._build_html())
        layout.addWidget(self.browser)

    def _build_html(self):
        bg = C['bg']
        bg2 = C['bg_light']
        bg3 = C['bg_card']
        txt = C['text']
        txs = C['text_sec']
        txm = C['text_muted']
        blu = C['blue']
        cya = C['cyan']
        amb = C['amber']
        emr = C['emerald']
        ros = C['rose']
        pur = C['purple']
        
        # Estilos inline reutilizables con bordes muy redondeados (evitar lo 'cuadrado')
        # Qt Rich Text soporta border-radius
        
        card_style = (f'background-color: {bg3}; margin: 20px 10px; padding: 25px; '
                      f'border-radius: 16px; border: 1px solid {C["border"]};')
                      
        step_badge = (f'background-color: {blu}; color: white; padding: 6px 14px; '
                      f'border-radius: 12px; font-weight: bold; font-size: 14px;')
                      
        s_eq = (f'background-color: {bg2}; padding: 18px; margin: 15px 10px; '
                f'text-align: center; color: {C["text_bright"]}; font-size: 18px; '
                f'border: 1px solid {C["border_light"]}; border-radius: 12px; '
                f'font-family: Consolas, "Cambria Math", monospace;')
                
        s_eq_highlight = (f'background-color: #1A2235; padding: 20px; margin: 15px 10px; '
                          f'text-align: center; color: {cya}; font-size: 19px; '
                          f'font-weight: bold; border: 2px solid {blu}; border-radius: 12px; '
                          f'font-family: Consolas, "Cambria Math", monospace;')
                          
        s_note = (f'background-color: rgba(16, 185, 129, 0.1); padding: 16px 20px; '
                  f'margin: 15px 10px; color: #A7F3D0; font-size: 14.5px; '
                  f'border-left: 5px solid {emr}; border-radius: 0px 12px 12px 0px;')

        return f"""
<html>
<body style="background-color: {bg}; color: {txt};
             font-family: 'Segoe UI', Verdana, Arial, sans-serif;
             font-size: 15px; line-height: 1.8;
             padding: 30px 50px;">

<!-- TÍTULO PRINCIPAL -->
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="color: {C['text_bright']}; font-size: 34px; margin-bottom: 5px;">
        Fundamentos Matemáticos del Simulador
    </h1>
    <p style="color: {blu}; font-size: 16px; font-weight: bold; margin-top: 0px;">
        Modelado de Estructuras Sometidas a Sismos (Paso a Paso)
    </p>
</div>

<!-- PASO 1 -->
<div style="{card_style}">
    <span style="{step_badge}">PASO 1</span>
    <h2 style="color: {C['text_bright']}; font-size: 22px; margin-top: 15px; margin-bottom: 10px;">
        La Segunda Ley de Newton Aplicada a Edificios
    </h2>
    <p>Todo el análisis dinámico de estructuras parte de la <b>Segunda Ley de Newton</b>. Para un edificio que se desplaza horizontalmente debido a un sismo, el movimiento se rige por el equilibrio dinámico. Si consideramos al edificio como una masa concentrada en la parte superior (modelo SDOF), tenemos:</p>
    
    <div style="{s_eq}">
        Σ F = m · a
    </div>
    
    <p>Donde <b>m</b> es la masa del edificio y <b>a</b> (o <i>ẍ</i>) es su aceleración relativa. Las fuerzas internas que se oponen al movimiento son:</p>
    <ul style="color: {txs};">
        <li><b>Fuerza Restauradora (Resorte):</b> Proviene de la rigidez de columnas y muros. Es proporcional al desplazamiento. <i>F_k = k · x</i></li>
        <li><b>Fuerza Disipativa (Amortiguador):</b> Fricción interna y micro-fisuras. Es proporcional a la velocidad. <i>F_c = c · ẋ</i></li>
    </ul>
</div>

<!-- PASO 2 -->
<div style="{card_style}">
    <span style="{step_badge}">PASO 2</span>
    <h2 style="color: {C['text_bright']}; font-size: 22px; margin-top: 15px; margin-bottom: 10px;">
        Ecuación Diferencial del Sistema SDOF
    </h2>
    <p>Igualando las fuerzas internas con la fuerza externa inducida por el sismo <b>F(t)</b>, obtenemos la Ecuación Diferencial Ordinaria (EDO) de segundo orden que define el comportamiento de nuestro edificio en el tiempo:</p>
    
    <div style="{s_eq_highlight}">
        m·ẍ(t) + c·ẋ(t) + k·x(t) = F(t)
    </div>
    
    <div style="{s_note}">
        <b>Significado Físico:</b><br>
        • <b>m·ẍ</b> : Fuerza de Inercia (cómo la masa se resiste a cambiar su estado).<br>
        • <b>c·ẋ</b> : Fuerza de Amortiguamiento (disipa la energía del sismo).<br>
        • <b>k·x</b> : Fuerza Elástica (intenta devolver al edificio a su posición vertical).
    </div>
</div>

<!-- PASO 3 -->
<div style="{card_style}">
    <span style="{step_badge}">PASO 3</span>
    <h2 style="color: {C['text_bright']}; font-size: 22px; margin-top: 15px; margin-bottom: 10px;">
        Añadiendo el TMD (Amortiguador de Masa Sintonizado)
    </h2>
    <p>Para reducir las vibraciones (evitar el colapso), añadimos una pequeña masa <b>m_d</b> en la azotea, conectada mediante su propio resorte (<b>k_d</b>) y amortiguador (<b>c_d</b>). El sistema pasa a tener <b>Dos Grados de Libertad (2DOF)</b>.</p>
    <p>El sistema se acopla, generando un sistema de dos ecuaciones diferenciales simultáneas:</p>
    
    <div style="{s_eq}">
        <b>Edificio:</b> m·ẍ + c·ẋ + k·x − c_d·(ẋ_d − ẋ) − k_d·(x_d − x) = F(t)<br><br>
        <b>TMD:</b> m_d·ẍ_d + c_d·(ẋ_d − ẋ) + k_d·(x_d − x) = 0
    </div>
    
    <p>Al vibrar, el TMD se mueve en <b>desfase</b> respecto al edificio principal. La energía sísmica se transfiere del edificio al TMD, que se encarga de disiparla agresivamente.</p>
</div>

<!-- PASO 4 -->
<div style="{card_style}">
    <span style="{step_badge}">PASO 4</span>
    <h2 style="color: {C['text_bright']}; font-size: 22px; margin-top: 15px; margin-bottom: 10px;">
        Solución Computacional (Método Numérico RK45)
    </h2>
    <p>Las computadoras no resuelven ecuaciones de 2º orden directamente. Debemos transformar nuestro sistema de 2 EDOs de 2º orden en <b>4 EDOs de 1º orden</b>. Definimos el vector de estado <b>Y</b>:</p>
    
    <div style="{s_eq}">
        Y = [ x, x_d, ẋ, ẋ_d ]ᵀ
    </div>
    
    <p>Y calculamos su derivada respecto al tiempo <b>dY/dt</b> en cada instante. Nuestro simulador utiliza el algoritmo <b>Runge-Kutta de orden 4(5)</b> de la librería SciPy. Este método aproxima la curva de respuesta paso a paso (dt = 0.02s) garantizando alta precisión y estabilidad para sismos severos.</p>
</div>

<br><br>
</body>
</html>
"""
