import os
import sys
import uuid
from concurrent import futures
import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pagos_pb2
import pagos_pb2_grpc


class ValidadorPagosServicer(pagos_pb2_grpc.ValidadorPagosServicer):
    """Implementación del servicio ValidadorPagos sin impresiones en consola."""

    def VerificarTransaccion(self, request, context):
        # Regla 1: Si el monto es menor o igual a cero, o el numero_tarjeta no tiene 16 dígitos
        if request.monto <= 0 or len(request.numero_tarjeta) != 16 or not request.numero_tarjeta.isdigit():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Monto o número de tarjeta inválido")
            return pagos_pb2.ResultadoPago()

        # Regla 2: Si la tarjeta inicia con "4000" (tarjeta bloqueada por lista negra)
        if request.numero_tarjeta.startswith("4000"):
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Tarjeta bloquada por fraude")
            return pagos_pb2.ResultadoPago()

        # Regla 3: Si el monto excede $10,000 USD, aprobar solo si el país de origen coincide con "US" o "MX"
        if request.monto > 10000 and request.codigo_moneda.upper() == "USD":
            if request.pais_origen.upper() not in ["US", "MX"]:
                return pagos_pb2.ResultadoPago(
                    aprobado=False,
                    codigo_autorizacion="",
                    motivo_rechazo="Transacción denegada por política de fraude: País no autorizado para montos superiores a $10,000 USD"
                )

        # Transacción aprobada
        codigo_auth = f"AUTH-{uuid.uuid4().hex[:8].upper()}"
        return pagos_pb2.ResultadoPago(
            aprobado=True,
            codigo_autorizacion=codigo_auth,
            motivo_rechazo=""
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pagos_pb2_grpc.add_ValidadorPagosServicer_to_server(ValidadorPagosServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
