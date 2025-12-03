# model/empleado.py - Optimizado
from model.base_model import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class Empleado(BaseModel):
    """Modelo Empleado optimizado"""
    
    def crear(self, nombre: str, email: str, **kwargs) -> Optional[int]:
        """Método crear optimizado con parámetros opcionales"""
        if not nombre or not email:
            print("❌ Nombre y email son obligatorios")
            return None
        
        # Parámetros por defecto
        datos = {
            'nombre': nombre.strip(),
            'email': email.lower().strip(),
            'direccion': kwargs.get('direccion'),
            'telefono': kwargs.get('telefono'),
            'fecha_contratacion': kwargs.get('fecha_contratacion') or datetime.today().strftime('%Y-%m-%d'),
            'salario': float(kwargs.get('salario', 0)),
            'departamento_id': kwargs.get('departamento_id'),
            'usuario_id': kwargs.get('usuario_id')
        }
        
        # Validar email
        if '@' not in datos['email']:
            print("❌ Email inválido")
            return None
        
        query = """
            INSERT INTO empleado 
            (nombre, direccion, telefono, email, fecha_contratacion, salario, departamento_id, usuario_id)
            VALUES (%(nombre)s, %(direccion)s, %(telefono)s, %(email)s, %(fecha_contratacion)s, 
                    %(salario)s, %(departamento_id)s, %(usuario_id)s)
        """
        
        try:
            empleado_id = self.ejecutar(query, datos)
            if empleado_id:
                print(f"✅ Empleado '{datos['nombre']}' creado (ID: {empleado_id})")
            return empleado_id
        except Exception as e:
            print(f"❌ Error al crear empleado: {e}")
            return None
    
    def listar(self) -> List[Dict]:
        query = """
            SELECT e.*, d.nombre AS departamento_nombre
            FROM empleado e
            LEFT JOIN departamento d ON e.departamento_id = d.id
            ORDER BY e.nombre
        """
        return self.ejecutar(query) or []
    
    def buscar_por_id(self, empleado_id: int) -> Optional[Dict]:
        query = """
            SELECT e.*, d.nombre AS departamento_nombre
            FROM empleado e
            LEFT JOIN departamento d ON e.departamento_id = d.id
            WHERE e.id = %s
        """
        return self.ejecutar(query, (empleado_id,), fetch_one=True)
    
    def actualizar(self, empleado_id: int, **campos) -> bool:
        if not campos:
            return False
        
        sets = []
        valores = []
        for campo, valor in campos.items():
            sets.append(f"{campo} = %s")
            valores.append(valor)
        
        valores.append(empleado_id)
        query = f"UPDATE empleado SET {', '.join(sets)} WHERE id = %s"
        
        return bool(self.ejecutar(query, tuple(valores)))
    
    def eliminar(self, empleado_id: int) -> bool:
        # Verificar si tiene registros relacionados primero
        query_check = "SELECT 1 FROM registro_tiempo WHERE empleado_id = %s LIMIT 1"
        if self.ejecutar(query_check, (empleado_id,), fetch_one=True):
            print("⚠️  El empleado tiene registros de horas. Eliminación parcial.")
        
        query = "DELETE FROM empleado WHERE id = %s"
        return bool(self.ejecutar(query, (empleado_id,)))