# model/proyecto.py - Corregido
from model.base_model import BaseModel
from model.empleado import Empleado
from datetime import datetime
from typing import Optional, List, Dict

class Proyecto(BaseModel):
    """Modelo Proyecto optimizado"""
    
    def crear(self, nombre: str, descripcion: str = "", **kwargs) -> Optional[int]:
        nombre = nombre.strip()
        if not nombre:
            print("❌ Nombre del proyecto es obligatorio")
            return None
        
        datos = {
            'nombre': nombre,
            'descripcion': descripcion.strip() or None,
            'fecha_inicio': kwargs.get('fecha_inicio') or datetime.today().strftime('%Y-%m-%d'),
            'estado': 'activo'
        }
        
        query = """
            INSERT INTO proyecto (nombre, descripcion, fecha_inicio, estado)
            VALUES (%(nombre)s, %(descripcion)s, %(fecha_inicio)s, %(estado)s)
        """
        
        proyecto_id = self.ejecutar(query, datos)
        if proyecto_id:
            print(f"✅ Proyecto '{nombre}' creado (ID: {proyecto_id})")
        return proyecto_id
    
    def listar(self, incluir_empleados: bool = False) -> List[Dict]:
        """Listar optimizado - incluir_empleados es opcional para mejor performance"""
        if incluir_empleados:
            query = """
                SELECT p.*, 
                       GROUP_CONCAT(e.nombre SEPARATOR ', ') AS empleados_asignados
                FROM proyecto p
                LEFT JOIN asignacion_proyecto ap ON p.id = ap.proyecto_id
                LEFT JOIN empleado e ON ap.empleado_id = e.id
                GROUP BY p.id
                ORDER BY p.fecha_inicio DESC
            """
        else:
            query = "SELECT * FROM proyecto ORDER BY fecha_inicio DESC, nombre"
        
        return self.ejecutar(query) or []
    
    def buscar_por_id(self, proyecto_id: int) -> Optional[Dict]:
        query = """
            SELECT p.*,
                   GROUP_CONCAT(e.id) AS empleados_ids,
                   GROUP_CONCAT(e.nombre SEPARATOR ', ') AS empleados_nombres
            FROM proyecto p
            LEFT JOIN asignacion_proyecto ap ON p.id = ap.proyecto_id
            LEFT JOIN empleado e ON ap.empleado_id = e.id
            WHERE p.id = %s
            GROUP BY p.id
        """
        return self.ejecutar(query, (proyecto_id,), fetch_one=True)
    
    def actualizar(self, proyecto_id: int, **campos) -> bool:
        if not campos:
            return False
        
        sets = []
        valores = []
        for campo, valor in campos.items():
            if campo in ['nombre', 'descripcion', 'fecha_inicio', 'estado']:
                sets.append(f"{campo} = %s")
                valores.append(valor)
        
        if not sets:
            return False
        
        valores.append(proyecto_id)
        query = f"UPDATE proyecto SET {', '.join(sets)} WHERE id = %s"
        return bool(self.ejecutar(query, tuple(valores)))
    
    def asignar_empleado(self, proyecto_id: int, empleado_id: int) -> bool:
        # Verificar existencia
        if not Empleado().buscar_por_id(empleado_id):
            print(f"❌ Empleado ID {empleado_id} no existe")
            return False
        
        if not self.buscar_por_id(proyecto_id):
            print(f"❌ Proyecto ID {proyecto_id} no existe")
            return False
        
        query = "INSERT IGNORE INTO asignacion_proyecto (empleado_id, proyecto_id) VALUES (%s, %s)"
        return bool(self.ejecutar(query, (empleado_id, proyecto_id)))
    
    def desasignar_empleado(self, proyecto_id: int, empleado_id: int) -> bool:
        query = "DELETE FROM asignacion_proyecto WHERE empleado_id = %s AND proyecto_id = %s"
        return bool(self.ejecutar(query, (empleado_id, proyecto_id)))
    
    def eliminar(self, proyecto_id: int) -> bool:
        if not self.buscar_por_id(proyecto_id):
            print("❌ Proyecto no encontrado")
            return False
        
        query = "DELETE FROM proyecto WHERE id = %s"
        return bool(self.ejecutar(query, (proyecto_id,)))
    
    def empleados_en_proyecto(self, proyecto_id: int) -> List[Dict]:
        query = """
            SELECT e.*
            FROM empleado e
            JOIN asignacion_proyecto ap ON e.id = ap.empleado_id
            WHERE ap.proyecto_id = %s
            ORDER BY e.nombre
        """
        return self.ejecutar(query, (proyecto_id,)) or []