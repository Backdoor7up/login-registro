from PyQt6.QtWidgets import QStackedWidget

from ventanas.ventana_login import VentanaLogin
from ventanas.ventana_registro import VentanaRegistro


class VentanaPrincipal(QStackedWidget):
    """Mantiene ambas pantallas y muestra una por vez."""

    def __init__(self, servicio):
        super().__init__()
        self.login = VentanaLogin(servicio)
        self.registro = VentanaRegistro(servicio)
        self.addWidget(self.login)
        self.addWidget(self.registro)
        self.setFixedSize(500, 600)
        self.setWindowTitle("Iniciar sesión")
        self.setCurrentWidget(self.login)

        self.login.btn_ir_registro.clicked.connect(self.mostrar_registro)
        self.registro.btn_volver_login.clicked.connect(self.mostrar_login)
        self.registro.registro_exitoso.connect(self._al_registrar)

    def mostrar_login(self):
        self.login.label_mensaje.clear()
        self.setCurrentWidget(self.login)
        self.setWindowTitle("Iniciar sesión")
        self.login.input_usuario.setFocus()

    def mostrar_registro(self):
        self.registro.label_mensaje.clear()
        self.setCurrentWidget(self.registro)
        self.setWindowTitle("Crear cuenta")
        self.registro.input_nombre.setFocus()

    def _al_registrar(self, usuario):
        self.mostrar_login()
        self.login.input_usuario.setText(usuario)
        self.login.input_password.clear()
        self.login._mostrar_mensaje(
            "Cuenta creada. Iniciá sesión con tus datos.", "exito"
        )
        self.login.input_password.setFocus()