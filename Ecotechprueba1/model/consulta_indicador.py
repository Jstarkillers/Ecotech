# model/consulta_indicador.py
# Logging completo de uso del sistema + estadísticas + privacidad
from model.base_model import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

class ConsultaIndicador(BaseModel):
    """
    Modelo que registra TODAS las consultas a indicadores económicos.
    Cumple al 100% el requisito de auditoría y trazabilidad del sistema.
    Incluye estadísticas, limpieza automática y privacidad de datos.
    """

    def registrar(self, usuario_id: int, codigo: str, fecha_indicador: str,
                  valor: float, guardado: bool = False) -> Optional[int]:
        """
        Registra una consulta realizada por un usuario.
        Es obligatorio registrar TODAS las consultas (incluso las no guardadas).
        """
        codigo = codigo.lower().strip()

        try:
            datetime.strptime(fecha_indicador, "%Y-%m-%d")
        except ValueError:
            print("Error interno: fecha del indicador inválida.")
            return None

        query = """
            INSERT INTO consulta_indicador 
            (usuario_id, indicador_codigo, fecha_indicador, valor, guardado)
            VALUES (%s, %s, %s, %s, %s)
        """
        consulta_id = self.ejecutar(query, (
            usuario_id,
            codigo,
            fecha_indicador,
            round(float(valor), 4),
            1 if guardado else 0
        ))

        if consulta_id:
            estado = "guardada permanentemente" if guardado else "registrada en bitácora"
            print(f"Consulta de {codigo.upper()} {estado}.")
        return consulta_id

    def listar_por_usuario(self, usuario_id: int, limite: int = 50) -> List[Dict]:
        """Historial completo de consultas del usuario"""
        query = """
            SELECT 
                ci.*,
                DATE_FORMAT(ci.fecha_consulta, '%d/%m/%Y %H:%i') AS fecha_consulta_cl,
                DATE_FORMAT(ci.fecha_indicador, '%d/%m/%Y') AS fecha_indicador_cl,
                CASE WHEN ci.guardado = 1 THEN 'Sí' ELSE 'No' END AS guardado_txt
            FROM consulta_indicador ci
            WHERE ci.usuario_id = %s
            ORDER BY ci.fecha_consulta DESC
            LIMIT %s
        """
        return self.ejecutar(query, (usuario_id, limite)) or []

    def estadisticas_usuario(self, usuario_id: int) -> List[Dict]:
        """Estadísticas detalladas por indicador para un usuario"""
        query = """
            SELECT 
                indicador_codigo AS código,
                COUNT(*) AS consultas_realizadas,
                SUM(guardado) AS veces_guardado,
                ROUND(AVG(valor), 4) AS valor_promedio
            FROM consulta_indicador
            WHERE usuario_id = %s
            GROUP BY indicador_codigo
            ORDER BY consultas_realizadas DESC
        """
        return self.ejecutar(query, (usuario_id,)) or []

    def total_consultas_hoy(self) -> int:
        """Total de consultas realizadas hoy en todo el sistema"""
        query = """
            SELECT COUNT(*) AS total 
            FROM consulta_indicador 
            WHERE DATE(fecha_consulta) = CURDATE()
        """
        resultado = self.ejecutar(query, fetch_one=True)
        return int(resultado['total']) if resultado else 0

    def top_indicadores_global(self, limite: int = 5) -> List[Dict]:
        """Los indicadores más consultados en todo el sistema"""
        query = """
            SELECT 
                indicador_codigo AS indicador,
                COUNT(*) AS consultas,
                SUM(guardado) AS guardados
            FROM consulta_indicador
            GROUP BY indicador_codigo
            ORDER BY consultas DESC
            LIMIT %s
        """
        return self.ejecutar(query, (limite,)) or []

    def resumen_mensual_usuario(self, usuario_id: int, año: int = None, mes: int = None) -> Dict:
        """Resumen mensual de actividad del usuario"""
        if not año:
            año = date.today().year
        if not mes:
            mes = date.today().month

        query = """
            SELECT 
                COUNT(*) AS consultas_mes,
                SUM(guardado) AS guardados_mes,
                COUNT(DISTINCT indicador_codigo) AS indicadores_distintos
            FROM consulta_indicador
            WHERE usuario_id = %s
              AND YEAR(fecha_consulta) = %s
              AND MONTH(fecha_consulta) = %s
        """
        resultado = self.ejecutar(query, (usuario_id, año, mes), fetch_one=True)
        return {
            "mes": f"{mes:02d}/{año}",
            "consultas": resultado['consultas_mes'] if resultado else 0,
            "guardados": resultado['guardados_mes'] if resultado else 0,
            "distintos": resultado['indicadores_distintos'] if resultado else 0
        }

    def limpiar_consultas_antiguas(self, dias_retencion: int = 180) -> int:
        """
        Política de privacidad: elimina consultas antiguas
        Recomendado: 180 días (6 meses)
        """
        fecha_corte = (date.today() - timedelta(days=dias_retencion)).strftime("%Y-%m-%d")
        query = "DELETE FROM consulta_indicador WHERE fecha_consulta < %s"
        eliminadas = self.ejecutar(query, (fecha_corte,))
        
        if eliminadas and eliminadas > 0:
            print(f"Privacidad: {eliminadas} consultas antiguas eliminadas (>{dias_retencion} días)")
        return eliminadas or 0
