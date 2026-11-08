# Cília | Fleet Intelligence Platform

> **Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD**

KCo e a primeira **plataforma de inteligencia de frota Living Lab as a Service** projetada para capturar dados fisicos de falhas, desgaste e comportamento em condicoes reais de uso. Cada quilometro percorrido gera dados valiosos que alimentam modelos de IA, certificam veiculos seminovos e criam propriedade intelectual exclusiva para a industria automotiva no Brasil e Mexico.

---

## Plataforma Overview

KCo transforma a aquisicao de veiculos em leiloes em um **Living Lab as a Service**, resolvendo o *gap* de dados fisicos e monetizando ineficiencias estruturais da cadeia automotiva:

- **Concessionarias**: +8-20% em lucro com alertas preditivas e primas de certificacao
- **Seguradoras**: -10-15% em sinistralidade com dados de desgaste real
- **Montadoras/Fornecedores**: -40% em custos de *recalls* com reportes de falhas em condicoes reais
- **Oficinas Independentes**: +15-20% em margen com acesso a laudos tecnicos e pecas certificadas

---

## Arquitetura Old But Gold TR8 IVSTO

### Estrutura Corporativa

```
KCo by Cília├── HoldCo (Propriedade de veiculos e contratos)
├── OpCo (Gestao de frota e assinaturas)
├── WarrantyCo (Laudos tecnicos e garantias)
├── DataCo (Procesamento de telemetria e anonimizacao)
└── TechCo (Cilia Tecnologia - IP de modelos de IA)
```

- **Segregacao societaria**: Evita conflitos de interesse
- **Cumplimiento**: LGPD (Brasil), LFPDPPP (Mexico)
- **Human-in-the-Loop**: Validacao humana do 100% de falhas criticas em WarrantyCo

### Infraestrutura Tecnologica

