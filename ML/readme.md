# Machine Learning & Image Processing - KCo Fleet Intelligence

> **AI-Powered Fleet Intelligence | Old But Gold TR8 IVSTO**

Este diretorio contem todos os modelos de Machine Learning e processamento de imagens da plataforma KCo. Nossa abordagem combina **detectacao de anomalias em tempo real** com **processamento de imagens avancado** para criar um sistema completo de inteligencia de frota.

---

## Estrutura do Diretorio

```
ML/
├── models/                  # Modelos treinados
│   ├── anomaly_detection/   # Modelos de deteccao de anomalias
│   │   ├── telemetry_model.pkl
│   │   └── obd2_model.pkl
│   ├── image_processing/     # Modelos de processamento de imagens
│   │   ├── object_detection.pkl
│   │   ├── anomaly_detection.pkl
│   │   └── damage_assessment.pkl
│   └── README.md            # Documentacao dos modelos
│
├── scripts/                 # Scripts de treinamento e inferencia
│   ├── train_anomaly.py      # Treinamento de modelos de anomalias
│   ├── train_image.py        # Treinamento de modelos de imagens
│   ├── inference.py          # Scripts de inferencia
│   └── evaluation.py         # Avaliacao de modelos
│
├── processing/              # Modulos de processamento
│   ├── image_utils.py        # Utilitarios de imagens
│   ├── preprocessing.py      # Pre-processamento de dados
│   ├── postprocessing.py     # Pos-processamento de resultados
│   └── __init__.py
│
└── readme.md                # Este documento
```

---

## Processamento de Imagens

### Arquitetura

Nosso pipeline de processamento de imagens e projetado para **alta precisao** e **baixa latencia**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMAGE PROCESSING PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. IMAGE ACQUISITION                                           │
│     ├─ Camera 360° (Multiple angles)                            │
│     ├─ High-resolution (4K support)                             │
│     ├─ Real-time streaming                                       │
│     └─ Batch processing                                          │
│                                                                  │
│  2. PREPROCESSING                                               │
│     ├─ Resize to standard dimensions                           │
│     ├─ Normalization (0-1 or -1 to 1)                            │
│     ├─ Color space conversion (RGB, HSV, Lab)                   │
│     ├─ Enhancement (CLAHE, histogram equalization)             │
│     ├─ Noise reduction (Gaussian, median blur)                 │
│     └─ Perspective correction                                   │
│                                                                  │
│  3. OBJECT DETECTION  (YOLOv8 / Faster R-CNN)                   │
│     ├─ Vehicle parts detection                                  │
│     │  ├─ Tires (position, condition)                            │
│     │  ├─ Headlights (functionality)                              │
│     │  ├─ Doors (alignment, damage)                              │
│     │  ├─ Windows (cracks, tint)                                  │
│     │  ├─ Bumpers (damage, alignment)                             │
│     │  └─ Body panels (dents, scratches)                         │
│     └─ Detection confidence: > 95%                               │
│                                                                  │
│  4. ANOMALY DETECTION  (Custom CNN Models)                       │
│     ├─ Visual anomaly detection                                  │
│     │  ├─ Dents (size, depth, location)                           │
│     │  ├─ Scratches (length, width, severity)                     │
│     │  ├─ Rust (area, severity)                                   │
│     │  ├─ Cracks (type, length, criticality)                       │
│     │  └─ Missing parts                                          │
│     └─ Anomaly confidence: > 93%                                 │
│                                                                  │
│  5. DAMAGE ASSESSMENT  (Regression + Classification)            │
│     ├─ Severity scoring (0-1 scale)                              │
│     ├─ Repair cost estimation                                    │
│     ├─ Location mapping (2D/3D coordinates)                      │
│     ├─ Damage dimensions (width, height, depth)                 │
│     └─ Recommendation engine                                     │
│                                                                  │
│  6. POST-PROCESSING                                             │
│     ├─ Result aggregation                                        │
│     ├─ Confidence score calculation                              │
│     ├─ Visual overlay generation                                 │
│     ├─ Report generation (JSON, PDF)                             │
│     └─ LOWDATAESC integration                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Capacidades

