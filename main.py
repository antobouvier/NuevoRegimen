import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from Modules.style import RoundedWindow
import pyodbc

class MainWindow(RoundedWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestión de Régimen")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Campo para CUIL
        self.label_cuil = QLabel("Ingrese CUIL:")
        layout.addWidget(self.label_cuil)

        self.cuil_input = QLineEdit()
        self.cuil_input.setPlaceholderText("CUIL (11 dígitos)")
        layout.addWidget(self.cuil_input)

        # ComboBox para Régimen
        self.label_regimen = QLabel("Seleccione Régimen:")
        layout.addWidget(self.label_regimen)

        self.regimen_combo = QComboBox()
        self.regimen_combo.addItem("Docentes", 1)
        self.regimen_combo.addItem("Régimen Común", 2)
        self.regimen_combo.addItem("Régimen Policial", 3)
        layout.addWidget(self.regimen_combo)

        # Botón para guardar
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.guardar_regimen)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def mostrar_mensaje(self, titulo, mensaje, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(icon)
        msg_box.exec()

    def guardar_regimen(self):
        cuil = self.cuil_input.text().strip()
        nuevo_regimen = self.regimen_combo.currentData()

        # Validaciones básicas
        if len(cuil) != 11 or not cuil.isdigit():
            self.mostrar_mensaje("Error", "El CUIL debe tener exactamente 11 dígitos numéricos.", QMessageBox.Warning)
            return

        try:
            # Ejecutar procedimiento almacenado
            conn = obtener_conexion()
            cursor = conn.cursor()

            cursor.execute("""
                EXEC nuevo_regimen @CUIL = ?, @NuevoRegimen = ?
            """, (cuil, nuevo_regimen))

            conn.commit()
            self.mostrar_mensaje("Éxito", "Régimen actualizado correctamente.")

        except pyodbc.Error as e:
            print("Error al ejecutar el procedimiento almacenado:", e)
            self.mostrar_mensaje("Error", "No se pudo actualizar el régimen.", QMessageBox.Critical)
        finally:
            conn.close()

# Conexión a la base de datos
def obtener_conexion():
    drivers = [
        'ODBC Driver 17 for SQL Server',  # Preferido y más reciente
        'SQL Server Native Client 11.0',  # Native Client version 11
        'SQL Server Native Client 10.0',  # Native Client version 10
        'SQL Server',  # Generic ODBC driver name (legacy)
    ]
    server = 'PC-2193'
    database = 'Aportes'

    for driver in drivers:
        conexion_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )
        try:
            print(f"Intentando conectar con el driver: {driver}")
            conexion = pyodbc.connect(conexion_str)
            print(f"Conexión exitosa con el driver: {driver}")
            return conexion
        except pyodbc.Error as error:
            print(f"Error al intentar conectar con el driver: {driver}")
            print(error)
    
    raise Exception("No se pudo conectar a la base de datos con ninguno de los drivers disponibles.")

# Configuración y ejecución de la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
