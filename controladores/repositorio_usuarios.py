import os

import mysql.connector
from mysql.connector import IntegrityError
from mysql.connector.errorcode import ER_DUP_ENTRY

from controladores.errores import ErrorPersistencia, UsuarioDuplicadoError


class RepositorioUsuariosMySQL:
    """Lee y escribe usuarios en MySQL."""

    def __init__(self, host, port, user, password, database):
        self._conexion = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            use_unicode=True,
        )
        try:
            self._crear_tabla()
        except mysql.connector.Error as error:
            self._conexion.close()
            raise ErrorPersistencia(
                "No se pudo preparar la tabla de usuarios en MySQL."
            ) from error

    @classmethod
    def desde_entorno(cls):
        password = os.getenv("MYSQL_PASSWORD")
        if password is None:
            raise ValueError("Falta configurar MYSQL_PASSWORD en el archivo .env.")

        try:
            port = int(os.getenv("MYSQL_PORT", "3306"))
        except ValueError as error:
            raise ValueError("MYSQL_PORT debe ser un número entero.") from error

        return cls(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=port,
            user=os.getenv("MYSQL_USER", "root"),
            password=password,
            database=os.getenv("MYSQL_DATABASE", "login_registro"),
        )

    def _crear_tabla(self):
        consulta = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                usuario VARCHAR(255) NOT NULL,
                password_hash BINARY(32) NOT NULL,
                password_salt BINARY(16) NOT NULL,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                UNIQUE KEY uq_usuarios_usuario (usuario)
            ) ENGINE=InnoDB
              DEFAULT CHARACTER SET utf8mb4
              COLLATE utf8mb4_unicode_ci
        """
        with self._conexion.cursor() as cursor:
            cursor.execute(consulta)
        self._conexion.commit()

    def obtener_credenciales(self, usuario):
        consulta = """
            SELECT password_hash, password_salt
            FROM usuarios
            WHERE usuario = %s
        """
        try:
            with self._conexion.cursor(dictionary=True) as cursor:
                cursor.execute(consulta, (usuario,))
                return cursor.fetchone()
        except mysql.connector.Error as error:
            raise ErrorPersistencia(
                "No se pudo consultar la base de datos."
            ) from error

    def crear_usuario(self, nombre, apellido, usuario, password_hash, password_salt):
        consulta = """
            INSERT INTO usuarios
                (nombre, apellido, usuario, password_hash, password_salt)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with self._conexion.cursor() as cursor:
                cursor.execute(
                    consulta,
                    (nombre, apellido, usuario, password_hash, password_salt),
                )
            self._conexion.commit()
        except IntegrityError as error:
            self._conexion.rollback()
            if error.errno == ER_DUP_ENTRY:
                raise UsuarioDuplicadoError(
                    "Ese usuario ya está registrado."
                ) from error
            raise ErrorPersistencia(
                "No se pudo guardar el usuario en la base de datos."
            ) from error
        except mysql.connector.Error as error:
            self._conexion.rollback()
            raise ErrorPersistencia(
                "No se pudo guardar el usuario en la base de datos."
            ) from error

    def cerrar(self):
        self._conexion.close()