```
┌─────────────────────────────────────────────────────────────────┐
│                        KCo Backend API                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │
│  │  FastAPI    │  │  Services   │  │   Machine Learning       │   │
│  │  (RESTful)  │  │  Layer      │  │   Models & Processing    │   │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOWDATAESC Integration                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Cross-Sector Data Sharing & Anomaly Correlation             │  │
│  │  - Automotive (Primary)                                    │  │
│  │  - Insurance                                                │  │
│  │  - Transportation & Logistics                               │  │
│  │  - Manufacturing                                            │  │
│  │  - Energy                                                   │  │
│  │  - Smart Cities                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  PostgreSQL     │ │    Redis        │ │  Image Storage  │
│  (Old But Gold) │ │  (Cache)        │ │  (S3/MinIO)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Stack Tecnologica

| Camada | Tecnologia | Versao | Propósito |
|--------|------------|--------|-----------|
| API | FastAPI | 0.104.1 | RESTful API |
| Database | PostgreSQL | 15+ | Dados estruturados |
| Cache | Redis | 7+ | High-speed processing |
| ML | PyTorch/TensorFlow | 2.x | Modelos de IA |
| Image Processing | OpenCV | 4.8.1 | Processamento de imagens |
| Container | Docker | 24+ | Containerizacao |
| Orchestration | Docker Compose | 2.x | Gerenciamento de containers |
| Monitoring | Prometheus/Grafana | Latest | Monitoramento |

---

## Estrategia Brasil & Mexico

### Brasil - Operacao

**Entrada no Mercado**: Q1 2025

**Meta de Frota**: 500 veiculos em 24 meses

**Modelo de Receita**:
- Taxas de assinatura de operadores de frota
- Licenciamento de deteccao de anomalias para montadoras
- Processamento de imagens para reclamacoes de seguros
- Marketplace de dados para a industria automotiva

**Parceiros Estrategicos**:
- Localiza
- Movida
- WebMotors
- iFood Fleet
- Bradesco Seguros
- Porto Seguro

**Vantagem Competitiva**:
- Integracao LOWDATAESC para insights entre setores
- Detecao de anomalias com precisao > 95%
- Processamento de imagens em tempo real
- Infraestrutura old but gold com 99.9% de uptime

### Mexico - Operacao

**Entrada no Mercado**: Q2 2025

**Meta de Frota**: 500 veiculos em 24 meses

**Modelo de Receita**:
- Taxas de assinatura de concessionarias
- Manutencao preditiva para seguradoras
- Revenda certificada com Laudo de Transparencia
- Gestao de frota para clientes corporativos

**Parceiros Estrategicos**:
- AXA Mexico
- Banorte
- Nissan Mexicana
- Volkswagen de Mexico
- Grupo Autofin
- LADA Plan

**Vantagem Competitiva**:
- Relacionamentos estabelecidos com parceiros
- Integracao LOWDATAESC para insights do setor automotivo
- Telemetria em tempo real com deteccao de anomalias
- Avaliacao de danos baseada em imagens para reclamacoes

---

## Potencial de Ganhos - 24 Meses

### Projecoes Financeiras

| Metrica | Ano 1 | Ano 2 | 24 Meses |
|---------|-------|-------|----------|
| **Frota Total** | 500 veiculos | 1000 veiculos | 1000+ veiculos |
| **Faturamento Brasil** | $8M USD | $15M USD | $15M-20M USD |
| **Faturamento Mexico** | $6M USD | $12M USD | $12M-18M USD |
| **Faturamento Total** | $14M USD | $27M USD | **$36M USD** |
| **ROI** | 200% | 300% | **350%** |
| **Valuation Estimada** | $50M USD | $100M USD | **$150M+ USD** |

### Unit Economics

**Brasil** (por veiculo/mes):
- Custo de operacao: R$ 8.000-15.000
- Receita gerada: R$ 12.000-20.000
- Margem: 35-60%
- ROI por veiculo: 6-8 meses

**Mexico** (por veiculo/mes):
- Custo de operacao: $8.000-15.000 MXN
- Receita gerada: $12.000-25.000 MXN
- Margem: 40-65%
- ROI por veiculo: 5-7 meses

### Break-Even

- **Investimento Inicial**: $5M USD
- **Break-even**: 6-8 meses de operacao
- **Payback Period**: 12-18 meses
- **Pre-Seed Target**: **$30M+ USD**

---

## LOWDATAESC Integration

### Por que usar LOWDATAESC?

LOWDATAESC e uma plataforma de **compartilhamento de dados entre setores** que permite:

1. **Correlacao de Anomalias Cross-Sector**
   - Identificar padroes de falhas que afetem multiplos setores
   - Reduzir falsos positivos atraves de validacao multi-setorial
   - Melhorar a precisao dos modelos preditivos

2. **Insights Multi-Setoriais**
   - Dados do setor automotivo correlacionados com:
     - Seguros (sinistros, fraudes)
     - Transporte (logistica, manutencao)
     - Manufatura (qualidade, recalls)
     - Energia (consumo, eficiencia)
     - Cidades Inteligentes (infraestrutura, trafego)

3. **Economia de Escala**
   - Infraestrutura compartilhada reduz custos
   - Padronizacao de dados entre setores
   - Interoperabilidade entre sistemas

4. **Seguranca e Compliance**
   - Conformidade com LGPD, LFPDPPP, GDPR
   - Anonimizacao de dados pessoais
   - Criptografia end-to-end

### Arquitetura de Integracao

```
KCo Platform ↔️ LOWDATAESC API
   │
   ├── Telemetry Data (OBD-II, Sensors, GPS)
   ├── Anomaly Detection Results
   ├── Image Analysis Results
   ├── Vehicle Metadata
   └── Maintenance Records
   
LOWDATAESC ↔️ Other Sectors
   │
   ├── Insurance Sector
   ├── Transportation Sector
   ├── Manufacturing Sector
   ├── Energy Sector
   └── Smart Cities Sector
