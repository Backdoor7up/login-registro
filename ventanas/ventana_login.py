from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QLineEdit, QWidget

from controladores.errores import ErrorPersistencia

RUTA_UI = Path(__file__).parent / "login.ui"


class VentanaLogin(QWidget):
    """Controla la pantalla de inicio de sesión. El diseño vive en login.ui."""

    def __init__(self, servicio):
        super().__init__()
        self.servicio = servicio
        uic.loadUi(RUTA_UI, self)
        self._conectar_eventos()

    def _conectar_eventos(self):
        self.btn_login.clicked.connect(self.iniciar_sesion)
        self.input_password.returnPressed.connect(self.iniciar_sesion)
        self.chk_mostrar_password.toggled.connect(self.alternar_password)
        self.input_usuario.returnPressed.connect(self.input_password.setFocus)

    def iniciar_sesion(self):
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()
        error = self._validar(usuario, password)
        if error:
            self._mostrar_mensaje(error, "error")
            return

        try:
            autenticado = self.servicio.autenticar(usuario, password)
        except ErrorPersistencia as error:
            self._mostrar_mensaje(str(error), "error")
            return

        if autenticado:
            self._mostrar_mensaje(f"Sesión iniciada como {usuario}.", "exito")
        else:
            self._mostrar_mensaje("Usuario o contraseña incorrectos.", "error")

    @staticmethod
    def _validar(usuario, password):
        if not usuario:
            return "Ingresa tu usuario o correo electrónico."
        if not password:
            return "Ingresa tu contraseña."
        return None

    def alternar_password(self, visible):
        modo = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.input_password.setEchoMode(modo)

    def _mostrar_mensaje(self, texto, tipo="info"):
        self.label_mensaje.setText(texto)
        self.label_mensaje.setProperty("tipo", tipo)
        self.label_mensaje.style().unpolish(self.label_mensaje)
        self.label_mensaje.style().polish(self.label_mensaje)