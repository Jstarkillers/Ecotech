# controller/menu_controller.py - VERSIÓN CORREGIDA
import os
import getpass
from datetime import datetime
from typing import Dict, Any
from model.empleado import Empleado
from model.departamento import Departamento
from model.proyecto import Proyecto
from model.registro_tiempo import RegistroTiempo
from model.usuario import Usuario
from controller.indicador_controller import IndicadorController


class MenuController:
    def __init__(self, usuario: Dict[str, Any]):
        self.usuario = usuario
        self.rol = usuario.get('rol', 'empleado')
        self.es_admin = self.rol == 'admin'
        self.es_recursos_humanos = self.rol == 'recursos_humanos'
        self.es_empleado = self.rol == 'empleado'
        self.usuario_id = usuario['id']

        # Instancias de modelos
        self.empleado_model = Empleado()
        self.departamento_model = Departamento()
        self.proyecto_model = Proyecto()
        self.registro_model = RegistroTiempo()
        self.usuario_model = Usuario()

    def limpiar(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def pausar(self, msg: str = "Presione ENTER para continuar...") -> None:
        input(f"\n{msg}")

    # ==================== MÉTODOS DE GESTIÓN DE EMPLEADOS ====================
    def menu_empleados(self) -> None:
        if self.es_empleado:
            print("❌ Acceso denegado. Solo administradores y recursos humanos pueden acceder.")
            self.pausar()
            return
            
        while True:
            self.limpiar()
            print(" GESTIÓN DE EMPLEADOS")
            print("═" * 50)
            print("1. Listar todos los empleados")
            print("2. Crear nuevo empleado")
            print("3. Buscar empleado")
            print("4. Actualizar empleado")
            print("5. Eliminar empleado")
            print("6. Asignar a departamento")
            print("0. Volver")
            print("─" * 50)
            op = input(" → ").strip()

            if op == "1":
                self.listar_empleados()
                self.pausar()
            elif op == "2":
                self.crear_empleado()
            elif op == "3":
                self.buscar_empleado()
            elif op == "4":
                self.actualizar_empleado()
            elif op == "5":
                self.eliminar_empleado()
            elif op == "6":
                self.asignar_departamento()
            elif op == "0":
                break
            else:
                print("❌ Opción inválida.")
                self.pausar()

    def listar_empleados(self):
        """Lista todos los empleados con manejo seguro de valores None"""
        empleados = self.empleado_model.listar()
        if not empleados:
            print("No hay empleados registrados.")
            return

        print(f"\n{'ID':<4} {'Nombre':<25} {'Email':<30} {'Departamento':<20}")
        print("─" * 90)
        
        for emp in empleados:
            # Manejo seguro de valores None usando get() y proporcionando valores por defecto
            emp_id = str(emp.get('id', 'N/A'))
            
            # Para nombre y email, asegurar que no sean None
            nombre = emp.get('nombre', 'Sin nombre')
            if nombre is None:
                nombre = 'Sin nombre'
            nombre = str(nombre)[:24]  # Limitar longitud
            
            email = emp.get('email', 'Sin email')
            if email is None:
                email = 'Sin email'
            email = str(email)[:29]  # Limitar longitud
            
            # Para departamento_nombre, usar valor por defecto
            dept_nombre = emp.get('departamento_nombre', 'Sin asignar')
            if dept_nombre is None:
                dept_nombre = 'Sin asignar'
            dept_nombre = str(dept_nombre)[:19]  # Limitar longitud
            
            # Imprimir con formato seguro
            print(f"{emp_id:<4} {nombre:<25} {email:<30} {dept_nombre:<20}")

    def crear_empleado(self):
        """Crea un nuevo empleado"""
        self.limpiar()
        print(" CREAR NUEVO EMPLEADO")
        print("═" * 55)

        # Nombre
        nombre = input("Nombre completo: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            self.pausar()
            return

        # Email
        email = input("Email: ").strip().lower()
        if not email or '@' not in email:
            print("❌ Email inválido")
            self.pausar()
            return

        # Fecha de contratación
        fecha_input = input("Fecha contratación (YYYY-MM-DD, ENTER = hoy): ").strip()
        fecha_contratacion = fecha_input or datetime.today().strftime("%Y-%m-%d")
        
        # Salario
        salario_input = input("Salario inicial: ").strip()
        try:
            salario = float(salario_input) if salario_input else 0.0
        except ValueError:
            print("❌ Salario inválido. Se establecerá en 0.")
            salario = 0.0

        # Datos opcionales
        direccion = input("Dirección (opcional): ").strip() or None
        telefono = input("Teléfono (opcional): ").strip() or None

        # Departamento (opcional)
        departamento_id = None
        departamentos = self.departamento_model.listar()
        if departamentos:
            print("\nDepartamentos disponibles:")
            for dept in departamentos:
                gerente = dept.get('gerente_nombre', 'Sin gerente') or 'Sin gerente'
                print(f"  {dept['id']}: {dept['nombre']} (Gerente: {gerente})")
            
            dept_input = input("\nID del departamento (ENTER para omitir): ").strip()
            if dept_input.isdigit():
                departamento_id = int(dept_input)

        # Crear empleado
        empleado_id = self.empleado_model.crear(
            nombre=nombre,
            email=email,
            fecha_contratacion=fecha_contratacion,
            salario=salario,
            direccion=direccion,
            telefono=telefono,
            departamento_id=departamento_id
        )

        if empleado_id:
            print(f"✅ Empleado creado exitosamente (ID: {empleado_id})")
        else:
            print("❌ Error al crear empleado")
        self.pausar()

    def buscar_empleado(self):
        """Busca un empleado por nombre o email con manejo seguro de valores None"""
        self.limpiar()
        print(" BUSCAR EMPLEADO")
        print("═" * 55)

        criterio = input("Buscar por (1) Nombre  (2) Email: ").strip()
        empleado = None

        if criterio == "1":
            nombre = input("Nombre a buscar: ").strip()
            if not nombre:
                print("❌ Debe ingresar un nombre")
                self.pausar()
                return
            empleado = self.empleado_model.buscar_por_nombre(nombre)
        elif criterio == "2":
            email = input("Email a buscar: ").strip().lower()
            if not email:
                print("❌ Debe ingresar un email")
                self.pausar()
                return
            empleado = self.empleado_model.buscar_por_email(email)
        else:
            print("❌ Opción inválida")
            self.pausar()
            return

        if empleado:
            print("\n" + "═" * 55)
            print(" EMPLEADO ENCONTRADO")
            print("═" * 55)
            
            # Usar get() con valores por defecto para todos los campos
            print(f"ID: {empleado.get('id', 'N/A')}")
            print(f"Nombre: {empleado.get('nombre', 'Sin nombre') or 'Sin nombre'}")
            print(f"Email: {empleado.get('email', 'Sin email') or 'Sin email'}")
            print(f"Departamento: {empleado.get('departamento_nombre', 'Sin asignar') or 'Sin asignar'}")
            print(f"Fecha contratación: {empleado.get('fecha_contratacion', 'No especificada') or 'No especificada'}")
            
            # Manejo seguro del salario
            salario = empleado.get('salario')
            if salario is not None:
                try:
                    print(f"Salario: ${float(salario):,.2f}")
                except (ValueError, TypeError):
                    print(f"Salario: $0.00")
            else:
                print(f"Salario: $0.00")
            
            if empleado.get('direccion'):
                print(f"Dirección: {empleado['direccion']}")
            if empleado.get('telefono'):
                print(f"Teléfono: {empleado['telefono']}")
            print("═" * 55)
        else:
            print("❌ Empleado no encontrado")
        self.pausar()

    def actualizar_empleado(self):
        """Actualiza los datos de un empleado"""
        self.limpiar()
        print(" ACTUALIZAR EMPLEADO")
        print("═" * 55)

        try:
            empleado_id = int(input("ID del empleado a actualizar: ").strip())
        except ValueError:
            print("❌ ID inválido")
            self.pausar()
            return

        # Buscar empleado actual
        empleado = self.empleado_model.buscar_por_id(empleado_id)
        if not empleado:
            print("❌ Empleado no encontrado")
            self.pausar()
            return

        print("\nDeje en blanco para mantener el valor actual\n")

        # Recoger nuevos valores
        campos = {}

        nuevo_nombre = input(f"Nuevo nombre ({empleado.get('nombre', 'Sin nombre')}): ").strip()
        if nuevo_nombre:
            campos['nombre'] = nuevo_nombre

        nuevo_email = input(f"Nuevo email ({empleado.get('email', 'Sin email')}): ").strip().lower()
        if nuevo_email:
            if '@' in nuevo_email:
                campos['email'] = nuevo_email
            else:
                print("⚠️  Email inválido, se mantendrá el actual.")

        # Manejo seguro del salario actual
        salario_actual = empleado.get('salario', 0)
        try:
            salario_actual_float = float(salario_actual) if salario_actual is not None else 0.0
        except (ValueError, TypeError):
            salario_actual_float = 0.0
            
        nuevo_salario = input(f"Nuevo salario (${salario_actual_float:,.2f}): ").strip()
        if nuevo_salario:
            try:
                campos['salario'] = float(nuevo_salario)
            except ValueError:
                print("⚠️  Salario inválido, se mantendrá el actual.")

        # Departamento
        departamentos = self.departamento_model.listar()
        if departamentos:
            print("\nDepartamentos disponibles:")
            for dept in departamentos:
                print(f"  {dept['id']}: {dept['nombre']}")
            print("  0: Quitar departamento")
            
            dept_actual = empleado.get('departamento_nombre', 'Sin asignar') or 'Sin asignar'
            dept_input = input(f"\nNuevo departamento (actual: {dept_actual}): ").strip()
            
            if dept_input == "0":
                campos['departamento_id'] = None
            elif dept_input.isdigit():
                campos['departamento_id'] = int(dept_input)

        if campos:
            if self.empleado_model.actualizar(empleado_id, **campos):
                print("✅ Empleado actualizado correctamente")
            else:
                print("❌ Error al actualizar empleado")
        else:
            print("ℹ️  No se realizaron cambios")
        self.pausar()

    def eliminar_empleado(self):
        """Elimina un empleado"""
        self.limpiar()
        print(" ELIMINAR EMPLEADO")
        print("═" * 55)

        try:
            empleado_id = int(input("ID del empleado a eliminar: ").strip())
        except ValueError:
            print("❌ ID inválido")
            self.pausar()
            return

        empleado = self.empleado_model.buscar_por_id(empleado_id)
        if not empleado:
            print("❌ Empleado no encontrado")
            self.pausar()
            return

        print(f"\nEmpleado a eliminar:")
        print(f"  Nombre: {empleado.get('nombre', 'Sin nombre')}")
        print(f"  Email: {empleado.get('email', 'Sin email')}")
        print(f"  Departamento: {empleado.get('departamento_nombre', 'Sin asignar')}")
        print("═" * 55)
        
        confirmacion = input("¿Está seguro de eliminar este empleado? (s/N): ").strip().lower()
        if confirmacion != 's':
            print("Operación cancelada")
            self.pausar()
            return

        if self.empleado_model.eliminar(empleado_id):
            print("✅ Empleado eliminado correctamente")
        else:
            print("❌ Error al eliminar empleado")
        self.pausar()

    def asignar_departamento(self):
        """Asigna un empleado a un departamento"""
        self.limpiar()
        print(" ASIGNAR EMPLEADO A DEPARTAMENTO")
        print("═" * 55)

        try:
            empleado_id = int(input("ID del empleado: ").strip())
        except ValueError:
            print("❌ ID de empleado inválido")
            self.pausar()
            return

        empleado = self.empleado_model.buscar_por_id(empleado_id)
        if not empleado:
            print("❌ Empleado no encontrado")
            self.pausar()
            return

        departamentos = self.departamento_model.listar()
        if not departamentos:
            print("❌ No hay departamentos registrados")
            self.pausar()
            return

        print("\nDepartamentos disponibles:")
        for dept in departamentos:
            print(f"  {dept['id']}: {dept['nombre']}")
        print("  0: Quitar departamento")

        dept_actual = empleado.get('departamento_nombre', 'Sin asignar') or 'Sin asignar'
        dept_input = input(f"\nID del departamento (actual: {dept_actual}): ").strip()
        
        if dept_input == "0":
            departamento_id = None
        elif dept_input.isdigit():
            departamento_id = int(dept_input)
        else:
            print("❌ Opción inválida")
            self.pausar()
            return

        if self.empleado_model.asignar_departamento(empleado_id, departamento_id):
            print("✅ Departamento asignado correctamente")
        else:
            print("❌ Error al asignar departamento")
        self.pausar()

    # ==================== MÉTODOS DE GESTIÓN DE DEPARTAMENTOS ====================
    def menu_departamentos(self) -> None:
        """Menú de gestión de departamentos"""
        if self.es_empleado:
            print("❌ Acceso denegado. Solo administradores y recursos humanos pueden acceder.")
            self.pausar()
            return
            
        while True:
            self.limpiar()
            print(" GESTIÓN DE DEPARTAMENTOS")
            print("═" * 50)
            print("1. Listar departamentos")
            print("2. Crear departamento")
            print("3. Asignar/Quitar gerente")
            print("4. Eliminar departamento")
            print("0. Volver")
            op = input(" → ").strip()

            if op == "1":
                self.listar_departamentos()
                self.pausar()
            elif op == "2":
                self.crear_departamento()
            elif op == "3":
                self.gestionar_gerente()
            elif op == "4":
                self.eliminar_departamento()
            elif op == "0":
                break
            else:
                print("❌ Opción inválida.")
                self.pausar()

    def listar_departamentos(self):
        """Lista todos los departamentos con manejo seguro de valores"""
        departamentos = self.departamento_model.listar()
        if not departamentos:
            print("No hay departamentos registrados.")
            return
            
        print(f"\n{'ID':<4} {'Nombre':<25} {'Gerente':<25} {'Empleados':<10}")
        print("─" * 70)
        for d in departamentos:
            gerente = d.get('gerente_nombre') or 'Sin asignar'
            empleados = d.get('total_empleados', 0) or 0
            print(f"{d['id']:<4} {d['nombre']:<25} {gerente:<25} {empleados:<10}")

    def crear_departamento(self):
        """Crea un nuevo departamento"""
        self.limpiar()
        print(" CREAR NUEVO DEPARTAMENTO")
        print("═" * 50)
        
        nombre = input("Nombre del departamento: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            self.pausar()
            return
        
        # Mostrar empleados para asignar como gerente
        empleados = self.empleado_model.listar()
        gerente_id = None
        
        if empleados:
            print("\nEmpleados disponibles para asignar como gerente:")
            for emp in empleados[:10]:
                print(f"  {emp['id']}: {emp.get('nombre', 'Sin nombre')}")
            
            gerente_input = input("\nID del gerente (ENTER para dejar vacío): ").strip()
            if gerente_input.isdigit():
                gerente_id = int(gerente_input)
        
        # Crear departamento
        dept_id = self.departamento_model.crear(nombre, gerente_id)
        if dept_id:
            print(f"✅ Departamento '{nombre}' creado con ID {dept_id}")
        else:
            print("❌ Error al crear departamento")
        self.pausar()

    def gestionar_gerente(self):
        """Asigna o quita un gerente de departamento"""
        self.limpiar()
        print(" ASIGNAR/QUITAR GERENTE DE DEPARTAMENTO")
        print("═" * 60)
        
        try:
            # Mostrar departamentos
            departamentos = self.departamento_model.listar()
            if not departamentos:
                print("No hay departamentos registrados.")
                self.pausar()
                return
                
            print("\nDepartamentos disponibles:")
            for d in departamentos:
                gerente = d.get('gerente_nombre') or 'Sin asignar'
                print(f"  {d['id']}: {d['nombre']} (Gerente actual: {gerente})")
            
            dept_id = int(input("\nID del departamento: ").strip())
            
            # Mostrar empleados disponibles
            empleados = self.empleado_model.listar()
            print("\nEmpleados disponibles:")
            for emp in empleados[:15]:
                print(f"  {emp['id']}: {emp.get('nombre', 'Sin nombre')}")
            
            gerente_input = input("\nID del nuevo gerente (0 para quitar gerente, ENTER para cancelar): ").strip()
            
            if gerente_input == "":
                print("Operación cancelada.")
            elif gerente_input == "0":
                # Quitar gerente
                if self.departamento_model.asignar_gerente(dept_id, None):
                    print("✅ Gerente removido del departamento")
                else:
                    print("❌ Error al remover gerente")
            elif gerente_input.isdigit():
                # Asignar nuevo gerente
                gerente_id = int(gerente_input)
                if self.departamento_model.asignar_gerente(dept_id, gerente_id):
                    print("✅ Gerente asignado correctamente")
                else:
                    print("❌ Error al asignar gerente")
                    
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    def eliminar_departamento(self):
        """Elimina un departamento"""
        self.limpiar()
        print(" ELIMINAR DEPARTAMENTO")
        print("═" * 50)
        
        try:
            # Mostrar departamentos
            departamentos = self.departamento_model.listar()
            if not departamentos:
                print("No hay departamentos registrados.")
                self.pausar()
                return
                
            print("\nDepartamentos disponibles:")
            for d in departamentos:
                empleados = d.get('total_empleados', 0) or 0
                print(f"  {d['id']}: {d['nombre']} ({empleados} empleados)")
            
            dept_id = int(input("\nID del departamento a eliminar: ").strip())
            
            # Confirmar
            confirm = input("¿Está seguro de eliminar este departamento? (s/N): ").strip().lower()
            if confirm != 's':
                print("Operación cancelada.")
                self.pausar()
                return
            
            # Eliminar
            if self.departamento_model.eliminar(dept_id):
                print("✅ Departamento eliminado correctamente")
            else:
                print("❌ Error al eliminar departamento")
                
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    # ==================== MÉTODOS DE GESTIÓN DE PROYECTOS ====================
    def menu_proyectos(self) -> None:
        """Menú de gestión de proyectos"""
        if self.es_empleado:
            print("❌ Acceso denegado. Solo administradores y recursos humanos pueden acceder.")
            self.pausar()
            return
            
        while True:
            self.limpiar()
            print(" GESTIÓN DE PROYECTOS")
            print("═" * 55)
            print("1. Listar proyectos")
            print("2. Crear proyecto")
            print("3. Asignar/Quitar empleado")
            print("4. Ver empleados en proyecto")
            print("5. Eliminar proyecto")
            print("0. Volver")
            print("═" * 55)
            op = input(" → ").strip()

            if op == "1":
                self.listar_proyectos()
                self.pausar()
            elif op == "2":
                self.crear_proyecto()
            elif op == "3":
                self.gestionar_asignacion_proyecto()
            elif op == "4":
                self.empleados_en_proyecto()
                self.pausar()
            elif op == "5":
                self.eliminar_proyecto()
            elif op == "0":
                break
            else:
                print("❌ Opción inválida.")
                self.pausar()

    def listar_proyectos(self):
        """Lista todos los proyectos con manejo seguro de valores"""
        proyectos = self.proyecto_model.listar(incluir_empleados=True)
        if not proyectos:
            print("No hay proyectos registrados.")
            return
            
        print(f"\n{'ID':<4} {'Nombre':<25} {'Estado':<12} {'Empleados':<15}")
        print("─" * 60)
        for p in proyectos:
            empleados = p.get('empleados_asignados') or 'Ninguno'
            if empleados is None:
                empleados = 'Ninguno'
            empleados = str(empleados)[:15]
            print(f"{p['id']:<4} {p['nombre']:<25} {p['estado']:<12} {empleados:<15}")

    def crear_proyecto(self):
        """Crea un nuevo proyecto"""
        self.limpiar()
        print(" CREAR NUEVO PROYECTO")
        print("═" * 50)
        
        nombre = input("Nombre del proyecto: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            self.pausar()
            return
        
        descripcion = input("Descripción (opcional): ").strip() or ""
        
        proyecto_id = self.proyecto_model.crear(nombre, descripcion)
        if proyecto_id:
            print(f"✅ Proyecto '{nombre}' creado con ID {proyecto_id}")
        else:
            print("❌ Error al crear proyecto")
        self.pausar()

    def gestionar_asignacion_proyecto(self):
        """Asigna o desasigna empleados de proyectos"""
        self.limpiar()
        print(" ASIGNAR/DESASIGNAR EMPLEADO DE PROYECTO")
        print("═" * 60)
        
        try:
            proyecto_id = int(input("ID del proyecto: ").strip())
            empleado_id = int(input("ID del empleado: ").strip())
            
            accion = input("Acción: (a)signar o (d)esasignar [a/d]: ").strip().lower()
            
            if accion == 'a':
                if self.proyecto_model.asignar_empleado(proyecto_id, empleado_id):
                    print("✅ Empleado asignado al proyecto")
                else:
                    print("❌ Error al asignar empleado")
            elif accion == 'd':
                if self.proyecto_model.desasignar_empleado(proyecto_id, empleado_id):
                    print("✅ Empleado desasignado del proyecto")
                else:
                    print("❌ Error al desasignar empleado")
            else:
                print("❌ Acción inválida")
                
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    def empleados_en_proyecto(self):
        """Muestra los empleados asignados a un proyecto"""
        self.limpiar()
        print(" EMPLEADOS EN PROYECTO")
        print("═" * 60)
        
        try:
            proyecto_id = int(input("ID del proyecto: ").strip())
            empleados = self.proyecto_model.empleados_en_proyecto(proyecto_id)
            
            if not empleados:
                print("No hay empleados asignados a este proyecto.")
                return
                
            print(f"\nEmpleados en el proyecto:")
            for emp in empleados:
                nombre = emp.get('nombre', 'Sin nombre') or 'Sin nombre'
                email = emp.get('email', 'Sin email') or 'Sin email'
                print(f"  • {nombre} ({email})")
                
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")

    def eliminar_proyecto(self):
        """Elimina un proyecto"""
        self.limpiar()
        print(" ELIMINAR PROYECTO")
        print("═" * 50)
        
        try:
            proyecto_id = int(input("ID del proyecto a eliminar: ").strip())
            
            # Confirmar
            confirm = input("¿Está seguro de eliminar este proyecto? (s/N): ").strip().lower()
            if confirm != 's':
                print("Operación cancelada.")
                self.pausar()
                return
            
            # Eliminar
            if self.proyecto_model.eliminar(proyecto_id):
                print("✅ Proyecto eliminado correctamente")
            else:
                print("❌ Error al eliminar proyecto")
                
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    # ==================== MÉTODOS DE REGISTRO DE HORAS ====================
    def menu_registro_horas(self) -> None:
        """Menú para registrar horas trabajadas"""
        self.limpiar()
        print(" REGISTRO DE HORAS TRABAJADAS")
        print("═" * 50)
        
        # Si es empleado, solo puede registrar sus propias horas
        if self.es_empleado:
            empleado_id = self.usuario_id
            print(f"Registrando horas para usted mismo (ID: {empleado_id})")
        else:
            try:
                empleado_id = int(input("ID del empleado (ENTER para usar su ID): ").strip() or self.usuario_id)
            except ValueError:
                print("❌ ID inválido. Usando su ID.")
                empleado_id = self.usuario_id
        
        try:
            proy_id = int(input("ID del proyecto: "))
            fecha = input("Fecha (YYYY-MM-DD, hoy por defecto): ") or datetime.today().strftime('%Y-%m-%d')
            horas = float(input("Horas trabajadas: "))
            desc = input("Descripción (opcional): ")
            
            if self.registro_model.registrar(empleado_id, proy_id, fecha, horas, desc):
                print("✅ Horas registradas con éxito.")
            else:
                print("❌ Error al registrar horas.")
        except ValueError:
            print("❌ Error: datos inválidos (ID o horas).")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    def menu_mis_horas(self) -> None:
        """Menú para ver las horas propias"""
        self.limpiar()
        print(f" MIS HORAS – {self.usuario['username'].upper()}")
        print("═" * 60)
        
        try:
            registros = self.registro_model.listar_por_empleado(self.usuario_id)
            if not registros:
                print("No tienes horas registradas.")
            else:
                print(f"{'Fecha':<12} {'Proyecto':<20} {'Horas':<6} Descripción")
                print("─" * 60)
                for r in registros[:20]:  # Mostrar solo los últimos 20
                    desc = (r.get('descripcion') or "")[:40]
                    print(f"{r['fecha']:<12} {r.get('proyecto_nombre', 'Sin nombre'):<20} {r['horas']:<6} {desc}")
                
                total = self.registro_model.total_horas_empleado(self.usuario_id)
                print(f"\n📊 TOTAL HORAS: {total:.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    # ==================== MÉTODOS DE REPORTES ====================
    def menu_reportes(self) -> None:
        """Menú de reportes y estadísticas"""
        while True:
            self.limpiar()
            print(" REPORTES Y ESTADÍSTICAS")
            print("═" * 70)
            
            # Opciones para todos los usuarios
            print("1. Top indicadores económicos consultados")
            print("2. Estadísticas generales del sistema")
            print("3. Últimos valores de indicadores económicos")
            
            # Opciones solo para admin y recursos humanos
            if not self.es_empleado:
                print("4. Reporte de horas por empleado")
                print("5. Reporte de horas por proyecto")
            
            print("0. Volver al menú principal")
            print("─" * 70)
            op = input(" Seleccione una opción → ").strip()

            if op == "1":
                self._reporte_top_indicadores()
            elif op == "2":
                self._reporte_estadisticas_generales()
            elif op == "3":
                self._reporte_ultimos_indicadores()
            elif op == "4" and not self.es_empleado:
                self._reporte_horas_empleados()
            elif op == "5" and not self.es_empleado:
                self._reporte_horas_proyectos()
            elif op == "0":
                break
            else:
                print("❌ Opción no válida. Intente nuevamente.")
                self.pausar()

    def _reporte_top_indicadores(self):
        """Muestra el top de indicadores económicos consultados"""
        self.limpiar()
        print(" TOP 10 INDICADORES MÁS CONSULTADOS")
        print("═" * 70)
        try:
            # Importar solo cuando sea necesario
            from model.consulta_indicador import ConsultaIndicador
            top = ConsultaIndicador().top_indicadores_global(10)
            if not top:
                print("Aún no se han realizado consultas de indicadores.")
            else:
                for i, t in enumerate(top, 1):
                    nombre = t.get('indicador', 'Desconocido').upper()
                    consultas = t.get('consultas', 0)
                    print(f" {i:2}. {nombre:<40} → {consultas:>4} consultas")
        except Exception as e:
            print(f"❌ Error al cargar top de indicadores: {e}")
        self.pausar()

    def _reporte_estadisticas_generales(self):
        """Muestra estadísticas generales del sistema"""
        self.limpiar()
        print(" ESTADÍSTICAS GENERALES DEL SISTEMA")
        print("═" * 80)

        try:
            stats = self.registro_model.estadisticas_globales()
            print("\n REGISTRO DE HORAS Y PRODUCTIVIDAD")
            print("─" * 80)
            print(f"{'Total de horas registradas':<45}: {stats.get('total_horas_registradas', 0):>10,.2f} h")
            print(f"{'Empleados activos con registros':<45}: {stats.get('empleados_con_horas', 0):>10}")
            print(f"{'Proyectos con horas asignadas':<45}: {stats.get('proyectos_activos', 0):>10}")
            if stats.get('empleados_con_horas', 0) > 0:
                print(f"{'Promedio de horas por empleado':<45}: {stats.get('promedio_horas_por_empleado', 0):>10,.2f} h")
            print(f"{'Primer registro de horas':<45}: {stats.get('fecha_primer_registro', 'Nunca'):>15}")
            print(f"{'Último registro de horas':<45}: {stats.get('fecha_ultimo_registro', 'Nunca'):>15}")
        except Exception as e:
            print(f"❌ Error al cargar estadísticas: {e}")
        self.pausar()

    def _reporte_ultimos_indicadores(self):
        """Muestra los últimos valores de indicadores económicos"""
        self.limpiar()
        print(" ÚLTIMOS VALORES DE INDICADORES ECONÓMICOS")
        print("═" * 80)
        try:
            from model.indicador_economico import IndicadorEconomico
            ultimos = IndicadorEconomico().listar_todos_ultimos()
            if not ultimos:
                print("No hay datos de indicadores económicos aún.")
            else:
                print(f"{'Indicador':<40} {'Fecha':<12} {'Valor':>15}")
                print("─" * 80)
                for u in ultimos:
                    valor = u.get('valor', 0)
                    nombre = u.get('nombre', 'Desconocido')
                    fecha = u.get('fecha', 'Desconocida')
                    print(f" {nombre:<40} {fecha:<12} ${valor:>14,.4f}")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    def _reporte_horas_empleados(self):
        """Reporte de horas por empleado con manejo seguro de valores"""
        self.limpiar()
        print(" REPORTE DE HORAS POR EMPLEADO")
        print("═" * 80)
        
        try:
            empleados = self.empleado_model.listar()
            if not empleados:
                print("No hay empleados registrados.")
            else:
                print(f"{'ID':<5} {'Nombre':<25} {'Total Horas':<12} {'Promedio/Día':<12}")
                print("─" * 80)
                for emp in empleados:
                    total = self.registro_model.total_horas_empleado(emp['id'])
                    # Calcular promedio (asumiendo 20 días laborales al mes)
                    promedio = total / 20 if total > 0 else 0
                    nombre = emp.get('nombre', 'Sin nombre') or 'Sin nombre'
                    print(f"{emp['id']:<5} {nombre[:24]:<25} {total:<12.2f} {promedio:<12.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    def _reporte_horas_proyectos(self):
        """Reporte de horas por proyecto con manejo seguro de valores"""
        self.limpiar()
        print(" REPORTE DE HORAS POR PROYECTO")
        print("═" * 80)
        
        try:
            proyectos = self.proyecto_model.listar(incluir_empleados=False)
            if not proyectos:
                print("No hay proyectos registrados.")
            else:
                print(f"{'ID':<5} {'Proyecto':<30} {'Estado':<12} {'Total Horas':<12}")
                print("─" * 80)
                for proy in proyectos:
                    # Obtener total de horas para este proyecto
                    query = "SELECT COALESCE(SUM(horas), 0) AS total FROM registro_tiempo WHERE proyecto_id = %s"
                    from model.base_model import BaseModel
                    base = BaseModel()
                    resultado = base.ejecutar(query, (proy['id'],), fetch_one=True)
                    total_horas = resultado.get('total', 0) if resultado else 0
                    
                    nombre = proy.get('nombre', 'Sin nombre') or 'Sin nombre'
                    estado = proy.get('estado', 'Desconocido') or 'Desconocido'
                    
                    print(f"{proy['id']:<5} {nombre[:29]:<30} {estado:<12} {total_horas:<12.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    # ==================== MÉTODOS DE GESTIÓN DE USUARIOS ====================
    def gestion_usuarios(self):
        """Gestión de usuarios (solo para admin)"""
        if not self.es_admin:
            print("❌ Acceso denegado. Solo administradores pueden acceder.")
            self.pausar()
            return
            
        while True:
            self.limpiar()
            print(" GESTIÓN DE USUARIOS - ADMINISTRADOR")
            print("═" * 55)
            print("1. Listar todos los usuarios")
            print("2. Crear nuevo usuario")
            print("3. Cambiar rol de usuario")
            print("4. Eliminar usuario")
            print("0. Volver")
            print("─" * 55)
            
            opcion = input("Seleccione opción → ").strip()
            
            if opcion == "1":
                self._listar_usuarios_admin()
            elif opcion == "2":
                self._crear_usuario_admin()
            elif opcion == "3":
                self._cambiar_rol_usuario()
            elif opcion == "4":
                self._eliminar_usuario_admin()
            elif opcion == "0":
                break
            else:
                print("❌ Opción no válida.")
            self.pausar()

    def _listar_usuarios_admin(self):
        """Lista todos los usuarios para administradores"""
        usuarios = self.usuario_model.listar_todos()
        if usuarios:
            print(f"\n{'ID':<5} {'Usuario':<15} {'Rol':<15}")
            print("─" * 40)
            for u in usuarios:
                rol_display = {
                    'admin': '👑 Administrador',
                    'recursos_humanos': '👔 Recursos Humanos',
                    'empleado': '👤 Empleado'
                }.get(u.get('rol', 'empleado'), u.get('rol', 'empleado'))
                username = u.get('username', 'Sin nombre')
                print(f"{u.get('id', 'N/A'):<5} {username:<15} {rol_display:<15}")
        else:
            print("No hay usuarios registrados.")

    def _crear_usuario_admin(self):
        """Crea un nuevo usuario desde el panel de admin"""
        self.limpiar()
        print(" CREAR NUEVO USUARIO")
        print("═" * 45)
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("❌ El nombre de usuario es obligatorio")
            self.pausar()
            return
        
        password = getpass.getpass("Contraseña: ").strip()
        if not password:
            print("❌ La contraseña es obligatoria")
            self.pausar()
            return
        
        confirm_password = getpass.getpass("Confirmar contraseña: ").strip()
        if password != confirm_password:
            print("❌ Las contraseñas no coinciden")
            self.pausar()
            return
        
        if len(password) < 4:
            print("❌ La contraseña debe tener al menos 4 caracteres")
            self.pausar()
            return
        
        print("\nRoles disponibles:")
        print("  1. 👑 Administrador")
        print("  2. 👔 Recursos Humanos")
        print("  3. 👤 Empleado")
        
        rol_opcion = input("\nSeleccione rol (1-3): ").strip()
        roles = {
            '1': 'admin',
            '2': 'recursos_humanos',
            '3': 'empleado'
        }
        
        rol = roles.get(rol_opcion, 'empleado')
        
        # Crear usuario
        usuario_id = self.usuario_model.crear(username, password, rol)
        if usuario_id:
            print(f"✅ Usuario '{username}' creado con rol '{rol}' (ID: {usuario_id})")
        else:
            print("❌ Error al crear usuario")
        self.pausar()

    def _cambiar_rol_usuario(self):
        """Cambia el rol de un usuario"""
        self.limpiar()
        print(" CAMBIAR ROL DE USUARIO")
        print("═" * 45)
        
        try:
            # Listar usuarios
            usuarios = self.usuario_model.listar_todos()
            if not usuarios:
                print("No hay usuarios registrados.")
                self.pausar()
                return
                
            print("\nUsuarios disponibles:")
            for u in usuarios:
                print(f"  {u.get('id', 'N/A')}: {u.get('username', 'Sin nombre')} (rol actual: {u.get('rol', 'empleado')})")
            
            usuario_id = int(input("\nID del usuario: ").strip())
            
            print("\nNuevos roles disponibles:")
            print("  1. 👑 Administrador")
            print("  2. 👔 Recursos Humanos")
            print("  3. 👤 Empleado")
            
            nuevo_rol_opcion = input("\nSeleccione nuevo rol (1-3): ").strip()
            roles_map = {
                '1': 'admin',
                '2': 'recursos_humanos',
                '3': 'empleado'
            }
            
            nuevo_rol = roles_map.get(nuevo_rol_opcion)
            if not nuevo_rol:
                print("❌ Rol inválido")
                self.pausar()
                return
            
            # Cambiar rol
            if self.usuario_model.cambiar_rol(usuario_id, nuevo_rol):
                print(f"✅ Rol cambiado a '{nuevo_rol}'")
            else:
                print("❌ Error al cambiar rol")
                
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    def _eliminar_usuario_admin(self):
        """Elimina un usuario desde el panel de admin"""
        self.limpiar()
        print(" ELIMINAR USUARIO")
        print("═" * 45)
        
        try:
            # Listar usuarios (excepto admin)
            usuarios = self.usuario_model.listar_todos()
            if not usuarios:
                print("No hay usuarios registrados.")
                self.pausar()
                return
                
            print("\nUsuarios disponibles:")
            for u in usuarios:
                if u.get('username') != 'admin':  # No mostrar admin para eliminar
                    print(f"  {u.get('id', 'N/A')}: {u.get('username', 'Sin nombre')} (rol: {u.get('rol', 'empleado')})")
            
            usuario_id = int(input("\nID del usuario a eliminar: ").strip())
            
            # Verificar que no sea admin
            for u in usuarios:
                if u.get('id') == usuario_id and u.get('username') == 'admin':
                    print("❌ No se puede eliminar el usuario administrador principal")
                    self.pausar()
                    return
            
            # Confirmar
            confirm = input("¿Está seguro de eliminar este usuario? (s/N): ").strip().lower()
            if confirm != 's':
                print("Operación cancelada.")
                self.pausar()
                return
            
            # Eliminar
            if self.usuario_model.eliminar(usuario_id):
                print("✅ Usuario eliminado correctamente")
            else:
                print("❌ Error al eliminar usuario")
                
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.pausar()

    # ==================== CAMBIAR CONTRASEÑA ====================
    def cambiar_contraseña(self) -> None:
        """Cambia la contraseña del usuario actual"""
        self.limpiar()
        print(" CAMBIAR CONTRASEÑA")
        print("═" * 40)
        
        actual = getpass.getpass("Contraseña actual: ")
        if not self.usuario_model.autenticar(self.usuario['username'], actual):
            print("❌ Contraseña incorrecta.")
            self.pausar()
            return
        
        nueva = getpass.getpass("Nueva contraseña: ")
        confirmar = getpass.getpass("Confirmar: ")
        
        if nueva != confirmar:
            print("❌ Las contraseñas no coinciden.")
        elif len(nueva) < 4:
            print("❌ Mínimo 4 caracteres.")
        elif self.usuario_model.cambiar_contraseña(self.usuario['id'], nueva):
            print("✅ Contraseña cambiada con éxito.")
        else:
            print("❌ Error al cambiar contraseña.")
        self.pausar()