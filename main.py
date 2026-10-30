import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMessageBox

from controladores.autenticacion import ServicioAutenticacion
from controladores.errores import ErrorPersistencia
from controladores.repositorio_usuarios import RepositorioUsuariosMySQL
from ventanas.ventana_principal import VentanaPrincipal

RUTA_PROYECTO = Path(__file__).parent
RUTA_ESTILOS = Path(__file__).parent / "ventanas" / "estilos.qss"


def cargar_estilos(app):
    try:
        app.setStyleSheet(RUTA_ESTILOS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Aviso: no se encontro {RUTA_ESTILOS}. Se usara el estilo predeterminado.")


def main():
    load_dotenv(RUTA_PROYECTO / ".env")
    app = QApplication(sys.argv)
    cargar_estilos(app)

    try:
        repositorio = RepositorioUsuariosMySQL.desde_entorno()
    except (mysql.connector.Error, ErrorPersistencia, ValueError) as error:
        print(f"No se pudo iniciar la aplicación: {error}", file=sys.stderr)
        QMessageBox.critical(
            None,
            "No se pudo conectar con MySQL",
            "Verificá que MySQL esté iniciado y que los datos de conexión "
            "del archivo .env sean correctos.",
        )
        return 1

    servicio = ServicioAutenticacion(repositorio)
    ventana = VentanaPrincipal(servicio)
    app.aboutToQuit.connect(repositorio.cerrar)
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())