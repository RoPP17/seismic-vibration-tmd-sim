import csv
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def export_to_csv(parent, t_vec, x_vec, v_vec, seis_vec, xd_vec):
    """Exporta los datos de simulación actuales a un archivo CSV."""
    if len(t_vec) == 0:
        QMessageBox.warning(parent, "Advertencia", "No hay datos para exportar.")
        return
        
    path, _ = QFileDialog.getSaveFileName(parent, "Exportar Datos", "", "CSV Files (*.csv)")
    if not path:
        return
        
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if xd_vec is not None:
                writer.writerow(["Tiempo [s]", "Despl. Edificio [m]", "Velocidad [m/s]", "Acel. Suelo [m/s2]", "Despl. TMD [m]"])
                for t, x, v, a, xd in zip(t_vec, x_vec, v_vec, seis_vec, xd_vec):
                    writer.writerow([f"{t:.4f}", f"{x:.6f}", f"{v:.6f}", f"{a:.6f}", f"{xd:.6f}"])
            else:
                writer.writerow(["Tiempo [s]", "Despl. Edificio [m]", "Velocidad [m/s]", "Acel. Suelo [m/s2]"])
                for t, x, v, a in zip(t_vec, x_vec, v_vec, seis_vec):
                    writer.writerow([f"{t:.4f}", f"{x:.6f}", f"{v:.6f}", f"{a:.6f}"])
                    
        QMessageBox.information(parent, "Éxito", f"Datos exportados correctamente a:\n{path}")
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Error al exportar:\n{str(e)}")