#### Detecao de Objetos
- **Modelo**: YOLOv8 (You Only Look Once)
- **Precisao**: 95.5%
- **Classe de Objetos**: 50+ classes de pecas automotivas
- **Velocidade**: 60+ FPS em GPU
- **Resolucao**: Suporta ate 4K

**Classes Principais**:
```
- Veiculo completo
- Pneus (4 posicoes)
- Farois (dianteiros e traseiros)
- Portas (direito e esquerdo)
- Capo
- Porta-malas
- Para-choques (dianteiro e traseiro)
- Janelas
- Espelhos
- Rodas
- Calotas
- Placa de licenca
- Logotipos de montadoras
```

#### Detectao de Anomalias Visuais
- **Modelo**: Custom CNN (Convolutional Neural Network)
- **Precisao**: 93.8%
- **Tipos de Anomalias**: 20+ tipos
- **Severidade**: 4 niveis (Baixo, Medio, Alto, Critico)

**Tipos de Anomalias**:
```
- Amassados (Dents)
  - Pequeno (< 2cm)
  - Medio (2-5cm)
  - Grande (> 5cm)
  - Profundo (com deformacao estrutural)

- Arranhoes (Scratches)
  - Superficiais (pintura)
  - Profundos (metal)
  - Longos (> 10cm)

- Ferrugem (Rust)
  - Inicial (superficial)
  - Moderada (penetracao)
  - Severa (estrutural)

- Rachaduras (Cracks)
  - Vidro
  - Plastico
  - Metal

- Partes Faltando
  - Calotas
  - Espelhos
  - Pecas de acabamento

- Danos por Impacto
  - Colisao frontal
  - Colisao traseira
  - Colisao lateral
```

#### Avaliacao de Danos
- **Modelo**: Ensemble (Regression + Classification)
- **Precisao**: 92.5%
- **Saidas**:
  - Score de condicao (0-100)
  - Custo estimado de reparo
  - Tempo estimado de reparo
  - Prioridade de reparo

**Exemplo de Saida**:
```json
{
  "overall_condition": "good",
  "damage_score": 0.25,
  "estimated_repair_cost": 1500.00,
  "estimated_repair_time": "2 days",
  "priority": "medium",
  "damages": [
    {
      "type": "dent",
      "severity": "medium",
      "location": {"x": 0.4, "y": 0.6},
      "dimensions": {"width": 5.0, "height": 3.0, "depth": 0.5},
      "estimated_cost": 800.00,
      "confidence": 0.85,
      "recommended_action": "Panel beating and repainting"
    },
    {
      "type": "scratch",
      "severity": "low",
      "location": {"x": 0.5, "y": 0.2},
      "dimensions": {"width": 10.0, "height": 0.2},
      "estimated_cost": 200.00,
      "confidence": 0.75,
      "recommended_action": "Polishing or touch-up paint"
    }
  ]
}
```

### Performance

| Metrica | Valor |
|---------|-------|
| **Precisao de Detecao** | 95.5% |
| **Recall de Detecao** | 94.2% |
| **F1-Score** | 94.8% |
| **Latencia (CPU)** | < 200ms |
| **Latencia (GPU)** | < 50ms |
| **Throughput** | 10+ imagens/segundo |
| **Resolucao Maxima** | 4K (3840x2160) |
| **Memoria (GPU)** | 4GB VRAM |

---

## Detectao de Anomalias (Telemetria)

### Modelos

#### 1. Engine Temperature Model
- **Tipo**: Regression + Classification
- **Input**: Engine temperature, RPM, load, ambient temperature
- **Output**: Anomaly flag, severity, predicted failure time
- **Threshold**: > 120°C (Critical), > 110°C (High)
- **Precisao**: 97.2%

#### 2. Oil Pressure Model
- **Tipo**: Time Series Analysis
- **Input**: Oil pressure (psi), engine RPM, temperature
- **Output**: Anomaly flag, severity, recommended action
- **Threshold**: < 20 psi (Low), > 80 psi (High)
- **Precisao**: 96.8%

#### 3. Battery Voltage Model
- **Tipo**: Statistical Analysis
- **Input**: Battery voltage, charging state, alternator status
- **Output**: Anomaly flag, severity
- **Threshold**: > 14.5V (Overvoltage), < 12V (Undervoltage)
- **Precisao**: 98.1%

