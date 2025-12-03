# model/usuario.py - Corregido
from model.base_model import BaseModel
import bcrypt
from typing import Dict, Optional, List

class Usuario(BaseModel):
    """Modelo Usuario optimizado"""
    
    def crear_admin(self) -> bool:
        """Crea usuario admin por defecto si no existe"""
        try:
            if not self.existe('admin'):
                password_hash = bcrypt.hashpw(
                    b'admin123', 
                    bcrypt.gensalt(rounds=10)
                ).decode('utf-8')
                
                query = """
                    INSERT INTO usuario (username, password_hash, rol) 
                    VALUES ('admin', %s, 'admin')
                """
                return bool(self.ejecutar(query, (password_hash,)))
        except Exception as e:
            print(f"Error al crear admin: {e}")
        return False
    
    def existe(self, username: str) -> bool:
        query = "SELECT 1 FROM usuario WHERE username = %s LIMIT 1"
        return bool(self.ejecutar(query, (username,), fetch_one=True))
    
    def crear(self, username: str, password: str, rol: str = 'empleado') -> Optional[int]:
        try:
            if rol not in ['admin', 'recursos_humanos', 'empleado']:
                print(f"❌ Rol inválido: {rol}")
                return None
                
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt(rounds=10)
            ).decode('utf-8')
            
            query = """
                INSERT INTO usuario (username, password_hash, rol) 
                VALUES (%s, %s, %s)
            """
            return self.ejecutar(query, (username, password_hash, rol))
        except Exception as e:
            print(f"❌ Error al crear usuario: {e}")
            return None
    
    def autenticar(self, username: str, password: str) -> Optional[Dict]:
        query = "SELECT id, username, password_hash, rol FROM usuario WHERE username = %s"
        resultado = self.ejecutar(query, (username,), fetch_one=True)
        
        if not resultado:
            return None
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), resultado['password_hash'].encode('utf-8')):
                return {
                    'id': resultado['id'],
                    'username': resultado['username'],
                    'rol': resultado['rol']
                }
        except Exception:
            pass
        return None
    
    def listar_todos(self) -> List[Dict]:
        return self.ejecutar("SELECT id, username, rol FROM usuario ORDER BY username") or []
    
    def cambiar_contraseña(self, usuario_id: int, nueva_contraseña: str) -> bool:
        try:
            password_hash = bcrypt.hashpw(
                nueva_contraseña.encode('utf-8'), 
                bcrypt.gensalt(rounds=10)
            ).decode('utf-8')
            
            query = "UPDATE usuario SET password_hash = %s WHERE id = %s"
            return bool(self.ejecutar(query, (password_hash, usuario_id)))
        except Exception:
            return False
    
    def cambiar_rol(self, usuario_id: int, nuevo_rol: str) -> bool:
        if nuevo_rol not in ['admin', 'recursos_humanos', 'empleado']:
            return False
        query = "UPDATE usuario SET rol = %s WHERE id = %s"
        return bool(self.ejecutar(query, (nuevo_rol, usuario_id)))
    
    def eliminar(self, usuario_id: int) -> bool:
        query = "DELETE FROM usuario WHERE id = %s AND username != 'admin'"
        return bool(self.ejecutar(query, (usuario_id,)))