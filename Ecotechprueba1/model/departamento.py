# model/departamento.py
from model.base_model import BaseModel
from typing import Optional, List, Dict

class Departamento(BaseModel):
    """Modelo para gestión de departamentos"""
    
    def crear(self, nombre: str, gerente_id: Optional[int] = None) -> Optional[int]:
        """Crea un nuevo departamento"""
        nombre = nombre.strip()
        if not nombre:
            print("❌ El nombre del departamento es obligatorio")
            return None
        
        query = "INSERT INTO departamento (nombre, gerente_id) VALUES (%s, %s)"
        dept_id = self.ejecutar(query, (nombre, gerente_id))
        
        if dept_id:
            print(f"✅ Departamento '{nombre}' creado (ID: {dept_id})")
        return dept_id
    
    def listar(self) -> List[Dict]:
        """Lista todos los departamentos con información del gerente"""
        query = """
            SELECT d.*, 
                   e.nombre AS gerente_nombre,
                   (SELECT COUNT(*) FROM empleado WHERE departamento_id = d.id) AS total_empleados
            FROM departamento d
            LEFT JOIN empleado e ON d.gerente_id = e.id
            ORDER BY d.nombre
        """
        return self.ejecutar(query) or []
    
    def buscar_por_id(self, departamento_id: int) -> Optional[Dict]:
        """Busca un departamento por su ID"""
        query = """
            SELECT d.*, e.nombre AS gerente_nombre
            FROM departamento d
            LEFT JOIN empleado e ON d.gerente_id = e.id
            WHERE d.id = %s
        """
        return self.ejecutar(query, (departamento_id,), fetch_one=True)
    
    def asignar_gerente(self, departamento_id: int, gerente_id: Optional[int]) -> bool:
        """Asigna o quita un gerente del departamento"""
        # Verificar que el departamento existe
        dept = self.buscar_por_id(departamento_id)
        if not dept:
            print(f"❌ Departamento ID {departamento_id} no existe")
            return False
        
        # Si se asigna un gerente, verificar que el empleado existe
        if gerente_id:
            from model.empleado import Empleado
            emp = Empleado().buscar_por_id(gerente_id)
            if not emp:
                print(f"❌ Empleado ID {gerente_id} no existe")
                return False
        
        query = "UPDATE departamento SET gerente_id = %s WHERE id = %s"
        return bool(self.ejecutar(query, (gerente_id, departamento_id)))
    
    def actualizar(self, departamento_id: int, **campos) -> bool:
        """Actualiza un departamento"""
        if not campos:
            return False
        
        sets = []
        valores = []
        for campo, valor in campos.items():
            if campo in ['nombre']:
                sets.append(f"{campo} = %s")
                valores.append(valor)
        
        if not sets:
            return False
        
        valores.append(departamento_id)
        query = f"UPDATE departamento SET {', '.join(sets)} WHERE id = %s"
        return bool(self.ejecutar(query, tuple(valores)))
    
    def eliminar(self, departamento_id: int) -> bool:
        """Elimina un departamento"""
        # Verificar que no tenga empleados asignados
        query_check = "SELECT COUNT(*) AS total FROM empleado WHERE departamento_id = %s"
        resultado = self.ejecutar(query_check, (departamento_id,), fetch_one=True)
        
        if resultado and resultado['total'] > 0:
            print("❌ No se puede eliminar el departamento porque tiene empleados asignados")
            return False
        
        # Eliminar departamento
        query = "DELETE FROM departamento WHERE id = %s"
        return bool(self.ejecutar(query, (departamento_id,)))