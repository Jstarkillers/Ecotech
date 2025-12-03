# model/indicador_economico.py - VERSIÓN CORREGIDA
# API externa + persistencia + política de retención + nombres oficiales
from model.base_model import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

class IndicadorEconomico(BaseModel):
    """
    Modelo para gestionar indicadores económicos desde mindicador.cl
    Incluye "Indicadores Económicos" + persistencia + limpieza automática
    """

    # Nombres oficiales para mostrar al usuario
    NOMBRES_OFICIALES = {
        "uf": "Unidad de Fomento (UF)",
        "ivp": "Índice de Valor Promedio (IVP)",
        "dolar": "Dólar Observado",
        "euro": "Euro",
        "ipc": "Índice de Precios al Consumidor (IPC)",
        "utm": "Unidad Tributaria Mensual (UTM)",
        "bitcoin": "Bitcoin"
    }

    CODIGOS_VALIDOS = set(NOMBRES_OFICIALES.keys())

    @classmethod
    def es_codigo_valido(cls, codigo: str) -> bool:
        return codigo.lower().strip() in cls.CODIGOS_VALIDOS

    # ====================== GUARDAR / ACTUALIZAR ======================
    def guardar(self, codigo: str, fecha: str, valor: float, fuente: str = "https://mindicador.cl") -> bool:
        """
        Guarda o actualiza un valor de indicador.
        Usa ON DUPLICATE KEY UPDATE → evita duplicados y actualiza si cambia el valor.
        """
        codigo = codigo.lower().strip()

        if codigo not in self.CODIGOS_VALIDOS:
            print(f"Indicador no soportado: {codigo}")
            return False

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            print("Fecha inválida (debe ser YYYY-MM-DD)")
            return False

        nombre = self.NOMBRES_OFICIALES[codigo]

        query = """
            INSERT INTO indicador_economico (codigo, nombre, fecha, valor, fuente)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                valor = VALUES(valor),
                fuente = VALUES(fuente),
                registrado_en = CURRENT_TIMESTAMP
        """
        
        try:
            resultado = self.ejecutar(query, (codigo, nombre, fecha, round(float(valor), 4), fuente))
            
            if resultado:
                print(f"✅ {nombre} → {fecha}: ${valor:,.4f} guardado correctamente")
                return True
            else:
                print(f"❌ No se pudo guardar {nombre}")
                return False
                
        except Exception as e:
            print(f"❌ Error al guardar indicador: {e}")
            return False

    # ====================== CONSULTAS ======================
    def obtener(self, codigo: str, fecha: str) -> Optional[Dict]:
        query = "SELECT * FROM indicador_economico WHERE codigo = %s AND fecha = %s"
        return self.ejecutar(query, (codigo.lower(), fecha), fetch_one=True)

    def ultimo_valor(self, codigo: str) -> Optional[Dict]:
        """Último valor registrado (más reciente)"""
        if codigo.lower() not in self.CODIGOS_VALIDOS:
            return None
        
        query = """
            SELECT *, DATE_FORMAT(fecha, '%%d/%%m/%%Y') AS fecha_chilena
            FROM indicador_economico
            WHERE codigo = %s
            ORDER BY fecha DESC, registrado_en DESC
            LIMIT 1
        """
        return self.ejecutar(query, (codigo.lower(),), fetch_one=True)

    def historial(self, codigo: str, dias: int = 30) -> List[Dict]:
        """Historial reciente de un indicador"""
        if codigo.lower() not in self.CODIGOS_VALIDOS:
            return []
        
        query = """
            SELECT 
                codigo,
                nombre,
                DATE_FORMAT(fecha, '%%d/%%m/%%Y') AS fecha,
                valor
            FROM indicador_economico
            WHERE codigo = %s
            ORDER BY fecha DESC
            LIMIT %s
        """
        return self.ejecutar(query, (codigo.lower(), dias)) or []

    def listar_todos_ultimos(self) -> List[Dict]:
        """Último valor de cada indicador (ideal para menú) - CORREGIDO"""
        try:
            query = """
                SELECT 
                    i.codigo,
                    i.nombre,
                    DATE_FORMAT(i.fecha, '%%d/%%m/%%Y') AS fecha,
                    i.valor
                FROM indicador_economico i
                INNER JOIN (
                    SELECT codigo, MAX(fecha) AS max_fecha
                    FROM indicador_economico
                    GROUP BY codigo
                ) ultimos ON i.codigo = ultimos.codigo AND i.fecha = ultimos.max_fecha
                ORDER BY i.codigo
            """
            resultado = self.ejecutar(query)
            
            if resultado is None:
                return []
            
            # Asegurar que todos los valores sean strings válidos
            for item in resultado:
                if item:
                    item['nombre'] = str(item.get('nombre', 'Desconocido'))
                    item['fecha'] = str(item.get('fecha', 'Sin fecha'))
                    item['valor'] = float(item.get('valor', 0))
                    
            return resultado
            
        except Exception as e:
            print(f"❌ Error en listar_todos_ultimos: {e}")
            return []

    # ====================== MANTENIMIENTO ======================
    def limpiar_antiguos(self, dias_retencion: int = 730) -> int:
        """
        Elimina indicadores antiguos (política de retención)
        Recomendado: 2 años (730 días)
        """
        fecha_corte = (date.today() - timedelta(days=dias_retencion)).strftime('%Y-%m-%d')
        query = "DELETE FROM indicador_economico WHERE fecha < %s"
        eliminados = self.ejecutar(query, (fecha_corte,))
        if eliminados and eliminados > 0:
            print(f"Limpieza automática: {eliminados} registros antiguos eliminados (> {dias_retencion} días)")
        return eliminados or 0

    def estadisticas(self) -> Dict[str, Any]:
        """Estadísticas generales del módulo"""
        try:
            total = self.ejecutar("SELECT COUNT(*) AS c FROM indicador_economico", fetch_one=True)
            indicadores = self.ejecutar("SELECT COUNT(DISTINCT codigo) AS c FROM indicador_economico", fetch_one=True)
            ultimo_update = self.ejecutar("SELECT MAX(registrado_en) AS u FROM indicador_economico", fetch_one=True)
            
            return {
                "total_registros": total.get('c', 0) if total else 0,
                "indicadores_activos": indicadores.get('c', 0) if indicadores else 0,
                "ultima_actualizacion": ultimo_update.get('u', "Nunca") if ultimo_update else "Nunca"
            }
        except Exception as e:
            print(f"❌ Error en estadísticas: {e}")
            return {
                "total_registros": 0,
                "indicadores_activos": 0,
                "ultima_actualizacion": "Nunca"
            }