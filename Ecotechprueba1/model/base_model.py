# model/base_model.py - Corregido
from config.database import DatabaseConnection
from typing import Optional, List, Dict, Any

class BaseModel:
    """Clase base optimizada con conexión por instancia"""
    
    def __init__(self):
        self.conn = DatabaseConnection.get_connection()
        self.cursor = self.conn.cursor()
    
    def ejecutar(self, query: str, params=None, fetch_one: bool = False) -> Any:
        """Método ejecutar optimizado"""
        try:
            self.cursor.execute(query, params or ())
            
            if query.strip().upper().startswith("SELECT"):
                result = self.cursor.fetchone() if fetch_one else self.cursor.fetchall()
                return result if result else ({} if fetch_one else [])
            
            elif query.strip().upper().startswith("INSERT"):
                self.conn.commit()
                return self.cursor.lastrowid
            
            else:  # UPDATE, DELETE
                self.conn.commit()
                return self.cursor.rowcount
                
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error en consulta: {e}")
            print(f"   Query: {query[:100]}...")
            return None if fetch_one else []
    
    def __del__(self):
        """Cierra cursor al eliminar instancia"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
    
    # Métodos genéricos optimizados
    def obtener_todos(self, tabla: str, orden: str = "id") -> List[Dict]:
        query = f"SELECT * FROM {tabla} ORDER BY {orden}"
        return self.ejecutar(query) or []
    
    def obtener_por_id(self, tabla: str, id_value: int) -> Optional[Dict]:
        query = f"SELECT * FROM {tabla} WHERE id = %s"
        return self.ejecutar(query, (id_value,), fetch_one=True)
    
    def eliminar_por_id(self, tabla: str, id_value: int) -> bool:
        query = f"DELETE FROM {tabla} WHERE id = %s"
        return bool(self.ejecutar(query, (id_value,)))
    
    def buscar_por_campo(self, tabla: str, campo: str, valor: str) -> List[Dict]:
        query = f"SELECT * FROM {tabla} WHERE {campo} LIKE %s"
        return self.ejecutar(query, (f"%{valor}%",)) or []