import os
import sys
import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pagos_pb2
import pagos_pb2_grpc


def procesar_transaccion(stub, descripcion_caso, id_transaccion, numero_tarjeta, monto, codigo_moneda, pais_origen):
    print("\n" + "=" * 75)
    print(f"ESCENARIO: {descripcion_caso}")
    print(f"Datos enviados -> ID: {id_transaccion} | Tarjeta: {numero_tarjeta} | "
          f"Monto: {monto} {codigo_moneda} | País: {pais_origen}")
    print("-" * 75)

    solicitud = pagos_pb2.SolicitudPago(
        id_transaccion=id_transaccion,
        numero_tarjeta=numero_tarjeta,
        monto=monto,
        codigo_moneda=codigo_moneda,
        pais_origen=pais_origen,
    )

    try:
        respuesta = stub.VerificarTransaccion(solicitud)
        if respuesta.aprobado:
            print(f"[STATUS: APROBADO]")
            print(f"  * Código de Autorización : {respuesta.codigo_autorizacion}")
        else:
            print(f"[STATUS: RECHAZADO POR POLÍTICA]")
            print(f"  * Motivo de Rechazo      : {respuesta.motivo_rechazo}")
    except grpc.RpcError as e:
        print(f"[STATUS: EXCEPCIÓN gRPC CAPTURADA]")
        print(f"  * Código de estado (e.code())    : {e.code()}")
        print(f"  * Detalle del error (e.details()): {e.details()}")


def main():
    canal = grpc.insecure_channel("localhost:50051")
    stub = pagos_pb2_grpc.ValidadorPagosStub(canal)

    print("###########################################################################")
    print("           EJECUTANDO CASOS DE PRUEBA - VALIDACIÓN DE PAGOS gRPC          ")
    print("###########################################################################")

    # Caso 1: Pago exitoso
    procesar_transaccion(
        stub=stub,
        descripcion_caso="Caso 1: Pago Exitoso (Tarjeta válida, monto válido)",
        id_transaccion="TXN-1001",
        numero_tarjeta="4532015893201452",
        monto=150.75,
        codigo_moneda="USD",
        pais_origen="US",
    )

    # Caso 2: Argumento inválido (Monto negativo)
    procesar_transaccion(
        stub=stub,
        descripcion_caso="Caso 2: Argumento Inválido (Monto negativo)",
        id_transaccion="TXN-1002",
        numero_tarjeta="4532015893201452",
        monto=-25.00,
        codigo_moneda="USD",
        pais_origen="MX",
    )

    # Caso 3: Tarjeta denegada (Inicia con 4000 - Bloqueada en lista negra)
    procesar_transaccion(
        stub=stub,
        descripcion_caso="Caso 3: Tarjeta Denegada por Lista Negra (Inicia con 4000)",
        id_transaccion="TXN-1003",
        numero_tarjeta="4000123456789010",
        monto=500.00,
        codigo_moneda="USD",
        pais_origen="US",
    )

    # Caso 4 (Demostración adicional): Monto superior a $10,000 USD desde país no autorizado
    procesar_transaccion(
        stub=stub,
        descripcion_caso="Caso 4 (Adicional): Monto > $10,000 USD con país no registrado (BR)",
        id_transaccion="TXN-1004",
        numero_tarjeta="5200123456789012",
        monto=15000.00,
        codigo_moneda="USD",
        pais_origen="BR",
    )

    print("\n" + "=" * 75)
    print("Fin de las pruebas de validación.")


if __name__ == "__main__":
    main()
