import sys
import pyodbc
import os
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from Modules.style import RoundedWindow
from Modules.resources import ICON_PATH  

class MainWindow(RoundedWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestión de Régimen")
        self.setGeometry(100, 100, 400, 320)

        # Verificar que la ruta del ícono existe
        if os.path.exists(ICON_PATH):
            print(f"Ícono encontrado en: {ICON_PATH}")
            self.setWindowIcon(QIcon(ICON_PATH))  
        else:
            print("⚠️ Ícono no encontrado. Verifica la ruta.")

        layout = QVBoxLayout()

        # Campo para CUIL
        self.label_cuil = QLabel("Ingrese CUIL:")
        layout.addWidget(self.label_cuil)

        self.cuil_input = QLineEdit()
        self.cuil_input.setPlaceholderText("CUIL (11 dígitos)")
        layout.addWidget(self.cuil_input)

        # Botón para buscar
        self.buscar_button = QPushButton("Buscar")
        self.buscar_button.clicked.connect(self.buscar_persona)
        layout.addWidget(self.buscar_button)

        # Etiquetas para mostrar los datos obtenidos
        self.label_nombre = QLabel("Nombre:")
        layout.addWidget(self.label_nombre)

        self.label_fec_nac = QLabel("Fecha de Nacimiento:")
        layout.addWidget(self.label_fec_nac)

        self.label_regimen_actual = QLabel("Régimen Actual:")
        layout.addWidget(self.label_regimen_actual)

        # ComboBox para seleccionar el nuevo régimen
        self.label_regimen = QLabel("Seleccione Nuevo Régimen:")
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
        """Muestra un mensaje emergente"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(icon)
        msg_box.exec()

    def buscar_persona(self):
        """Ejecuta el procedimiento almacenado y muestra los datos de la persona y su régimen actual."""
        cuil = self.cuil_input.text().strip()

        if len(cuil) != 11 or not cuil.isdigit():
            self.mostrar_mensaje("Error", "El CUIL debe tener exactamente 11 dígitos numéricos.", QMessageBox.Warning)
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            # Obtener datos personales
            cursor.execute("EXEC Gestion.dbo.Anto_ObtenerPersonaPorCUIL @CUIL = ?", (cuil,))
            resultado_persona = cursor.fetchone()

            if resultado_persona:
                nombre = resultado_persona.Apeynom
                fecha_nac = resultado_persona.Fec_nac.strftime("%d/%m/%Y") if resultado_persona.Fec_nac else "No disponible"

                self.label_nombre.setText(f"Nombre: {nombre}")
                self.label_fec_nac.setText(f"Fecha de Nacimiento: {fecha_nac}")
            else:
                self.label_nombre.setText("Nombre: No encontrado")
                self.label_fec_nac.setText("Fecha de Nacimiento: No encontrado")

            # Obtener régimen actual
            cursor.execute("EXEC Gestion.dbo.anto_regimenactual @CUIL = ?", (cuil,))
            resultado_regimen = cursor.fetchone()

            if resultado_regimen:
                regimen_actual = resultado_regimen.REGIMEN
                self.label_regimen_actual.setText(f"Régimen Actual: {regimen_actual}")
            else:
                self.label_regimen_actual.setText("Régimen Actual: No encontrado")

        except pyodbc.Error as e:
            print("Error al ejecutar la consulta:", e)
            self.mostrar_mensaje("Error", "No se pudo obtener los datos.", QMessageBox.Critical)
        finally:
            conn.close()

    def guardar_regimen(self):
        """Ejecuta el procedimiento almacenado para actualizar el régimen de la persona."""
        cuil = self.cuil_input.text().strip()
        nuevo_regimen = self.regimen_combo.currentData()

        if len(cuil) != 11 or not cuil.isdigit():
            self.mostrar_mensaje("Error", "El CUIL debe tener exactamente 11 dígitos numéricos.", QMessageBox.Warning)
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            cursor.execute("""
                EXEC Gestion.dbo.Anto_CambiarRegimen @CUIL = ?, @NuevoRegimen = ?
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
    """Intenta conectarse a la base de datos usando diferentes drivers."""
    drivers = [
        'ODBC Driver 17 for SQL Server',  
        'SQL Server Native Client 11.0',  
        'SQL Server Native Client 10.0',  
        'SQL Server',  
    ]
    server = 'SQL01'
    database = 'Gestion'

    for driver in drivers:
        conexion_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )
        try:
            conexion = pyodbc.connect(conexion_str)
            return conexion
        except pyodbc.Error:
            continue

    raise Exception("No se pudo conectar a la base de datos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
