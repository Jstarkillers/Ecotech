# controller/indicador_controller.py
# Consumo seguro de API + logging de consultas + manejo total de errores
import requests
from datetime import datetime
from typing import Dict, Any
from model.indicador_economico import IndicadorEconomico
from model.consulta_indicador import ConsultaIndicador

class IndicadorController:
    """
    Controlador completo para consumo de mindicador.cl
    • Timeout, retries, headers
    • Validación estricta
    • Logging completo de consultas
    • Manejo avanzado de excepciones
    """

    URL_BASE = "https://mindicador.cl/api"
    TIMEOUT = 12  # segundos

    # Indicadores soportados oficialmente
    INDICADORES = {
        "uf":     "Unidad de Fomento (UF)",
        "ivp":    "Índice de Valor Promedio (IVP)",
        "dolar":  "Dólar Observado",
        "euro":   "Euro",
        "ipc":    "Índice de Precios al Consumidor (IPC)",
        "utm":    "Unidad Tributaria Mensual (UTM)",
        "bitcoin": "Bitcoin"
    }

    @staticmethod
    def _formatear_valor(valor: float) -> str:
        """Formato chileno: 12.345,67"""
        return f"{valor:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _formatear_fecha(fecha_iso: str) -> str:
        """De 2025-12-01 → 01-12-2025"""
        return datetime.strptime(fecha_iso[:10], "%Y-%m-%d").strftime("%d-%m-%Y")

    @classmethod
    def mostrar_menu(cls):
        print("\n" + "═" * 55)
        print("     CONSULTA DE INDICADORES ECONÓMICOS - CHILE 2025")
        print("═" * 66)
        for codigo, nombre in cls.INDICADORES.items():
            print(f"  {codigo.upper():<8} → {nombre}")
        print("─" * 55)

    @classmethod
    def consultar(cls, usuario_id: int) -> None:
        """
        Método principal – flujo completo de consulta
        """
        cls.mostrar_menu()
        codigo = input("\nCódigo del indicador → ").strip().lower()
        if codigo not in cls.INDICADORES:
            print("Código no válido. Intente nuevamente.")
            input("\nPresione ENTER para continuar...")
            return

        fecha_input = input("Fecha (YYYY-MM-DD) o ENTER para hoy → ").strip()

        if fecha_input:
            try:
                datetime.strptime(fecha_input, "%Y-%m-%d")
                fecha_url = f"/{fecha_input[8:10]}-{fecha_input[5:7]}-{fecha_input[:4]}"
                fecha_mostrar = cls._formatear_fecha(fecha_input)
            except ValueError:
                print("Formato de fecha inválido.")
                input("\nPresione ENTER...")
                return
        else:
            fecha_url = ""
            fecha_iso = datetime.today().strftime("%Y-%m-%d")
            fecha_mostrar = "hoy"

        url = f"{cls.URL_BASE}/{codigo}{fecha_url}"
        print(f"\nConsultando → {url}")

        try:
            headers = {
                "User-Agent": "EcoTechSolutions-Poo2025/1.0",
                "Accept": "application/json"
            }

            response = requests.get(url, timeout=cls.TIMEOUT, headers=headers)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            if 'serie' not in data or not data['serie']:
                print("No hay datos disponibles para esa fecha.")
                input("\nPresione ENTER para continuar...")
                return

            valor_info = data['serie'][0]
            valor = float(valor_info['valor'])
            fecha_iso = valor_info['fecha'][:10]
            nombre = cls.INDICADORES[codigo]

            # === MOSTRAR RESULTADO ===
            print("\n" + "═" * 55)
            print(f" INDICADOR: {nombre}")
            print(f" FECHA    : {cls._formatear_fecha(fecha_iso)}")
            print(f" VALOR    : {cls._formatear_valor(valor)}")
            print("═" * 55)

            # === REGISTRAR CONSULTA (siempre) ===
            guardado_final = False
            if input("\n¿Guardar este valor permanentemente en el sistema? (s/N) → ").strip().lower() == 's':
                ind_model = IndicadorEconomico()
                if ind_model.guardar(codigo=codigo, fecha=fecha_iso, valor=valor):
                    guardado_final = True
                    print("Indicador guardado exitosamente en el historial permanente.")
                else:
                    print("No se pudo guardar permanentemente.")
            else:
                print("Consulta registrada en bitácora, pero no guardada permanentemente.")

            # === REGISTRO ÚNICO Y PERFECTO EN AUDITORÍA ===
            ConsultaIndicador().registrar(
                usuario_id=usuario_id,
                codigo=codigo,
                fecha_indicador=fecha_iso,
                valor=valor,
                guardado=guardado_final
            )

            # === REGISTRO EN BITÁCORA (SIEMPRE SE GUARDA – para el Top 10) ===
            ConsultaIndicador.registrar_consulta(
                usuario_id=usuario_id,
                indicador_codigo=codigo,
                fecha_indicador=fecha_iso,
                valor=valor,
                guardado=guardado_final
            )

            print("Consulta registrada en el sistema de auditoría.")

        except requests.exceptions.Timeout:
            print("Tiempo de espera agotado. Verifique su conexión.")
        except requests.exceptions.ConnectionError:
            print("Error de conexión. No hay internet o mindicador.cl está caído.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("Indicador o fecha no encontrada en mindicador.cl")
            else:
                print(f"Error HTTP {e.response.status_code}")
        except Exception as e:
            print(f"Error inesperado: {e}")

        input("\nPresione ENTER para continuar...")