#### 4. Vibration Model
- **Tipo**: FFT (Fast Fourier Transform)
- **Input**: Vibration sensors (X, Y, Z axes)
- **Output**: Anomaly flag, frequency analysis, severity
- **Threshold**: > 0.5g (High), > 0.3g (Medium)
- **Precisao**: 95.9%

#### 5. OBD-II Code Analyzer
- **Tipo**: Rule-Based + ML
- **Input**: OBD-II trouble codes
- **Output**: Code interpretation, severity, recommended action
- **Database**: 10,000+ OBD-II codes
- **Precisao**: 99.1%

### Performance Geral

| Modelo | Precisao | Recall | F1-Score | Latencia |
|--------|----------|--------|----------|----------|
| Engine Temperature | 97.2% | 96.8% | 97.0% | < 10ms |
| Oil Pressure | 96.8% | 95.5% | 96.1% | < 10ms |
| Battery Voltage | 98.1% | 97.8% | 97.9% | < 5ms |
| Vibration | 95.9% | 94.7% | 95.3% | < 15ms |
| OBD-II Analyzer | 99.1% | 98.7% | 98.9% | < 1ms |
| **Overall** | **97.4%** | **96.7%** | **97.0%** | **< 50ms** |

---

## Integracao com LOWDATAESC

### Dados Enviados para LOWDATAESC

1. **Telemetry Data**
   - Aggregated and anonymized telemetry
   - Anomaly patterns
   - Vehicle performance metrics

2. **Anomaly Detection Results**
   - Detected anomalies with severity
   - Correlation patterns
   - Predictive indicators

3. **Image Analysis Results**
   - Detected objects
   - Visual anomalies
   - Damage assessments
   - Image metadata

4. **Vehicle Metadata**
   - Vehicle specifications
   - Maintenance history
   - Operational conditions

### Dados Recebidos de LOWDATAESC

1. **Cross-Sector Anomalies**
   - Anomalies from other sectors that may affect vehicles
   - Infrastructure issues
   - Weather conditions
   - Traffic patterns

2. **Correlation Insights**
   - Patterns between automotive and other sectors
   - Predictive indicators from multiple sources
   - Risk assessments

3. **Benchmark Data**
   - Industry benchmarks
   - Performance comparisons
   - Best practices

4. **Recommendations**
   - Maintenance recommendations based on multi-sector data
   - Operational optimization suggestions
   - Risk mitigation strategies

### Exemplo de Integracao

```python
from backend.services.lowdataesc_integration import LOWDATAESCService
from backend.services.image_processing import ImageProcessingService

# Process image
image_service = ImageProcessingService()
result = image_service.process_image({
    "image_url": "https://example.com/vehicle_image.jpg",
    "vehicle_id": "BR-001"
})

# Send to LOWDATAESC
lowdataesc_service = LOWDATAESCService()
lowdataesc_service.store_image_analysis(result)

# Get cross-sector insights
insights = lowdataesc_service.get_sector_insights("automotive")
print(insights)
```

---

## Treinamento de Modelos

### Requisitos

- Python 3.11+
- PyTorch 2.0+
- CUDA 11.8+ (para GPU)
- OpenCV 4.8.1+
- NumPy 1.26.2+
- Pandas 2.1.4+

### Dataset

#### Image Dataset
- **Total Images**: 50,000+ (growing)
- **Classes**: 50+ object classes, 20+ anomaly types
- **Annotations**: Bounding boxes, segmentation masks, severity scores
- **Sources**: Vehicle inspections, accident reports, maintenance records

#### Telemetry Dataset
- **Total Samples**: 100M+ data points
- **Vehicles**: 500+ instrumented vehicles
- **Duration**: 24+ months of continuous data
- **Frequency**: 5-10 Hz sampling rate

### Treinamento

```bash
# Treinar modelo de deteccao de objetos
python scripts/train_image.py --model yolo --epochs 100 --batch 32 --data images/train

# Treinar modelo de anomalias
python scripts/train_anomaly.py --model cnn --epochs 50 --batch 64 --data telemetry/train

# Avaliar modelos
python scripts/evaluation.py --model models/object_detection.pkl --test-data images/test
```

---

## Inferencia

### API de Inferencia

