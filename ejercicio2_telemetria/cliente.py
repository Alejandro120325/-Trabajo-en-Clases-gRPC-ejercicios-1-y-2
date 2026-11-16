import os
import sys
import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import telemetria_pb2
import telemetria_pb2_grpc

# Habilitar soporte ANSI en terminales de Windows
os.system("")

# Códigos de colores ANSI para la consola
COLOR_RESET = "\033[0m"
COLOR_VERDE = "\033[92m"
COLOR_ROJO_BRILLANTE = "\033[91m"
COLOR_FONDO_ROJO = "\033[41m\033[97m\033[1m"
COLOR_AMARILLO = "\033[93m"
COLOR_CIAN = "\033[96m"
COLOR_NEGRITA = "\033[1m"


def suscribirse_a_telemetria(stub, id_camion, intervalo_segundos=1, max_lecturas=None):
    """
    Se suscribe al flujo de telemetría de un camión usando el patrón Server Streaming.
    Consume el stream mediante un bucle `for respuesta in stub.TransmitirTelemetria(peticion)`.
    """
    print("\n" + "=" * 80)
    print(f"{COLOR_CIAN}Iniciando suscripción a telemetría para: {COLOR_NEGRITA}{id_camion}{COLOR_RESET}")
    print(f"Intervalo de actualización: {intervalo_segundos} segundo(s)")
    if max_lecturas:
        print(f"Modo demostración: Se recibirán {max_lecturas} lecturas.")
    print("=" * 80)

    peticion = telemetria_pb2.SuscripcionCamion(
        id_camion=id_camion,
        intervalo_segundos=intervalo_segundos
    )

    try:
        stream = stub.TransmitirTelemetria(peticion)
        contador = 0

        # Consumo de la respuesta de Server Streaming evento a evento
        for respuesta in stream:
            contador += 1

            if respuesta.alerta_critica:
                # Resaltado especial en consola para Alerta Crítica (Fuera del rango 2°C - 8°C)
                etiqueta = f"{COLOR_FONDO_ROJO} 🚨 ALERTA CRÍTICA: FUERA DE RANGO [2°C - 8°C] {COLOR_RESET}"
                temp_str = f"{COLOR_ROJO_BRILLANTE}{COLOR_NEGRITA}{respuesta.temperatura_celsius:.2f} °C{COLOR_RESET}"
            else:
                etiqueta = f"{COLOR_VERDE}✅ ESTADO SEGURO (Cadena de Frío OK){COLOR_RESET}"
                temp_str = f"{COLOR_VERDE}{respuesta.temperatura_celsius:.2f} °C{COLOR_RESET}"

            print(f"[{contador:02d}] {respuesta.timestamp} | Camión: {COLOR_NEGRITA}{respuesta.id_camion}{COLOR_RESET}")
            print(f"     Temperatura : {temp_str}  -->  {etiqueta}")
            print(f"     Ubicación   : Lat: {respuesta.latitud:.6f}, Lon: {respuesta.longitud:.6f}")
            print("-" * 80)

            if max_lecturas and contador >= max_lecturas:
                print(f"{COLOR_AMARILLO}Finalizando demostración tras recibir {max_lecturas} lecturas.{COLOR_RESET}")
                break

    except grpc.RpcError as e:
        print(f"\n{COLOR_ROJO_BRILLANTE}[EXCEPCIÓN gRPC CAPTURADA]{COLOR_RESET}")
        print(f"  * Código de estado (e.code())    : {e.code()}")
        print(f"  * Detalle del error (e.details()): {e.details()}")
    except KeyboardInterrupt:
        print(f"\n{COLOR_AMARILLO}Suscripción cancelada por el usuario (Ctrl+C).{COLOR_RESET}")


def main():
    canal = grpc.insecure_channel("localhost:50051")
    stub = telemetria_pb2_grpc.MonitorCadenaFrioStub(canal)

    print("################################################################################")
    print("      MONITOR EN TIEMPO REAL - TELEMETRÍA IoT Y CADENA DE FRÍO (gRPC STREAM)    ")
    print("################################################################################")

    # Caso 1: Camión no registrado (Debe retornar StatusCode.NOT_FOUND)
    print("\n--- PRUEBA 1: Suscripción con Camión Inexistente (Error Handling) ---")
    suscribirse_a_telemetria(stub, id_camion="CAM-999", intervalo_segundos=1)

    # Caso 2: Suscripción válida en tiempo real con detección de alertas críticas
    print("\n--- PRUEBA 2: Suscripción Válida a 'CAM-001' (Server Streaming) ---")
    suscribirse_a_telemetria(stub, id_camion="CAM-001", intervalo_segundos=1, max_lecturas=8)


if __name__ == "__main__":
    main()
