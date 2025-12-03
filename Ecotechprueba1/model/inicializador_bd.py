# model/inicializador_bd.py
"""
INICIALIZADOR DE BASE DE DATOS
Ubicado en model/ según tu estructura
"""
import pymysql
import bcrypt

class InicializadorBDCompleto:
    """Clase unificada para creación de BD, tablas y usuarios por defecto"""
    
    @staticmethod
    def inicializar():
        """
        Método principal que ejecuta toda la inicialización
        Devuelve: True si éxito, False si error
        """
        print("\n" + "═" * 50)
        print("   INICIALIZACIÓN DE BASE DE DATOS")
        print("═" * 50)
        
        try:
            # Configuración de conexión - AJUSTA ESTOS VALORES
            config = {
                'host': 'localhost',
                'user': 'poosuser',      # Cambia según tu MySQL
                'password': '12345678',   # Cambia según tu MySQL
                'port': 8889,            # 3306 para XAMPP, 8889 para MAMP
                'charset': 'utf8mb4'
            }
            
            db_name = 'ecotech_solutions'
            
            print("🔌 Conectando a MySQL...")
            # 1. Conectar a MySQL (sin especificar base de datos)
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            
            # 2. Crear base de datos si no existe
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {db_name}")
            print(f"✅ Base de datos '{db_name}' lista")
            
            # 3. Crear todas las tablas
            print("\n📋 Creando tablas...")
            tablas_sql = InicializadorBDCompleto._obtener_sql_tablas()
            
            for tabla, sql in tablas_sql.items():
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
                    cursor.execute(sql)
                    print(f"   ✅ {tabla}")
                except Exception as e:
                    print(f"   ⚠️  {tabla}: {str(e)[:50]}")
            
            # 4. Insertar usuarios por defecto
            print("\n👥 Creando usuarios por defecto...")
            usuarios = [
                ("admin", "admin123", "admin"),
                ("rrhh", "rrhh123", "recursos_humanos"),
                ("empleado1", "empleado123", "empleado")
            ]
            
            for username, password, rol in usuarios:
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                cursor.execute("""
                    INSERT IGNORE INTO usuario (username, password_hash, rol)
                    VALUES (%s, %s, %s)
                """, (username, password_hash, rol))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("\n✅ INICIALIZACIÓN COMPLETADA")
            print("\n📋 CREDENCIALES:")
            print("   admin / admin123")
            print("   rrhh / rrhh123")
            print("   empleado1 / empleado123")
            print("═" * 50)
            
            return True
            
        except pymysql.err.OperationalError as e:
            print(f"\n❌ ERROR DE CONEXIÓN: {e}")
            print("\n🔧 SOLUCIONES:")
            print("   1. Verifica que MySQL esté ejecutándose")
            print("   2. Ajusta las credenciales en model/inicializador_bd.py")
            print("   3. Si usas XAMPP, prueba con: user='root', password='', port=3306")
            print("   4. Si usas MAMP, prueba con: user='root', password='root', port=8889")
            return False
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            traceback.print_exc()
            return False
    
    @staticmethod
    def _obtener_sql_tablas():
        """Retorna el SQL para crear todas las tablas"""
        return {
            'usuario': """
                CREATE TABLE usuario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    rol VARCHAR(20) NOT NULL DEFAULT 'empleado',
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'departamento': """
                CREATE TABLE departamento (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    gerente_id INT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'empleado': """
                CREATE TABLE empleado (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    direccion VARCHAR(200),
                    telefono VARCHAR(20),
                    email VARCHAR(100) NOT NULL,
                    fecha_contratacion DATE NOT NULL,
                    salario DECIMAL(10, 2) DEFAULT 0,
                    departamento_id INT,
                    usuario_id INT,
                    FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON DELETE SET NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'proyecto': """
                CREATE TABLE proyecto (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    fecha_inicio DATE NOT NULL,
                    estado VARCHAR(20) DEFAULT 'activo'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'asignacion_proyecto': """
                CREATE TABLE asignacion_proyecto (
                    empleado_id INT,
                    proyecto_id INT,
                    PRIMARY KEY (empleado_id, proyecto_id),
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE,
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'registro_tiempo': """
                CREATE TABLE registro_tiempo (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    empleado_id INT NOT NULL,
                    proyecto_id INT NOT NULL,
                    fecha DATE NOT NULL,
                    horas DECIMAL(5,2) NOT NULL,
                    descripcion TEXT,
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE,
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'indicador_economico': """
                CREATE TABLE indicador_economico (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(20) NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    fecha DATE NOT NULL,
                    valor DECIMAL(20, 4) NOT NULL,
                    fuente VARCHAR(200) DEFAULT 'https://mindicador.cl',
                    registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unq_codigo_fecha (codigo, fecha)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'consulta_indicador': """
                CREATE TABLE consulta_indicador (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    indicador_codigo VARCHAR(20) NOT NULL,
                    fecha_indicador DATE NOT NULL,
                    valor DECIMAL(20, 4) NOT NULL,
                    guardado BOOLEAN DEFAULT 0,
                    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        }

# Si se ejecuta directamente
if __name__ == "__main__":
    import traceback
    if InicializadorBDCompleto.inicializar():
        print("\n✅ Base de datos lista. Ejecuta 'python main.py' para iniciar.")
    else:
        print("\n❌ La inicialización falló")