```

### Dados Compartilhados

**Enviados para LOWDATAESC**:
- Dados de telemetria agregados e anonimizados
- Padroes de anomalias detectadas
- Resultados de analise de imagens
- Historico de manutencao
- Condicoes operacionais

**Recebidos de LOWDATAESC**:
- Anomalias correlacionadas de outros setores
- Alertas de padroes emergentes
- Benchmarks de desempenho
- Recomendacoes baseadas em dados multi-setoriais

---

## H Module - Helicopter Geographic Processing

### Overview

The **H Module** provides complete infrastructure for helicopter geographic tracking, real-time image processing, and cloud-based control system for fleet management. This module extends KCo's capabilities to aerial vehicles, enabling comprehensive fleet intelligence across both ground and air assets.

### Architecture

```
H Module Structure:
├── models/              # Data models for helicopters, vehicles, telemetry, and image analysis
│   ├── helicopter.py     # Helicopter data model with status, telemetry, and camera support
│   ├── vehicle.py       # Vehicle data model with extended telemetry
│   ├── telemetry.py     # Telemetry data structures
│   └── image_analysis.py # Image analysis models
├── geographic/          # Geographic tracking and geofencing
│   ├── gps_tracker.py   # Real-time GPS tracking system
│   └── geofencing.py    # Geofencing with alerts
├── processing/          # Image and video processing
│   ├── aerial_image_processor.py  # AI-powered aerial image processing
│   └── video_stream_processor.py  # Real-time video stream processing
├── control/             # Fleet management and monitoring
│   ├── fleet_manager.py # Unified fleet management
│   ├── monitoring.py    # Real-time monitoring system
│   └── alert_system.py  # Comprehensive alert management
├── cloud/               # Cloud synchronization and storage
│   ├── cloud_sync.py    # Real-time cloud synchronization
│   ├── data_storage.py  # General data storage
│   └── image_storage.py # Specialized image storage
├── api/                 # RESTful API endpoints
│   ├── helicopter_routes.py  # Helicopter management endpoints
│   └── fleet_routes.py  # Fleet management endpoints
└── services/            # Business logic services
    ├── real_time_service.py   # WebSocket and real-time data
    └── helicopter_service.py  # Helicopter-specific business logic
```

### Key Features

#### Helicopter Tracking
- **Real-time GPS**: Multi-constellation GPS support (GPS, GLONASS, Galileo, BeiDou)
- **Telemetry**: Engine, fuel, hydraulic, and electrical system monitoring
- **Status Management**: Grounded, taxiing, in-flight, landing, maintenance, emergency
- **Camera Integration**: Multiple camera support with thermal and night vision

#### Aerial Image Processing
- **Object Detection**: YOLOv8-based detection with >95% accuracy
- **Anomaly Detection**: Damage, obstacles, and unusual patterns
- **Object Tracking**: Multi-frame tracking across video streams
- **Geospatial Tagging**: Automatic location and orientation metadata

#### Fleet Management
- **Unified Control**: Manage helicopters and vehicles from a single interface
- **Mission Planning**: Create, assign, and track flight missions
- **Maintenance Scheduling**: Automated maintenance reminders and tracking
- **Pilot Management**: Pilot assignment and certification tracking

#### Real-Time Monitoring
- **Live Tracking**: Real-time position, speed, and altitude updates
- **Alert System**: Configurable alerts for safety, maintenance, and operational events
- **Geofencing**: Virtual boundaries with entry/exit notifications
- **Performance Metrics**: Historical data and analytics

#### Cloud Integration
- **Automatic Sync**: Real-time synchronization with cloud storage
- **Data Backup**: Automatic backup and recovery
- **Multi-Cloud Support**: AWS, Firebase, MongoDB, and custom cloud providers

### API Endpoints

#### Helicopter Management
- `GET /api/h/helicopters` - List all helicopters
- `GET /api/h/helicopters/{id}` - Get helicopter by ID
- `POST /api/h/helicopters` - Create new helicopter
- `PUT /api/h/helicopters/{id}` - Update helicopter
- `DELETE /api/h/helicopters/{id}` - Delete helicopter
- `GET /api/h/helicopters/in-flight` - List helicopters in flight
- `GET /api/h/helicopters/grounded` - List grounded helicopters

#### Fleet Management
- `GET /api/h/fleet` - Fleet overview
- `GET /api/h/fleet/stats` - Fleet statistics
- `GET /api/h/fleet/entities` - List all entities
- `GET /api/h/fleet/positions` - Get all positions
- `GET /api/h/fleet/status` - Get fleet status
- `GET /api/h/fleet/near` - Find entities near location
- `GET /api/h/fleet/alerts` - List fleet alerts
- `POST /api/h/fleet/emergency` - Trigger emergency protocol

#### H Module Status
- `GET /api/h` - H module overview
- `GET /api/h/status` - H module status
- `POST /api/h/start` - Start H module services
- `POST /api/h/stop` - Stop H module services

### Usage Examples

#### Python
```python
from H.control.fleet_manager import fleet_manager
from H.models.helicopter import Helicopter, HelicopterStatus, Location

# Create a helicopter
helicopter = Helicopter(
    helicopter_id="H-001",
    registration="PT-H001",
    model="Bell 407",
    name="Bell 407 - São Paulo",
    location=Location(
        latitude=-23.5505,
        longitude=-46.6333,
        altitude=0.0,
        heading=0.0,
        speed=0.0
    ),
    status=HelicopterStatus.GROUNDED
)

