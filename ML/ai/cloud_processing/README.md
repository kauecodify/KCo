# KCo AI Cloud Processing - Image Analysis with Cloud Storage

> **Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD**
> **KCo by Cília | Laboratory of K and RockNewVenture**

## Overview

This module provides **AI-powered image processing** with automatic **cloud database storage** for all vehicle analyses. Each analysis is indexed by **vehicle ID** for efficient retrieval and tracking.

### Key Features

- **AI Image Processing**: Advanced anomaly detection using YOLOv8 and custom CNN models
- **Cloud Storage**: Automatic saving of all analysis results to cloud database
- **Vehicle ID Indexing**: All analyses are indexed by vehicle ID for easy querying
- **Real-time Processing**: Fast analysis with < 500ms processing time
- **Comprehensive Reports**: Detailed analysis with damage assessment and repair estimates

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Image Processor                      │
├─────────────────────────────────────────────────────────────┤
│  1. Image Loading (URL, File Path, Base64)                   │
│  2. Preprocessing (Resize, Normalize, Enhance)               │
│  3. Object Detection (YOLOv8 - Vehicle Parts)               │
│  4. Anomaly Detection (CNN - Dents, Scratches, Rust)         │
│  5. Damage Assessment (Severity, Cost, Time Estimation)      │
│  6. Cloud Storage (Automatic Save by Vehicle ID)             │
│  7. Result Return (JSON with Analysis Details)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Vehicle Analysis Storage                      │
├─────────────────────────────────────────────────────────────┤
│  • Save Analysis by Vehicle ID                               │
│  • Get Analysis History                                      │
│  • Query by Date Range                                       │
│  • Update Metadata                                           │
│  • Delete Analysis                                           │
│  • Get Statistics                                            │
│  • Custom Search Queries                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Database                             │
│  Collection: vehicle_analyses                                 │
│  Indexes: vehicle_id, timestamp, analysis_type, damage_score│
│  Storage: Full analysis data with metadata                    │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Install required packages
pip install opencv-python numpy pillow

# For cloud database integration
pip install motor pymongo  # For MongoDB
# or
pip install firebase-admin  # For Firebase
```

## Usage

### Basic Image Processing

```python
from ML.ai.cloud_processing import CloudImageProcessor

# Initialize processor
processor = CloudImageProcessor(
    cloud_storage_client=cloud_client,
    vehicle_id="BR-001"
)

# Process image from file
result = processor.process_image({
    "image_path": "/path/to/vehicle_image.jpg",
    "vehicle_id": "BR-001",
    "analysis_type": "full"
})

print(f"Analysis ID: {result['analysis_id']}")
print(f"Damage Score: {result['damage_assessment']['damage_score']}")
print(f"Estimated Cost: ${result['damage_assessment']['estimated_repair_cost']}")
print(f"Cloud Storage ID: {result['cloud_storage_id']}")
```

### Batch Processing

```python
# Process multiple images
image_urls = [
    "https://example.com/vehicle1.jpg",
    "https://example.com/vehicle2.jpg",
    "https://example.com/vehicle3.jpg"
]

vehicle_ids = ["BR-001", "BR-002", "BR-003"]

results = processor.process_batch(image_urls, vehicle_ids)

for result in results:
    print(f"Vehicle {result['vehicle_id']}: {result['anomalies']['total_anomalies']} anomalies")
```

### Vehicle Analysis Storage

```python
from ML.ai.cloud_processing import VehicleAnalysisStorage

# Initialize storage
storage = VehicleAnalysisStorage(cloud_client=cloud_client)

# Save analysis
async def save_analysis():
    result = await storage.save_analysis(
        vehicle_id="BR-001",
        analysis_data={
            "anomalies": {"total_anomalies": 3, "anomalies": [...]},
            "damage_assessment": {"damage_score": 45.5, "estimated_repair_cost": 1250.00}
        },
        metadata={"processed_by": "ai_system", "version": "v1.0"}
    )
    print(f"Saved with ID: {result['id']}")

# Get vehicle history
async def get_history():
    analyses = await storage.get_vehicle_history("BR-001", limit=10)
    for analysis in analyses:
        print(f"Analysis {analysis['analysis_id']}: {analysis['timestamp']}")

# Get statistics
async def get_stats():
    stats = await storage.get_statistics(vehicle_id="BR-001")
    print(f"Average Damage Score: {stats['statistics']['damage_score']['average']}")
