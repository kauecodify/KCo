# MEX | Intelligent Vision AI

Plataforma industrial de inspeccion inteligente por vision computacional para la operacion en Mexico. Permite que cualquier operador capture una pieza con la camara de un smartphone Android o iOS y reciba automaticamente su identificacion, clasificacion y resultado de inspeccion.

Toda la complejidad tecnologica (motor de vision, comparacion con referencias, calibracion de confianza, auditoria y metricas) permanece en el backend. La experiencia del operador se limita a: abrir, apuntar la camara, capturar y recibir el resultado.

---

## Arquitectura

```
CAPTURA MOBILE
    |
    v
VALIDACION LOCAL DE IMAGEN (compresion y redimension en el dispositivo)
    |
    v
API REST (FastAPI, JWT, RBAC)
    |
    v
VALIDACION DE CALIDAD (nitidez, iluminacion, reflejos, resolucion)
    |
    v
MOTOR DE VISION (ORB feature matching + histograma HSV, confianza calibrada)
    |
    v
CONSULTA AL CADASTRO (cache de referencias en memoria)
    |
    v
CLASIFICACION Y REGLAS DE APROBACION
    |
    v
RESULTADO MOBILE + HISTORICO + AUDITORIA + METRICAS
```

### Estructura del proyecto

```
MEX/
|-- backend/            API FastAPI, modelos, seguridad, servicios
|   |-- routers/       auth, parts, inspections, admin, health
|   |-- services/      vision_engine, image_validation, metrics, audit
|   |-- models.py      SQLAlchemy (User, Part, PartImage, Inspection, AuditLog, AIModelVersion)
|   |-- security.py    JWT, hashing PBKDF2, control de acceso por rol
|   `-- main.py        Aplicacion FastAPI y bootstrap
|-- frontend/           Aplicacion mobile (operador) y panel administrativo
|   |-- index.html     Interfaz del operador (captura por camara)
|   |-- admin.html     Panel de gestion
|   |-- app.js         Camara, resultados, historico, cola offline
|   `-- admin.js       Piezas, usuarios, inspecciones, metricas, modelos, auditoria
|-- scripts/            seed.py (datos iniciales) y smoke_test.py (pruebas end-to-end)
|-- monitoring/         Configuracion de Prometheus
|-- data/               Base de datos e imagenes (creada en tiempo de ejecucion)
|-- Dockerfile
|-- docker-compose.yml
`-- requirements.txt
```

### Motor de vision computacional

El motor inicial (`orb_matching`) combina:

- **ORB features**: deteccion de keypoints y descriptores de las piezas de referencia y de la captura, con matching de Hamming y ratio test de Lowe.
- **Histograma HSV**: similitud de distribucion de color y textura.
- **Confianza calibrada**: el puntaje bruto se convierte a probabilidad mediante una funcion logistica, devuelta como porcentaje de 0 a 100%.
- **Validacion de calidad**: deteccion de desenfoque (varianza del Laplaciano), iluminacion insuficiente o excesiva, reflejos y resolucion minima. Las capturas fuera de calidad generan divergencias y degradan el resultado.

Estados posibles del resultado:

| Estado | Significado |
|--------|-------------|
| GREEN  | Pieza identificada y aprobada conforme al criterio cadastrado |
| AMBER  | Confianza intermedia o divergencias no criticas: requiere revision humana |
| RED    | Divergencia critica o reprobacion conforme a la regla cadastrada |
| GRAY   | Pieza no identificada o no cadastrada (nunca se aprueba automaticamente) |

La arquitectura es modular: `backend/services/vision_engine.py` define la interfaz `identify(image, references)`. Nuevos motores (por ejemplo CNN de deteccion de defectos) se agregan registrando la clase en `ENGINES` sin reconstruir el sistema. Las versiones de motor se administran en el panel (tabla `ai_model_versions`).

### Metas de latencia

| Etapa | Meta |
|-------|------|
| Inferencia (servidor, p95) | inferior a 2000 ms |
| Flujo completo captura-resultado (p95, ambiente controlado) | inferior a 3000 ms |

Las metas se miden con pruebas reales y se monitorean por etapa (captura, upload, inferencia, total). La latencia de extremo a extremo depende de la red movil del operador y no se presenta como garantia absoluta. En pruebas locales de referencia la inferencia del motor ORB se ubica tipicamente entre 100 y 300 ms por imagen de 1600 px.

---

## Instalacion

### Requisitos

- Python 3.11 o superior (o Docker 24+ con Docker Compose 2.x)
- 2 GB de RAM disponibles para el backend
- Navegador mobile moderno con soporte de `getUserMedia` (Chrome/Safari actuales)

### Opcion A: instalacion local con Python

```bash
cd MEX

python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

pip install -r requirements.txt

python scripts/seed.py

uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Con el servidor activo:

- Interfaz del operador: `http://<host>:8000/`
- Panel administrativo: `http://<host>:8000/admin.html`
- Documentacion OpenAPI: `http://<host>:8000/docs`
- Health check: `http://<host>:8000/api/health`

