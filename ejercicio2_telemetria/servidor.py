import os
import sys
import datetime
import random
import time
from concurrent import futures
import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import telemetria_pb2
import telemetria_pb2_grpc

CAMIONES_VALIDOS = {
    "CAM-001": {"lat": 19.432608, "lon": -99.133209},
    "CAM-002": {"lat": 20.659698, "lon": -103.349609},
}


class MonitorCadenaFrioServicer(telemetria_pb2_grpc.MonitorCadenaFrioServicer):
    """Implementación del servicio de Server Streaming para telemetría IoT."""

    def TransmitirTelemetria(self, request, context):
        id_camion = request.id_camion
        intervalo = request.intervalo_segundos if request.intervalo_segundos > 0 else 1

        # Regla de negocio: Si el id_camion no existe en el sistema
        if id_camion not in CAMIONES_VALIDOS:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"El camión '{id_camion}' no existe en el sistema. Registrados: {list(CAMIONES_VALIDOS.keys())}"
            )
            return

        camion = CAMIONES_VALIDOS[id_camion]
        lat = camion["lat"]
        lon = camion["lon"]

        # Patrón de temperaturas que alterna lecturas seguras (2.0°C a 8.0°C)
        # y anomalías críticas (<2.0°C o >8.0°C) para probar la alerta
        patron_temperaturas = [4.5, 4.9, 5.2, 1.7, 4.8, 7.8, 8.5, 9.2, 5.5, 3.4]
        indice = 0

        while context.is_active():
            temp_base = patron_temperaturas[indice % len(patron_temperaturas)]
            temp = round(temp_base + random.uniform(-0.15, 0.15), 2)
            indice += 1

            # Desplazamiento simulado de coordenadas
            lat += random.uniform(-0.0003, 0.0003)
            lon += random.uniform(-0.0003, 0.0003)

            # Regla de negocio: Alerta crítica si temperatura < 2.0°C o > 8.0°C
            alerta_critica = (temp < 2.0 or temp > 8.0)
            timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            lectura = telemetria_pb2.LecturaSensor(
                id_camion=id_camion,
                temperatura_celsius=temp,
                latitud=round(lat, 6),
                longitud=round(lon, 6),
                timestamp=timestamp_str,
                alerta_critica=alerta_critica,
            )

            yield lectura
            time.sleep(intervalo)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetria_pb2_grpc.add_MonitorCadenaFrioServicer_to_server(MonitorCadenaFrioServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
