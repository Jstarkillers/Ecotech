# model/registro_tiempo.py - Corregido
from model.base_model import BaseModel
from datetime import datetime, date
from typing import List, Dict, Optional

class RegistroTiempo(BaseModel):
    """Modelo optimizado para registro de horas"""
    
    def registrar(self, empleado_id: int, proyecto_id: int, 
                  fecha: str, horas: float, descripcion: str = "") -> Optional[int]:
        """Registro optimizado con validaciones"""
        # Validaciones rápidas
        if not (0 < horas <= 24):
            print("❌ Horas deben estar entre 0.1 y 24")
            return None
        
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            print("❌ Formato de fecha inválido (YYYY-MM-DD)")
            return None
        
        # Verificar existencia (consultas separadas para claridad)
        from model.empleado import Empleado
        from model.proyecto import Proyecto
        
        if not Empleado().buscar_por_id(empleado_id):
            print(f"❌ Empleado ID {empleado_id} no existe")
            return None
        
        if not Proyecto().buscar_por_id(proyecto_id):
            print(f"❌ Proyecto ID {proyecto_id} no existe")
            return None
        
        # Insertar
        query = """
            INSERT INTO registro_tiempo 
            (empleado_id, proyecto_id, fecha, horas, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        registro_id = self.ejecutar(query, (
            empleado_id, proyecto_id, fecha, 
            round(horas, 2), descripcion.strip() or None
        ))
        
        if registro_id:
            print(f"✅ Horas registradas (ID: {registro_id})")
            return registro_id
        return None
    
    def listar_por_empleado(self, empleado_id: int, **kwargs) -> List[Dict]:
        fecha_desde = kwargs.get('fecha_desde')
        fecha_hasta = kwargs.get('fecha_hasta')
        
        query = """
            SELECT rt.*, p.nombre AS proyecto_nombre
            FROM registro_tiempo rt
            JOIN proyecto p ON rt.proyecto_id = p.id
            WHERE rt.empleado_id = %s
        """
        params = [empleado_id]

        if fecha_desde:
            query += " AND rt.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND rt.fecha <= %s"
            params.append(fecha_hasta)

        query += " ORDER BY rt.fecha DESC, rt.id DESC"
        return self.ejecutar(query, tuple(params)) or []
    
    def total_horas_empleado(self, empleado_id: int, **kwargs) -> float:
        fecha_desde = kwargs.get('fecha_desde')
        fecha_hasta = kwargs.get('fecha_hasta')
        
        query = "SELECT COALESCE(SUM(horas), 0) AS total FROM registro_tiempo WHERE empleado_id = %s"
        params = [empleado_id]

        if fecha_desde:
            query += " AND fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND fecha <= %s"
            params.append(fecha_hasta)

        resultado = self.ejecutar(query, tuple(params), fetch_one=True)
        return float(resultado['total']) if resultado else 0.0
    
    @classmethod
    def estadisticas_globales(cls) -> Dict:
        """Estadísticas optimizadas con menos consultas"""
        model = cls()
        
        # Consulta principal para múltiples estadísticas
        query = """
            SELECT 
                COUNT(DISTINCT rt.empleado_id) AS empleados_con_horas,
                COUNT(DISTINCT rt.proyecto_id) AS proyectos_activos,
                COALESCE(SUM(rt.horas), 0) AS total_horas,
                MIN(rt.fecha) AS fecha_primer,
                MAX(rt.fecha) AS fecha_ultimo
            FROM registro_tiempo rt
        """
        
        stats = model.ejecutar(query, fetch_one=True) or {}
        
        # Calcular promedios
        if stats.get('empleados_con_horas', 0) > 0:
            stats['promedio_horas'] = round(
                stats['total_horas'] / stats['empleados_con_horas'], 2
            )
        else:
            stats['promedio_horas'] = 0
        
        return {
            'total_horas_registradas': stats.get('total_horas', 0),
            'empleados_con_horas': stats.get('empleados_con_horas', 0),
            'proyectos_activos': stats.get('proyectos_activos', 0),
            'promedio_horas_por_empleado': stats['promedio_horas'],
            'fecha_primer_registro': stats.get('fecha_primer') or 'Nunca',
            'fecha_ultimo_registro': stats.get('fecha_ultimo') or 'Nunca'
        }