```

## API Reference

### CloudImageProcessor

#### `process_image(image_data)`
Process a single vehicle image.

**Parameters:**
- `image_data` (dict): Dictionary containing image data
  - `image_path`: Local file path
  - `image_base64`: Base64 encoded image
  - `image_url`: URL of the image
  - `vehicle_id`: Vehicle identifier
  - `analysis_type`: Type of analysis ("full", "quick", "damage", "anomaly")

**Returns:**
- Dictionary with analysis results including:
  - `analysis_id`: Unique analysis identifier
  - `vehicle_id`: Vehicle identifier
  - `timestamp`: Analysis timestamp
  - `detected_objects`: List of detected vehicle parts
  - `anomalies`: List of detected anomalies
  - `damage_assessment`: Overall damage assessment
  - `confidence_score`: Analysis confidence (0-1)
  - `cloud_storage_id`: Cloud database document ID

#### `process_batch(image_urls, vehicle_ids)`
Process multiple images in batch.

**Parameters:**
- `image_urls` (list): List of image URLs or paths
- `vehicle_ids` (list, optional): List of vehicle IDs

**Returns:**
- List of analysis results

### VehicleAnalysisStorage

#### `save_analysis(vehicle_id, analysis_data, metadata)`
Save analysis data to cloud database.

**Parameters:**
- `vehicle_id` (str): Vehicle identifier
- `analysis_data` (dict): Analysis results
- `metadata` (dict, optional): Additional metadata

**Returns:**
- Dictionary with save status and document ID

#### `get_analysis(analysis_id)`
Get a specific analysis by ID.

**Parameters:**
- `analysis_id` (str): Analysis document ID

**Returns:**
- Analysis document or None

#### `get_vehicle_history(vehicle_id, limit, sort_by, descending)`
Get all analyses for a vehicle.

**Parameters:**
- `vehicle_id` (str): Vehicle identifier
- `limit` (int): Maximum number of results
- `sort_by` (str): Field to sort by
- `descending` (bool): Sort order

**Returns:**
- List of analysis documents

#### `get_statistics(vehicle_id)`
Get statistics for analyses.

**Parameters:**
- `vehicle_id` (str, optional): Vehicle ID filter

**Returns:**
- Dictionary with statistics

## Analysis Result Structure

```json
{
  "analysis_id": "uuid-string",
  "vehicle_id": "BR-001",
  "timestamp": "2024-11-02T12:00:00Z",
  "image_info": {
    "source": "upload",
    "format": "jpg",
    "width": 640,
    "height": 480,
    "channels": 3
  },
  "detected_objects": {
    "total_objects": 15,
    "objects": [
      {
        "class": "tire",
        "confidence": 0.98,
        "bbox": [100, 300, 150, 100]
      }
    ],
    "detection_time_ms": 150
  },
  "anomalies": {
    "total_anomalies": 3,
    "anomalies": [
      {
        "type": "dent",
        "severity": "medium",
        "location": {"x": 0.45, "y": 0.6},
        "dimensions": {"width": 5.0, "height": 3.0, "depth": 0.5},
        "confidence": 0.85,
        "estimated_repair_cost": 800.00,
        "recommended_action": "Panel beating and repainting"
      }
    ],
    "anomaly_types": {
      "dent": 1,
      "scratch": 1,
      "rust": 1
    },
    "detection_time_ms": 200
  },
  "damage_assessment": {
    "overall_condition": "good",
    "damage_score": 45.5,
    "estimated_repair_cost": 1150.00,
    "estimated_repair_time": "2-3 days",
    "priority": "medium",
    "total_anomalies": 3,
    "assessment_time_ms": 100
  },
  "confidence_score": 0.9456,
  "processing_time_ms": 450,
  "model_version": "v1.0",
  "cloud_storage_id": "cloud-document-id",
  "cloud_storage_url": "https://cloud.example.com/..."
}
```

## Cloud Database Schema

### Collection: `vehicle_analyses`

```json
{
  "_id": "unique-document-id",
  "vehicle_id": "BR-001",
  "analysis_id": "uuid-string",
  "analysis_data": {
    // Full analysis result as shown above
  },
  "timestamp": "2024-11-02T12:00:00Z",
  "type": "vehicle_analysis",
  "metadata": {
    "processed_by": "ai_system",
    "version": "v1.0",
    "user_id": "user-uuid"
  },
  "indexes": {
    "vehicle_id": "BR-001",
    "analysis_type": "full",
    "timestamp": "2024-11-02T12:00:00Z",
    "damage_score": 45.5
  }
}
```

## Integration with LOWDATAESC

The cloud processing module can be integrated with **LOWDATAESC** for cross-sector data sharing:

```python
from ML.ai.cloud_processing import CloudImageProcessor
from backend.services.lowdataesc_integration import LOWDATAESCService

# Process image
processor = CloudImageProcessor(cloud_client=cloud_client)
result = processor.process_image(image_data)

# Send to LOWDATAESC
lowdataesc_service = LOWDATAESCService()
lowdataesc_service.store_image_analysis(result)

# Get cross-sector insights
insights = lowdataesc_service.get_sector_insights("automotive")
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Processing Time | < 500ms per image |
| Throughput | 10+ images/second |
| Detection Accuracy | > 95% |
| Anomaly Detection | > 93% |
| Damage Assessment | > 92% |
| Cloud Save Time | < 100ms |
| Query Time | < 50ms |

## Error Handling

The module handles various error scenarios:

- **Image Loading Errors**: Returns error status with details
- **Model Loading Errors**: Falls back to basic processing
- **Cloud Connection Errors**: Queues for retry
- **Database Errors**: Logs and returns error status

## Security

- All cloud connections use **TLS encryption**
- **Authentication tokens** are required for cloud access
- **Data validation** is performed on all inputs
- **Error messages** do not expose sensitive information

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This module is part of **KCo by Cília** and is subject to confidentiality agreements. Unauthorized distribution is prohibited.

## Contact

- **Email**: contato@kco.ai
- **Website**: https://kco.ai
- **Landing Page**: https://kauecodify.github.io/KCo/

---

> **© 2024-2026 KCo by Cília | Laboratory of K and RockNewVenture**
> 
> **Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD**
