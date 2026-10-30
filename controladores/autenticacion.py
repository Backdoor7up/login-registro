import hashlib
import hmac
import os
from typing import Protocol

LONGITUD_MINIMA_PASSWORD = 8
ITERACIONES = 600_000


class RepositorioUsuarios(Protocol):
    def obtener_credenciales(self, usuario: str) -> dict[str, bytes] | None: ...

    def crear_usuario(
        self,
        nombre: str,
        apellido: str,
        usuario: str,
        password_hash: bytes,
        password_salt: bytes,
    ) -> None: ...


class ServicioAutenticacion:
    """Aplica las reglas de autenticación sin conocer el motor de base de datos."""

    def __init__(self, repositorio: RepositorioUsuarios):
        self._repositorio = repositorio

    def registrar(self, nombre, apellido, usuario, password):
        clave = usuario.strip().casefold()
        nombre = nombre.strip()
        apellido = apellido.strip()
        if not nombre or not apellido or not clave:
            raise ValueError("Nombre, apellido y usuario son obligatorios.")
        if len(password) < LONGITUD_MINIMA_PASSWORD:
            raise ValueError(
                f"La contraseña necesita al menos {LONGITUD_MINIMA_PASSWORD} caracteres."
            )

        sal = os.urandom(16)
        password_hash = self._calcular_hash(password, sal)
        self._repositorio.crear_usuario(
            nombre, apellido, clave, password_hash, sal
        )

    def autenticar(self, usuario, password):
        registro = self._repositorio.obtener_credenciales(
            usuario.strip().casefold()
        )
        if registro is None:
            return False
        hash_ingresado = self._calcular_hash(password, registro["password_salt"])
        return hmac.compare_digest(hash_ingresado, registro["password_hash"])

    @staticmethod
    def _calcular_hash(password, sal):
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), sal, ITERACIONES
        )
