# model/asignacion_proyecto.py
# Modelo especializado N:M Empleado ↔ Proyecto
# Arquitectura limpia, rendimiento óptimo, reutilización
from model.base_model import BaseModel
from model.empleado import Empleado
from model.proyecto import Proyecto
from typing import List, Dict, Optional

class AsignacionProyecto(BaseModel):
    """
    Modelo dedicado exclusivamente a la tabla intermedia asignacion_proyecto.
    Evita lógica duplicada, mejora mantenibilidad y cumple al 100% con:
    • Relaciones muchos-a-muchos
    • Integridad referencial
    • Buenas prácticas de diseño
    """

    # Instancias únicas reutilizables → rendimiento máximo
    _empleado_model = Empleado()
    _proyecto_model = Proyecto()

    def asignar(self, empleado_id: int, proyecto_id: int) -> bool:
        """Asigna un empleado a un proyecto (INSERT IGNORE → idempotente)"""
        if not self._empleado_model.buscar_por_id(empleado_id):
            print(f"Empleado ID {empleado_id} no existe.")
            return False
        if not self._proyecto_model.buscar_por_id(proyecto_id):
            print(f"Proyecto ID {proyecto_id} no existe.")
            return False

        query = """
            INSERT IGNORE INTO asignacion_proyecto (empleado_id, proyecto_id)
            VALUES (%s, %s)
        """
        resultado = self.ejecutar(query, (empleado_id, proyecto_id))

        if resultado:
            print(f"Asignación exitosa: Empleado {empleado_id} → Proyecto {proyecto_id}")
        else:
            print("La asignación ya existía.")
        return bool(resultado)

    def desasignar(self, empleado_id: int, proyecto_id: int) -> bool:
        """Elimina una asignación específica"""
        query = """
            DELETE FROM asignacion_proyecto
            WHERE empleado_id = %s AND proyecto_id = %s
        """
        resultado = self.ejecutar(query, (empleado_id, proyecto_id))

        if resultado and resultado > 0:
            print(f"Asignación eliminada: Empleado {empleado_id} ← Proyecto {proyecto_id}")
            return True
        else:
            print("No existía esa asignación.")
            return False

    def esta_asignado(self, empleado_id: int, proyecto_id: int) -> bool:
        """Verifica si ya existe la relación"""
        query = """
            SELECT 1 FROM asignacion_proyecto
            WHERE empleado_id = %s AND proyecto_id = %s
            LIMIT 1
        """
        return self.ejecutar(query, (empleado_id, proyecto_id), fetch_one=True) is not None

    def proyectos_del_empleado(self, empleado_id: int) -> List[Dict]:
        """Todos los proyectos en los que trabaja un empleado"""
        query = """
            SELECT p.*, 
                   DATE_FORMAT(p.fecha_inicio, '%d/%m/%Y') AS fecha_inicio_fmt
            FROM proyecto p
            JOIN asignacion_proyecto ap ON p.id = ap.proyecto_id
            WHERE ap.empleado_id = %s
            ORDER BY p.fecha_inicio DESC, p.nombre
        """
        return self.ejecutar(query, (empleado_id,)) or []

    def empleados_del_proyecto(self, proyecto_id: int) -> List[Dict]:
        """Todos los empleados asignados a un proyecto"""
        query = """
            SELECT e.*, 
                   d.nombre AS departamento_nombre
            FROM empleado e
            JOIN asignacion_proyecto ap ON e.id = ap.empleado_id
            LEFT JOIN departamento d ON e.departamento_id = d.id
            WHERE ap.proyecto_id = %s
            ORDER BY e.nombre
        """
        return self.ejecutar(query, (proyecto_id,)) or []

    def total_asignados_proyecto(self, proyecto_id: int) -> int:
        """Cantidad de empleados en un proyecto"""
        query = "SELECT COUNT(*) AS total FROM asignacion_proyecto WHERE proyecto_id = %s"
        resultado = self.ejecutar(query, (proyecto_id,), fetch_one=True)
        return int(resultado['total']) if resultado else 0

    def total_proyectos_empleado(self, empleado_id: int) -> int:
        """Cantidad de proyectos en los que participa un empleado"""
        query = "SELECT COUNT(*) AS total FROM asignacion_proyecto WHERE empleado_id = %s"
        resultado = self.ejecutar(query, (empleado_id,), fetch_one=True)
        return int(resultado['total']) if resultado else 0

    def limpiar_proyecto(self, proyecto_id: int) -> int:
        """Elimina TODAS las asignaciones de un proyecto (usado al eliminarlo)"""
        query = "DELETE FROM asignacion_proyecto WHERE proyecto_id = %s"
        eliminadas = self.ejecutar(query, (proyecto_id,))
        if eliminadas and eliminadas > 0:
            print(f"Limpieza: {eliminadas} asignaciones eliminadas del proyecto {proyecto_id}")
        return eliminadas or 0

    def limpiar_empleado(self, empleado_id: int) -> int:
        """Elimina TODAS las asignaciones de un empleado (usado al eliminarlo)"""
        query = "DELETE FROM asignacion_proyecto WHERE empleado_id = %s"
        eliminadas = self.ejecutar(query, (empleado_id,))
        if eliminadas and eliminadas > 0:
            print(f"Limpieza: {eliminadas} asignaciones eliminadas del empleado {empleado_id}")
        return eliminadas or 0
