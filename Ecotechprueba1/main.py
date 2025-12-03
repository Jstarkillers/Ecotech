# main.py - Versión corregida para estructura actual
import sys
import os
import traceback

def verificar_estructura():
    """Verifica que existan todas las carpetas y archivos necesarios"""
    # Según tu estructura: config, model (con inicializador), view, controller
    carpetas_necesarias = ['config', 'model', 'view', 'controller']
    
    # Archivos necesarios en cada carpeta
    archivos_necesarios = {
        'config': ['database.py'],
        'model': ['inicializador_bd.py', 'base_model.py', 'usuario.py'],
        'controller': ['auth_controller.py', 'menu_controller.py'],
        'view': ['menu_consola.py']
    }
    
    problemas = []
    
    print("🔍 Verificando estructura del sistema...")
    
    # Verificar carpetas
    for carpeta in carpetas_necesarias:
        if not os.path.exists(carpeta):
            problemas.append(f"Falta carpeta: {carpeta}/")
        elif not os.path.isdir(carpeta):
            problemas.append(f"{carpeta} no es una carpeta")
    
    # Verificar archivos clave
    for carpeta, archivos in archivos_necesarios.items():
        if os.path.exists(carpeta):
            for archivo in archivos:
                ruta = os.path.join(carpeta, archivo)
                if not os.path.exists(ruta):
                    problemas.append(f"Falta archivo: {ruta}")
                else:
                    print(f"  ✅ {ruta} encontrado")
    
    return problemas

def inicializar_sistema():
    """Función principal optimizada para tu estructura"""
    try:
        # Mostrar banner
        print("\n" + "═" * 60)
        print("       SISTEMA DE GESTIÓN - ECOTECH SOLUTIONS")
        print("═" * 60)
        
        # Verificar estructura primero
        problemas = verificar_estructura()
        if problemas:
            print("\n❌ Problemas de estructura encontrados:")
            for problema in problemas:
                print(f"   • {problema}")
            print("\n🔧 Por favor, asegúrate de que todos los archivos y carpetas existan.")
            print("\n📁 Estructura esperada:")
            print("   main.py")
            print("   config/")
            print("   ├── database.py")
            print("   model/")
            print("   ├── inicializador_bd.py")
            print("   ├── base_model.py")
            print("   ├── usuario.py")
            print("   controller/")
            print("   ├── auth_controller.py")
            print("   ├── menu_controller.py")
            print("   view/")
            print("   └── menu_consola.py")
            sys.exit(1)
        
        # 1. Inicializar base de datos completa
        print("\n🔄 Inicializando base de datos...")
        
        # Importar y ejecutar inicializador desde model/
        try:
            # El inicializador está en model/
            from model.inicializador_bd import InicializadorBDCompleto
            if not InicializadorBDCompleto.inicializar():
                print("\n❌ No se pudo inicializar la base de datos")
                print("🔧 Verifica que MySQL esté ejecutándose y las credenciales sean correctas")
                input("\nPresiona ENTER para salir...")
                sys.exit(1)
        except ImportError as e:
            print(f"❌ Error al importar inicializador: {e}")
            print("🔧 Asegúrate de que el archivo model/inicializador_bd.py existe")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error al ejecutar inicializador: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        # 2. Proceso de autenticación
        print("\n" + "═" * 60)
        print("       INICIANDO AUTENTICACIÓN")
        print("═" * 60)
        
        # Importar controlador de autenticación desde controller/
        try:
            from controller.auth_controller import AuthController
            auth = AuthController()
            usuario = auth.login()
            
            if not usuario:
                print("\n❌ Autenticación fallida")
                input("Presiona ENTER para salir...")
                sys.exit(1)
        except ImportError as e:
            print(f"❌ Error al importar auth_controller: {e}")
            print("🔧 Asegúrate de que controller/auth_controller.py existe")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        # 3. Iniciar sistema principal con menú interactivo
        try:
            from view.menu_consola import iniciar_sistema as iniciar_interfaz
            iniciar_interfaz(usuario)
        except ImportError as e:
            print(f"❌ Error al importar menú consola: {e}")
            print("🔧 Asegúrate de que view/menu_consola.py existe")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Sistema cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {type(e).__name__}")
        print(f"   Detalle: {e}")
        traceback.print_exc()
    finally:
        # Cerrar conexión si existe
        try:
            from config.database import DatabaseConnection
            DatabaseConnection.close_connection()
        except ImportError:
            pass
        print("\n✅ Sistema finalizado correctamente\n")

if __name__ == "__main__":
    # Agregar el directorio actual al path para importaciones
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    inicializar_sistema()