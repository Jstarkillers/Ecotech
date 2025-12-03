# view/menu_consola.py
import os
from typing import Dict
from controller.menu_controller import MenuController
from controller.indicador_controller import IndicadorController


class MenuConsola:
    """
    Vista principal del sistema – Experiencia de usuario.
    Limpieza de pantalla, diseño, control de acceso y feedback claro.
    """

    # Colores ANSI (opcional – se ven increíbles si la terminal lo soporta)
    class Colores:
        VERDE = "\033[92m"
        AMARILLO = "\033[93m"
        ROJO = "\033[91m"
        CYAN = "\033[96m"
        BLANCO = "\033[97m"
        RESET = "\033[0m"
        NEGRITA = "\033[1m"

    def __init__(self, usuario: Dict):
        self.usuario = usuario
        self.rol = usuario.get('rol', 'empleado')
        self.es_admin = self.rol == 'admin'
        self.es_recursos_humanos = self.rol == 'recursos_humanos'
        self.es_empleado = self.rol == 'empleado'
        
        # Crear controlador pasando el usuario
        self.controller = MenuController(usuario)

    def limpiar(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def pausar(self, mensaje: str = "Presione ENTER para continuar..."):
        input(f"\n{self.Colores.AMARILLO}{mensaje}{self.Colores.RESET}")

    def titulo(self):
        self.limpiar()
        print(self.Colores.CYAN + "═" * 55)
        print(" SISTEMA DE GESTIÓN DE EMPLEADOS – ECOTECH SOLUTIONS")
        print("   Tecnologías Sostenibles & Seguridad Informática")
        print("═" * 55 + self.Colores.RESET)

        # Definir color según rol
        if self.es_admin:
            rol_color = self.Colores.ROJO
            rol_texto = "ADMINISTRADOR"
        elif self.es_recursos_humanos:
            rol_color = self.Colores.VERDE
            rol_texto = "RECURSOS HUMANOS"
        else:
            rol_color = self.Colores.AMARILLO
            rol_texto = "EMPLEADO"
            
        print(f"{self.Colores.BLANCO}Usuario:{self.Colores.RESET} {self.usuario['username'].upper():<8} "
              f"{self.Colores.BLANCO}Rol:{self.Colores.RESET} {rol_color}{rol_texto:<18}{self.Colores.RESET}")
        print(self.Colores.CYAN + "═" * 55 + self.Colores.RESET)

    def menu_principal(self):
        while True:
            self.titulo()
            
            # Mostrar menú según rol
            if self.es_admin:
                self._menu_admin()
            elif self.es_recursos_humanos:
                self._menu_recursos_humanos()
            else:  # empleado
                self._menu_empleado()
            
            opcion = input(f"\n{self.Colores.VERDE}Seleccione una opción → {self.Colores.RESET}").strip()

            # Mapeo de opciones según rol
            if self.es_admin:
                acciones = {
                    "1": self.controller.menu_empleados,
                    "2": self.controller.menu_departamentos,
                    "3": self.controller.menu_proyectos,
                    "4": self.controller.menu_registro_horas,
                    "5": lambda: IndicadorController.consultar(self.usuario['id']),
                    "6": self.controller.menu_mis_horas,
                    "7": self.controller.menu_reportes,
                    "8": self.controller.cambiar_contraseña,
                    "9": self.controller.gestion_usuarios,
                    "0": self.cerrar_sesion
                }
            elif self.es_recursos_humanos:
                acciones = {
                    "1": self.controller.menu_empleados,
                    "2": self.controller.menu_departamentos,
                    "3": self.controller.menu_proyectos,
                    "4": self.controller.menu_registro_horas,
                    "5": lambda: IndicadorController.consultar(self.usuario['id']),
                    "6": self.controller.menu_mis_horas,
                    "7": self.controller.menu_reportes,
                    "8": self.controller.cambiar_contraseña,
                    "0": self.cerrar_sesion
                }
            else:  # empleado
                acciones = {
                    "1": lambda: IndicadorController.consultar(self.usuario['id']),
                    "2": self.controller.menu_registro_horas,
                    "3": self.controller.menu_mis_horas,
                    "4": self.controller.menu_reportes,
                    "5": self.controller.cambiar_contraseña,
                    "0": self.cerrar_sesion
                }

            if opcion in acciones:
                acciones[opcion]()
                if opcion == "0":
                    break
            else:
                self.mostrar_error("Opción no válida. Intente nuevamente.")
                self.pausar()

    def _menu_admin(self):
        """Menú para administrador"""
        print(f"\n{self.Colores.NEGRITA} MENÚ PRINCIPAL - ADMINISTRADOR{self.Colores.RESET}")
        print(" ┌─────────────────────────────────────────────────────────────────┐")
        print(" │ 1. Gestionar Empleados           │ 6. Mis Horas Registradas     │")
        print(" │ 2. Gestionar Departamentos       │ 7. Reportes Generales        │")
        print(" │ 3. Gestionar Proyectos           │ 8. Cambiar Contraseña        │")
        print(" │ 4. Registrar Horas Trabajadas    │ 9. Gestionar Usuarios        │")
        print(" │ 5. Indicadores Económicos        │ 0. Cerrar Sesión             │")
        print(" └─────────────────────────────────────────────────────────────────┘")

    def _menu_recursos_humanos(self):
        """Menú para recursos humanos"""
        print(f"\n{self.Colores.NEGRITA} MENÚ PRINCIPAL - RECURSOS HUMANOS{self.Colores.RESET}")
        print(" ┌─────────────────────────────────────────────────────────────────┐")
        print(" │ 1. Gestionar Empleados           │ 5. Indicadores Económicos    │")
        print(" │ 2. Gestionar Departamentos       │ 6. Mis Horas Registradas     │")
        print(" │ 3. Gestionar Proyectos           │ 7. Reportes Generales        │")
        print(" │ 4. Registrar Horas Trabajadas    │ 8. Cambiar Contraseña        │")
        print(" │                                  │ 0. Cerrar Sesión             │")
        print(" └─────────────────────────────────────────────────────────────────┘")

    def _menu_empleado(self):
        """Menú para empleado"""
        print(f"\n{self.Colores.NEGRITA} MENÚ PRINCIPAL - EMPLEADO{self.Colores.RESET}")
        print(" ┌─────────────────────────────────────────────────────────────────┐")
        print(" │ 1. Indicadores Económicos        │ 4. Reportes Generales        │")
        print(" │ 2. Registrar Horas Trabajadas    │ 5. Cambiar Contraseña        │")
        print(" │ 3. Mis Horas Registradas         │ 0. Cerrar Sesión             │")
        print(" └─────────────────────────────────────────────────────────────────┘")

    def mostrar_error(self, mensaje: str):
        print(f"\n{self.Colores.ROJO}Error: {mensaje}{self.Colores.RESET}")

    def mostrar_exito(self, mensaje: str):
        print(f"\n{self.Colores.VERDE}Éxito: {mensaje}{self.Colores.RESET}")

    def cerrar_sesion(self):
        self.limpiar()
        print(f"\n{self.Colores.CYAN}Gracias por usar EcoTech Solutions, {self.usuario['username'].upper()}.{self.Colores.RESET}")
        print(f"{self.Colores.AMARILLO}Sesión cerrada de forma segura.{self.Colores.RESET}")
        print(f"{self.Colores.CYAN}¡Hasta pronto!{self.Colores.RESET}")

# === FUNCIÓN GLOBAL PARA INICIAR EL SISTEMA ===
def iniciar_sistema(usuario: Dict):
    """
    Inicia la interfaz gráfica por consola con el usuario autenticado.
    """
    MenuConsola(usuario).menu_principal()