Credenciales iniciales (cambiar en produccion con las variables de entorno):

- Usuario: `admin`
- Contrasena: `mex-admin-2024`

### Opcion B: instalacion con Docker

```bash
cd MEX

cp .env.example .env
# editar .env y definir un MEX_JWT_SECRET fuerte y contrasena de admin

docker compose up -d --build
```

El servicio queda disponible en el puerto 8000 y Prometheus en el 9090 (metricas en `/api/metrics/prometheus`).

### Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `MEX_JWT_SECRET` | valor de desarrollo | Secreto de firma JWT. Obligatorio cambiar en produccion |
| `MEX_ADMIN_USER` | `admin` | Usuario administrador inicial |
| `MEX_ADMIN_PASSWORD` | `mex-admin-2024` | Contrasena del administrador inicial |
| `MEX_DATABASE_URL` | SQLite local | URL SQLAlchemy (acepta PostgreSQL en produccion) |
| `MEX_JWT_EXPIRE_MINUTES` | `720` | Vigencia del token |
| `MEX_DEFAULT_APPROVAL_CONFIDENCE` | `0.80` | Confianza minima de aprobacion por defecto |
| `MEX_AMBER_THRESHOLD` | `0.55` | Piso del estado AMBER |
| `MEX_MIN_MATCH_THRESHOLD` | `0.35` | Puntaje minimo para considerar la pieza identificada |
| `MEX_MAX_UPLOAD_BYTES` | `8388608` | Limite de tamano de imagen |
| `MEX_RETENTION_DAYS` | `90` | Politica de retencion de capturas |

---

## Uso

### Operador (mobile)

1. Abrir la interfaz en el navegador del smartphone e ingresar credenciales.
2. Verificar el indicador de conexion en el encabezado.
3. Tocar `ESCANEAR PIEZA`: la camara ocupa la mayor parte de la pantalla.
4. Encuadrar la pieza y tocar `CAPTURAR`.
5. El resultado muestra fotografia, codigo, nombre, confianza, estado, divergencias, fecha e identificador de inspeccion.
6. El historico y la ultima inspeccion quedan visibles en la pantalla inicial.

Si el dispositivo pierde conexion, la captura se guarda en una cola local (localStorage) y se sincroniza automaticamente al reconectar, con la marca `synced_offline` en el registro.

### Supervisor / Administrador (panel)

- **Piezas**: cadastro con codigo unico, nombre, categoria, especificaciones, dimensiones, tolerancias, criterios de aprobacion y carga de imagenes de referencia multiples.
- **Inspecciones**: consulta por estado y revision humana de casos AMBER, RED y GRAY (aprobar o rechazar con nota).
- **Usuarios**: alta de operadores, supervisores y administradores; activacion/desactivacion.
- **Metricas**: total de inspecciones, tasa de aprobacion, pendientes de revision y latencia p50/p95/p99 por etapa contra las metas.
- **Modelos IA**: versiones del motor, activacion y parametros.
- **Auditoria**: registro de acciones por usuario y fecha.

---

## Seguridad y cumplimiento

- Autenticacion JWT con expiracion y hashing PBKDF2-SHA256 con salt individual.
- Control de acceso por rol: `operator` (inspeccion e historico), `supervisor` (piezas y revision), `admin` (usuarios, modelos, auditoria).
- Trilha de auditoria de todas las acciones relevantes con usuario, entidad y fecha.
- Limites de tamano de upload y validacion de contenido de imagen.
- Retencion de capturas configurable (default 90 dias) para alinearse con la LFPDPPP (Mexico).
- Versionamiento de piezas (cada actualizacion genera nueva version con historial) y de modelos de IA.
- Para produccion se recomienda: PostgreSQL con backup automatico, TLS terminado en reverse proxy, `MEX_JWT_SECRET` unico por ambiente y restringir `MEX_CORS_ORIGINS`.

## Monitoreo

- `GET /api/health`: estado del servicio y base de datos.
- `GET /api/metrics/prometheus`: metricas de latencia e inspecciones en formato Prometheus.
- `GET /api/admin/metrics`: metricas agregadas para el panel.
- Prometheus incluido en `docker-compose.yml` con scrape cada 15 s.

## Pruebas

```bash
cd MEX
python scripts/seed.py        # datos iniciales (piezas sinteticas de ejemplo)
python scripts/smoke_test.py  # suite end-to-end: auth, RBAC, cadastro, inspeccion, metricas
```

El smoke test valida login, permisos por rol, cadastro de piezas, upload de referencias, inspeccion de pieza conocida (esperado GREEN), pieza no identificada (esperado GRAY), revision, metricas p95, auditoria y exportacion Prometheus.

## Evolucion prevista

- Motor de deteccion de defectos con CNN (YOLO/EfficientNet) registrado como nueva version de modelo, sin cambio de interfaz.
- Cola asincrona (Redis/RQ o Celery) para picos de carga y reentrenamiento offline.
- Almacenamiento de objetos S3/MinIO para imagenes con ciclo de vida por politica de retencion.
- Despliegue multi-planta con particionamiento por `plant` por usuario.
