# config/database.py - Mantener igual pero asegurar configuración correcta
import pymysql
from pymysql.cursors import DictCursor
import threading

class DatabaseConnection:
    _config = {
        'host': 'localhost',
        'user': 'poosuser',  # Cambiar según tu configuración
        'password': '12345678',
        'port': 8889,  # Cambiar a 3306 si es XAMPP/MAMP estándar
        'database': 'ecotech_solutions',
        'cursorclass': DictCursor,
        'autocommit': True,
        'charset': 'utf8mb4',
        'connect_timeout': 5
    }
    
    _local = threading.local()
    
    @classmethod
    def get_connection(cls):
        """Obtiene conexión para el thread actual"""
        try:
            if not hasattr(cls._local, 'connection') or not cls._local.connection.open:
                cls._local.connection = pymysql.connect(**cls._config)
            return cls._local.connection
        except pymysql.err.OperationalError as e:
            print(f"❌ Error de conexión MySQL: {e}")
            
            # Intentar puerto alternativo
            if cls._config['port'] == 8889:
                print("🔄 Intentando con puerto 3306...")
                cls._config['port'] = 3306
                try:
                    cls._local.connection = pymysql.connect(**cls._config)
                    print("✅ Conexión exitosa con puerto 3306")
                    return cls._local.connection
                except:
                    pass
            
            print("\n🔧 CONFIGURACIÓN ACTUAL:")
            print(f"   Host: {cls._config['host']}")
            print(f"   Usuario: {cls._config['user']}")
            print(f"   Puerto: {cls._config['port']}")
            print(f"   Base de datos: {cls._config['database']}")
            
            raise ConnectionError(f"No se pudo conectar a MySQL. Verifica la configuración.")
    
    @classmethod
    def close_connection(cls):
        """Cierra conexión del thread actual"""
        if hasattr(cls._local, 'connection') and cls._local.connection.open:
            cls._local.connection.close()
            delattr(cls._local, 'connection')
    
    @classmethod
    def probar_conexion_simple(cls):
        """Prueba de conexión sin base de datos específica"""
        try:
            config_temp = cls._config.copy()
            config_temp.pop('database', None)
            conn = pymysql.connect(**config_temp)
            conn.close()
            return True
        except:
            return False