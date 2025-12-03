# controller/auth_controller.py - Simplificado
import getpass
import time
from typing import Optional, Dict
from model.usuario import Usuario

class AuthController:
    MAX_INTENTOS = 3
    RETRASO_BASE = 1

    def __init__(self):
        self.usuario_model = Usuario()

    def login(self) -> Optional[Dict]:
        """Proceso de login optimizado"""
        print("🔐 AUTENTICACIÓN SEGURA")
        print("═" * 55)
        print("\n📋 Usuarios disponibles:")
        print("  • admin / admin123       (👑 Administrador)")
        print("  • rrhh / rrhh123         (👔 Recursos Humanos)")
        print("  • empleado1 / empleado123 (👤 Empleado)")
        print("═" * 55)

        intentos = 0
        while intentos < self.MAX_INTENTOS:
            try:
                print(f"\nIntento {intentos + 1}/{self.MAX_INTENTOS}")
                username = input("Usuario: ").strip()
                password = getpass.getpass("Contraseña: ")

                if not username or not password:
                    print("¡Error! Campos vacíos.")
                    intentos += 1
                    continue

                usuario = self.usuario_model.autenticar(username, password)
                if usuario:
                    rol_display = {
                        'admin': '👑 ADMINISTRADOR',
                        'recursos_humanos': '👔 RECURSOS HUMANOS',
                        'empleado': '👤 EMPLEADO'
                    }.get(usuario['rol'], usuario['rol'].upper())
                    
                    print(f"\n✅ ACCESO CONCEDIDO: {usuario['username'].upper()} ({rol_display})")
                    time.sleep(1)
                    return usuario

                intentos += 1
                restantes = self.MAX_INTENTOS - intentos
                print(f"✗ Credenciales incorrectas. Intentos restantes: {restantes}")

                if restantes > 0:
                    retraso = self.RETRASO_BASE * (2 ** (intentos - 1))
                    print(f"⏳ Esperando {retraso} segundos...")
                    time.sleep(retraso)

            except KeyboardInterrupt:
                print("\n\n⚠️  Autenticación cancelada por el usuario")
                return None
            except Exception as e:
                print(f"Error inesperado: {e}")
                intentos += 1

        print("\n🚫 Límite de intentos superado")
        print("⚠️  El sistema se cerrará por seguridad")
        return None