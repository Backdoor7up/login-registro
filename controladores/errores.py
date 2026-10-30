class ErrorPersistencia(RuntimeError):
    """Error de acceso o escritura en la base de datos."""


class UsuarioDuplicadoError(ValueError):
    """El nombre de usuario ya está registrado."""
