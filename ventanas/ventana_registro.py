from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QWidget

from controladores.autenticacion import LONGITUD_MINIMA_PASSWORD
from controladores.errores import ErrorPersistencia

RUTA_UI = Path(__file__).parent / "registro.ui"


class VentanaRegistro(QWidget):
    """Controla el formulario de registro."""

    registro_exitoso = pyqtSignal(str)

    def __init__(self, servicio):
        super().__init__()
        self.servicio = servicio
        uic.loadUi(RUTA_UI, self)
        self._conectar_eventos()

    def _conectar_eventos(self):
        self.btn_registrar.clicked.connect(self.registrar)
        self.input_confirmar_password.returnPressed.connect(self.registrar)
        self.chk_mostrar_password.toggled.connect(self.alternar_password)
        self.input_nombre.returnPressed.connect(self.input_apellido.setFocus)
        self.input_apellido.returnPressed.connect(self.input_usuario.setFocus)
        self.input_usuario.returnPressed.connect(self.input_password.setFocus)
        self.input_password.returnPressed.connect(self.input_confirmar_password.setFocus)

    def _leer_formulario(self):
        return {
            "nombre": self.input_nombre.text().strip(),
            "apellido": self.input_apellido.text().strip(),
            "usuario": self.input_usuario.text().strip(),
            "password": self.input_password.text(),
            "confirmacion": self.input_confirmar_password.text(),
        }

    def _validar(self, datos):
        if not datos["nombre"]:
            return "Completá tu nombre."
        if not datos["apellido"]:
            return "Completá tu apellido."
        if not datos["usuario"]:
            return "Completá tu usuario o correo electrónico."
        if len(datos["password"]) < LONGITUD_MINIMA_PASSWORD:
            return f"La contraseña necesita al menos {LONGITUD_MINIMA_PASSWORD} caracteres."
        if datos["password"] != datos["confirmacion"]:
            return "Las contraseñas no coinciden."
        return None

    def registrar(self):
        datos = self._leer_formulario()
        error = self._validar(datos)
        if error:
            self._mostrar_mensaje(error, "error")
            return

        try:
            self.servicio.registrar(
                datos["nombre"], datos["apellido"], datos["usuario"], datos["password"]
            )
        except (ValueError, ErrorPersistencia) as error:
            self._mostrar_mensaje(str(error), "error")
            return

        self.registro_exitoso.emit(datos["usuario"])

    def alternar_password(self, visible):
        modo = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.input_password.setEchoMode(modo)
        self.input_confirmar_password.setEchoMode(modo)

    def _mostrar_mensaje(self, texto, tipo="info"):
        self.label_mensaje.setText(texto)
        self.label_mensaje.setProperty("tipo", tipo)
        self.label_mensaje.style().unpolish(self.label_mensaje)
        self.label_mensaje.style().polish(self.label_mensaje)