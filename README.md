# Laboratorio de Microservicios con gRPC y Protocol Buffers (Python)

Este repositorio contiene las soluciones organizadas en carpetas independientes para cada ejercicio:

- [`ejercicio1_pagos/`](file:///C:/Users/carri/PycharmProjects/gRPC_II/ejercicio1_pagos): Microservicio Unario de Validación de Pagos y Detección de Fraude en E-Commerce.
- [`ejercicio2_telemetria/`](file:///C:/Users/carri/PycharmProjects/gRPC_II/ejercicio2_telemetria): Monitor en Tiempo Real de Telemetría IoT y Cadena de Frío Logística (Server Streaming).

---

## 📦 Instalación y Configuración del Entorno

Activar el entorno virtual e instalar las dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
pip install grpcio grpcio-tools
```

---

## 💳 Ejercicio 1: Validación de Pagos y Fraude (Unario)

Ubicación: `ejercicio1_pagos/`

### 📁 Archivos
- `pagos.proto`: Definición del contrato del servicio `ValidadorPagos`.
- `pagos_pb2.py` / `pagos_pb2_grpc.py`: Código generado por Protobuf.
- `servidor.py`: Servidor gRPC que valida montos, longitud de tarjeta y lista negra (`INVALID_ARGUMENT`, `PERMISSION_DENIED`). Ejecución silenciosa sin impresiones en consola.
- `cliente.py`: Cliente que ejecuta 4 escenarios de prueba y captura excepciones `grpc.RpcError`.

### 🚀 Ejecución

**Terminal 1 (Servidor):**
```powershell
python ejercicio1_pagos/servidor.py
```

**Terminal 2 (Cliente):**
```powershell
python ejercicio1_pagos/cliente.py
```

---

## 🧊 Ejercicio 2: Monitor de Telemetría IoT y Cadena de Frío (Server Streaming)

Ubicación: `ejercicio2_telemetria/`

### 📁 Archivos
- `telemetria.proto`: Contrato gRPC con el servicio `MonitorCadenaFrio` y el método `rpc TransmitirTelemetria (SuscripcionCamion) returns (stream LecturaSensor);`.
- `telemetria_pb2.py` / `telemetria_pb2_grpc.py`: Código generado por Protobuf.
- `servidor.py`: Servidor que emite un flujo continuo de lecturas usando `yield` y evalúa el rango de frío (2°C a 8°C). Ejecución silenciosa sin impresiones en consola.
- `cliente.py`: Cliente que consume el stream con `for respuesta in stub.TransmitirTelemetria(peticion):` y resalta en rojo/alerta las lecturas críticas fuera de rango.

### 🚀 Ejecución

**Terminal 1 (Servidor):**
```powershell
python ejercicio2_telemetria/servidor.py
```

**Terminal 2 (Cliente):**
```powershell
python ejercicio2_telemetria/cliente.py
```