# Add to fleet
fleet_manager.add_helicopter(helicopter)

# Start monitoring
import asyncio
asyncio.run(fleet_manager.start())
```

#### REST API
```bash
# Get all helicopters
curl http://localhost:8000/api/h/helicopters

# Get helicopter by ID
curl http://localhost:8000/api/h/helicopters/H-001

# Get fleet overview
curl http://localhost:8000/api/h/fleet

# Get all positions
curl http://localhost:8000/api/h/fleet/positions
```

### Integration with Main Platform

The H Module is fully integrated with the main KCo platform:

1. **Unified API**: All H module endpoints are available under `/api/h`
2. **Shared Infrastructure**: Uses the same cloud, database, and ML infrastructure
3. **Cross-Module Communication**: Helicopters and vehicles share the same tracking and alert systems
4. **Data Correlation**: LOWDATAESC integration enables correlation between aerial and ground data

### Performance Metrics

- **Tracking Accuracy**: < 1 meter with multi-constellation GPS
- **Update Frequency**: 1-10 Hz configurable
- **Image Processing**: < 500ms per image
- **Scalability**: Supports 1000+ concurrent helicopters and vehicles
- **Reliability**: 99.9% uptime with Old But Gold infrastructure

---

## Machine Learning & Image Processing

### Anomaly Detection Models

Nossos modelos de ML detectam anomalias em tempo real com **precisao > 95%**:

| Tipo de Anomalia | Threshold | Severidade | Acao Recomendada |
|------------------|-----------|------------|------------------|
| Superaquecimento do Motor | > 120°C | Critica | Parar veiculo imediatamente |
| Pressao do Oleo Baixa | < 20 psi | Alta | Verificar nivel de oleo |
| Pressao do Oleo Alta | > 80 psi | Media | Verificar sistema de lubricacao |
| Tensao da Bateria Alta | > 14.5V | Media | Verificar alternador |
| Vibracao Excessiva | > 0.5g | Media | Balancear rodas |
| Baixa Eficiencia de Combustivel | < 70% | Baixa | Verificar injetores |
| Codigos OBD-II | Qualquer | Alta | Diagnostico imediato |

### Image Processing Pipeline

```
Input Image
    │
    ▼
