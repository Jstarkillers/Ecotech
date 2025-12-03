# model/conexion.py
# Versión definitiva y funcional (sin errores de indentación)
import pymysql
from pymysql.cursors import DictCursor

class Conexion:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def conectar(self):
        """
        Cada llamada devuelve una conexión NUEVA y limpia.
        Soluciona el bug del cursor agotado después del primer intento fallido.
        """
        try:
            return pymysql.connect(
                host='localhost',
                user='poosuser',
                password='12345678',
                database='ecotech_solutions',
                port=8889,
                cursorclass=DictCursor,
                autocommit=True,
                charset='utf8mb4',
                connect_timeout=10
            )
        except Exception as e:
            print(f"\nError al conectar con la base de datos: {e}")
            return None