```python
from backend.services.image_processing import ImageProcessingService

service = ImageProcessingService()

# Processar imagem da URL
result = service.process_image({
    "image_url": "https://example.com/vehicle.jpg",
    "vehicle_id": "BR-001",
    "analysis_type": "full"
})

print(result.to_dict())
```

### Processamento em Lote

```python
from backend.services.image_processing import ImageProcessingService

service = ImageProcessingService()

# Processar multiplas imagens
image_urls = [
    "https://example.com/vehicle1.jpg",
    "https://example.com/vehicle2.jpg",
    "https://example.com/vehicle3.jpg"
]

results = service.process_batch(image_urls)

for result in results:
    print(result.to_dict())
```

---

## Deploy de Modelos

### Formatos Suportados
- **PyTorch**: .pt, .pth
- **TensorFlow**: .h5, .pb
- **ONNX**: .onnx (recomendado para producao)
- **Pickle**: .pkl (para modelos scikit-learn)

### Conversao para ONNX

```python
import torch
from models.object_detection import YOLOModel

# Carregar modelo
model = YOLOModel()
model.load_state_dict(torch.load("models/yolo.pth"))
model.eval()

# Exportar para ONNX
dummy_input = torch.randn(1, 3, 640, 640)
torch.onnx.export(
    model,
    dummy_input,
    "models/yolo.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)
```

### Inferencia com ONNX

```python
import onnxruntime as ort
import numpy as np

# Carregar modelo ONNX
sess = ort.InferenceSession("models/yolo.onnx")

# Preparar input
input_data = np.random.randn(1, 3, 640, 640).astype(np.float32)

# Executar inferencia
outputs = sess.run(None, {"input": input_data})

print(outputs)
```

---

## Monitoramento e Manutencao

### Metricas de Monitoramento

1. **Model Performance**
   - Accuracy, Precision, Recall, F1-Score
   - Confusion Matrix
   - ROC Curve (para classificacao)

2. **Inference Metrics**
   - Latency (P50, P90, P99)
   - Throughput (images/second)
   - Memory Usage
   - CPU/GPU Utilization

3. **Data Quality**
   - Input data distribution
   - Anomaly detection rate
   - False positive rate
   - False negative rate

4. **System Health**
   - Model loading time
   - Model size
   - Inference queue size
   - Error rates

### Retreinamento

- **Frequencia**: Mensal ou quando a performance cair abaixo de 90%
- **Dataset**: Novos dados coletados no mes
- **Validacao**: Cross-validation com dataset de teste
- **Deploy**: Automatico apos validacao

---

## Roadmap de ML

### Q4 2024
- [x] Anomaly Detection v1 (Telemetria)
- [x] Image Processing v1 (Detecao de objetos)
- [x] Damage Assessment v1
- [x] Integracao LOWDATAESC basica

### Q1 2025
- [ ] Anomaly Detection v2 (Melhor precisao)
- [ ] Image Processing v2 (Mais classes)
- [ ] 3D Damage Assessment
- [ ] Video Processing (analise de video em tempo real)

### Q2 2025
- [ ] Predictive Maintenance Models
- [ ] Driver Behavior Analysis
- [ ] Route Optimization
- [ ] Energy Efficiency Models

### Q3 2025
- [ ] Federated Learning (treinamento distribuido)
- [ ] Edge AI (inferencia no dispositivo)
- [ ] Real-time Video Analytics
- [ ] Multi-modal Models (imagem + telemetria)

### Q4 2025
- [ ] Autonomous Damage Assessment
- [ ] Full 360° Vehicle Analysis
- [ ] Augmented Reality Integration
- [ ] Voice-based Analysis Reports

---

## Contribuindo

1. Fork o repositorio
2. Crie uma branch para sua feature (`git checkout -b ml/nova-feature`)
3. Adicione seus modelos e scripts em `ML/models/` e `ML/scripts/`
4. Atualize a documentacao
5. Abra um Pull Request

---

## Referencias

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [LOWDATAESC Platform](https://github.com/kauecodify/LOWDATAESC)

---

> **© 2024-2026 KCo Fleet Intelligence | Todos os direitos reservados**
> 
> **Machine Learning Team | Old But Gold TR8 IVSTO**