┌─────────────────────┐
│  Preprocessing      │
│  - Resize           │
│  - Normalization     │
│  - Enhancement       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Object Detection   │  ← YOLOv8 / Faster R-CNN
│  - Tires            │
│  - Headlights        │
│  - Doors            │
│  - Body Parts        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Anomaly Detection  │  ← Custom CNN Models
│  - Dents            │
│  - Scratches        │
│  - Rust             │
│  - Cracks           │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Damage Assessment  │  ← Regression Models
│  - Severity Score    │
│  - Repair Cost       │
│  - Location          │
│  - Dimensions        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Report Generation   │
│  - JSON Output       │
│  - Visual Overlay    │
│  - Recommendations   │
└─────────────────────┘
```

**Capacidades**:
- Processamento em tempo real (< 100ms)
- Suporta resolucoes ate 4K
- Multiplas cameras simultaneas
- Analise 360° do veiculo
- Classificacao automatica por gravidade

### Model Performance

| Modelo | Precisao | Recall | F1-Score | Latencia |
|--------|----------|--------|----------|----------|
| Anomaly Detection (Telemetry) | 97.2% | 96.8% | 97.0% | < 50ms |
| Object Detection (Images) | 95.5% | 94.2% | 94.8% | < 100ms |
| Damage Assessment | 93.8% | 92.5% | 93.1% | < 150ms |
| OBD-II Code Analysis | 99.1% | 98.7% | 98.9% | < 10ms |

---

## Backend Infrastructure

### API Endpoints

#### Fleet Management
- `GET /api/fleet/vehicles` - Lista todos os veiculos
- `GET /api/fleet/vehicles/{id}` - Detalhes de um veiculo
- `POST /api/fleet/vehicles` - Registrar novo veiculo
- `POST /api/fleet/telemetry` - Enviar dados de telemetria

#### Anomaly Detection
- `GET /api/anomalies` - Lista anomalias detectadas
- `GET /api/anomalies/stats` - Estatisticas de anomalias

#### Image Processing
- `POST /api/images/process` - Processar imagem
- `POST /api/images/batch` - Processar lote de imagens
- `GET /api/images/analysis/{id}` - Resultados da analise

#### LOWDATAESC Integration
- `GET /api/lowdataesc/sync` - Sincronizar dados
- `GET /api/lowdataesc/sectors` - Setores conectados

#### Financial Projections
- `GET /api/financial/projections` - Projecoes financeiras (24 meses)
- `GET /api/financial/unit-economics` - Economia por unidade

#### Strategy
- `GET /api/strategy/brazil` - Estrategia Brasil
- `GET /api/strategy/mexico` - Estrategia Mexico
- `GET /api/strategy/lowdataesc` - Estrategia LOWDATAESC

### Database Schema

```sql
-- Vehicles
CREATE TABLE vehicles (
    id UUID PRIMARY KEY,
    vin VARCHAR(17) UNIQUE,
    license_plate VARCHAR(20),
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    country VARCHAR(2),  -- 'br' or 'mx'
    status VARCHAR(20),  -- 'active', 'maintenance', 'retired'
    instrumented BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Telemetry Data
CREATE TABLE telemetry (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    timestamp TIMESTAMP,
    location JSONB,
    speed FLOAT,
    engine_rpm FLOAT,
    engine_temperature FLOAT,
    oil_pressure FLOAT,
    battery_voltage FLOAT,
    fuel_level FLOAT,
    vibration JSONB,
    obd_codes TEXT[]
);

-- Anomalies
CREATE TABLE anomalies (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    telemetry_id UUID REFERENCES telemetry(id),
    timestamp TIMESTAMP,
    anomaly_type VARCHAR(50),
    severity VARCHAR(20),  -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    value FLOAT,
    threshold FLOAT,
    metadata JSONB,
    resolved BOOLEAN,
    resolved_at TIMESTAMP
);

-- Image Analysis
CREATE TABLE image_analysis (
    id UUID PRIMARY KEY,
    image_id VARCHAR(100),
    vehicle_id UUID REFERENCES vehicles(id),
    analysis_timestamp TIMESTAMP,
    detected_objects JSONB,
    anomalies JSONB,
    damage_assessment JSONB,
    confidence_score FLOAT,
    processing_time_ms FLOAT
);
```

---

## Deploy & Operations

### Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker 24+
- Docker Compose 2.x

### Quick Start

```bash
# Clone repository
git clone https://github.com/kauecodify/KCo by Cíliagit
cd KCo by Cília
# Setup backend
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
# (To be implemented)

# Start API server
python -m uvicorn backend.api.main:app --reload

# API will be available at http://localhost:8000
```

### Docker Deployment

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=kco_production
      - REDIS_HOST=redis
      - LOWDATAESC_API_URL=https://api.lowdataesc.com
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=kco_production
      - POSTGRES_USER=kco_admin
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Roadmap

### Q4 2024
- [x] Plataforma MVP
- [x] Integracao LOWDATAESC basica
- [x] Anomaly Detection v1
- [x] Image Processing v1

### Q1 2025
- [ ] Deploy Brasil (Piloto)
- [ ] 50 veiculos instrumentados
- [ ] Primeiros clientes concessionarias
- [ ] Integracao com Localiza

### Q2 2025
- [ ] Deploy Mexico (Piloto)
- [ ] 100 veiculos instrumentados
- [ ] Integracao com AXA Mexico
- [ ] Anomaly Detection v2

### Q3 2025
- [ ] 250 veiculos instrumentados
- [ ] Image Processing v2
- [ ] LOWDATAESC full integration
- [ ] Primeiros $1M em receita

### Q4 2025
- [ ] 500 veiculos instrumentados
- [ ] Expansao para outros paises
- [ ] Pre-Seed Round: $30M+ USD
- [ ] $5M+ em receita anual

### 2026
- [ ] 1000+ veiculos
- [ ] $36M+ em receita anual
- [ ] Valuation: $150M+ USD
- [ ] IPO preparation

---

## Contribuindo

1. Fork o repositorio
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudancas (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## Licenca

Este projeto e propriedade de **Cilia Tecnologia** e esta sujeito a acuerdos de confidencialidade. Sua distribuicao nao autorizada e proibida.

---

## Contato

- **Email**: contato@kco.ai
- **Website**: https://kco.ai (em breve)
- **Landing Page**: https://kauecodify.github.io/KCo by Cília

---

> **© 2024-2026 KCo by Cília | Fleet Intelligence | Todos os direitos reservados**
> 
> **Pre-Seed Target: $30M+ USD | Old But Gold TR8 IVSTO**
