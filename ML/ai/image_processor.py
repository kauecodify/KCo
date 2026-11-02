"""
AI Image Processor - Advanced Image Analysis
KCo Fleet Intelligence Platform - Old But Gold TR8 IVSTO
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import json
import logging

from backend.models.image import ImageAnalysisResult, DamageAssessment, DetectedObject
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class AIImageProcessor:
    """AI-powered image processor for vehicle analysis"""
    
    def __init__(self):
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load AI models"""
        try:
            logger.info("Loading AI models...")
            # In production, load actual models
            # For now, we'll use OpenCV and mock models
            self.models_loaded = True
            logger.info("AI models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
            self.models_loaded = False
    
    def process_image(
        self,
        image_data: Dict[str, Any],
        vehicle_id: Optional[str] = None
    ) -> ImageAnalysisResult:
        """Process image and return analysis results"""
        start_time = datetime.utcnow()
        
        try:
            # Load image
            image = self._load_image(image_data)
            if image is None:
                raise ValueError("Failed to load image")
            
            # Generate unique ID
            analysis_id = str(uuid.uuid4())
            image_id = image_data.get("image_id", str(uuid.uuid4()))
            
            # Perform analysis
            detected_objects = self._detect_objects(image)
            anomalies = self._detect_anomalies(image, detected_objects)
            damage_assessment = self._assess_damage(image, detected_objects, anomalies)
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(detected_objects, anomalies)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create result
            result = ImageAnalysisResult(
                id=analysis_id,
                image_id=image_id,
                image_url=image_data.get("image_url", ""),
                vehicle_id=vehicle_id,
                analysis_timestamp=datetime.utcnow(),
                detected_objects=[obj.to_dict() for obj in detected_objects],
                anomalies=[anom.to_dict() for anom in anomalies],
                damage_assessment=damage_assessment.to_dict() if damage_assessment else {},
                image_width=image.shape[1] if len(image.shape) > 1 else 0,
                image_height=image.shape[0] if len(image.shape) > 1 else 0,
                image_format=image_data.get("image_format", "jpg"),
                image_size_bytes=image.nbytes if hasattr(image, 'nbytes') else 0,
                processing_time_ms=processing_time,
                confidence_score=confidence_score,
                model_version="v2.1.0",
                categories=self._categorize_image(detected_objects, anomalies)
            )
            
            logger.info(f"Processed image {analysis_id} in {processing_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _load_image(self, image_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Load image from various sources"""
        try:
            if "image_url" in image_data and image_data["image_url"]:
                # Download from URL
                import requests
                response = requests.get(image_data["image_url"], timeout=10)
                response.raise_for_status()
                image_array = np.frombuffer(response.content, np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            elif "image_base64" in image_data and image_data["image_base64"]:
                # Decode from base64
                image_base64 = image_data["image_base64"]
                if "," in image_base64:
                    image_base64 = image_base64.split(",")[1]
                image_array = np.frombuffer(base64.b64decode(image_base64), np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            elif "image_path" in image_data and image_data["image_path"]:
                # Load from file path
                return cv2.imread(image_data["image_path"])
            
            elif "image_file" in image_data and image_data["image_file"]:
                # Load from file object
                file = image_data["image_file"]
                if hasattr(file, 'read'):
                    content = file.read()
                    image_array = np.frombuffer(content, np.uint8)
                    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def _detect_objects(self, image: np.ndarray) -> List[DetectedObject]:
        """Detect objects in image using AI"""
        objects = []
        
        try:
            height, width = image.shape[:2]
            
            # In production, use actual object detection model (YOLO, etc.)
            # For demo, we'll detect some common vehicle parts
            
            # Mock detections based on image regions
            regions = [
                {"x_min": 0.1, "y_min": 0.6, "x_max": 0.3, "y_max": 0.9, "type": "tire", "confidence": 0.95},
                {"x_min": 0.7, "y_min": 0.6, "x_max": 0.9, "y_max": 0.9, "type": "tire", "confidence": 0.94},
                {"x_min": 0.15, "y_min": 0.35, "x_max": 0.25, "y_max": 0.45, "type": "headlight", "confidence": 0.92},
                {"x_min": 0.75, "y_min": 0.35, "x_max": 0.85, "y_max": 0.45, "type": "headlight", "confidence": 0.91},
                {"x_min": 0.3, "y_min": 0.2, "x_max": 0.7, "y_max": 0.6, "type": "door", "confidence": 0.98},
                {"x_min": 0.35, "y_min": 0.1, "x_max": 0.65, "y_max": 0.3, "type": "hood", "confidence": 0.96},
                {"x_min": 0.25, "y_min": 0.1, "x_max": 0.75, "y_max": 0.2, "type": "windshield", "confidence": 0.93},
            ]
            
            for region in regions:
                obj = DetectedObject(
                    object_type=region["type"],
                    confidence=region["confidence"],
                    bounding_box={
                        "x_min": region["x_min"],
                        "y_min": region["y_min"],
                        "x_max": region["x_max"],
                        "y_max": region["y_max"]
                    },
                    location={
                        "x": (region["x_min"] + region["x_max"]) / 2,
                        "y": (region["y_min"] + region["y_max"]) / 2
                    },
                    size={
                        "width": region["x_max"] - region["x_min"],
                        "height": region["y_max"] - region["y_min"]
                    }
                )
                objects.append(obj)
            
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
        
        return objects
    
    def _detect_anomalies(self, image: np.ndarray, detected_objects: List[DetectedObject]) -> List[Dict[str, Any]]:
        """Detect anomalies in image"""
        anomalies = []
        
        try:
            # In production, use actual anomaly detection model
            # For demo, we'll generate some mock anomalies
            
            # Check for common anomalies
            anomalies.append({
                "type": "dent",
                "severity": "medium",
                "description": "Dent detected on driver side door",
                "confidence": 0.85,
                "location": {"x": 0.4, "y": 0.5},
                "size": {"width": 0.05, "height": 0.05}
            })
            
            anomalies.append({
                "type": "scratch",
                "severity": "low",
                "description": "Scratch detected on hood",
                "confidence": 0.75,
                "location": {"x": 0.5, "y": 0.2},
                "size": {"width": 0.1, "height": 0.02}
            })
            
            # Check for rust based on color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lower_rust = np.array([0, 100, 50])
            upper_rust = np.array([10, 255, 255])
            mask = cv2.inRange(hsv, lower_rust, upper_rust)
            rust_pixels = cv2.countNonZero(mask)
            total_pixels = image.size // 3
            
            if rust_pixels > total_pixels * 0.01:  # More than 1% rust
                anomalies.append({
                    "type": "rust",
                    "severity": "high",
                    "description": "Significant rust detected",
                    "confidence": 0.88,
                    "location": {"x": 0.6, "y": 0.4},
                    "size": {"width": 0.15, "height": 0.1}
                })
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def _assess_damage(self, image: np.ndarray, detected_objects: List[DetectedObject], anomalies: List[Dict[str, Any]]) -> DamageAssessment:
        """Assess damage from detected anomalies"""
        try:
            # Calculate overall damage score
            damage_score = 0
            total_repair_cost = 0
            
            for anomaly in anomalies:
                if anomaly["severity"] == "critical":
                    damage_score += 0.4
                    total_repair_cost += 2000
                elif anomaly["severity"] == "high":
                    damage_score += 0.3
                    total_repair_cost += 1000
                elif anomaly["severity"] == "medium":
                    damage_score += 0.2
                    total_repair_cost += 500
                else:
                    damage_score += 0.1
                    total_repair_cost += 200
            
            # Normalize damage score
            damage_score = min(1.0, damage_score)
            
            # Determine overall condition
            if damage_score < 0.2:
                condition = "excellent"
            elif damage_score < 0.4:
                condition = "good"
            elif damage_score < 0.6:
                condition = "fair"
            elif damage_score < 0.8:
                condition = "poor"
            else:
                condition = "severe"
            
            return DamageAssessment(
                damage_type="multiple",
                severity=anomalies[0]["severity"] if anomalies else "low",
                location={"x": 0.5, "y": 0.5},
                dimensions={"width": 0.5, "height": 0.5},
                estimated_repair_cost=total_repair_cost,
                confidence=0.9,
                description=f"Overall condition: {condition}",
                recommended_action="Schedule maintenance inspection"
            )
            
        except Exception as e:
            logger.error(f"Error assessing damage: {e}")
            return DamageAssessment(
                damage_type="unknown",
                severity="low",
                location={"x": 0, "y": 0},
                dimensions={"width": 0, "height": 0},
                estimated_repair_cost=0,
                confidence=0.0,
                description="Unable to assess damage",
                recommended_action="Manual inspection required"
            )
    
    def _calculate_confidence(self, detected_objects: List[DetectedObject], anomalies: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score"""
        confidences = []
        
        for obj in detected_objects:
            confidences.append(obj.confidence)
        
        for anomaly in anomalies:
            confidences.append(anomaly.get("confidence", 0.0))
        
        if confidences:
            return sum(confidences) / len(confidences)
        
        return 0.0
    
    def _categorize_image(self, detected_objects: List[DetectedObject], anomalies: List[Dict[str, Any]]) -> Dict[str, float]:
        """Categorize image content"""
        categories = {
            "exterior": 0.0,
            "interior": 0.0,
            "damage": 0.0,
            "parts": 0.0
        }
        
        # Count object types
        object_types = [obj.object_type for obj in detected_objects]
        
        exterior_parts = ["tire", "headlight", "door", "hood", "bumper", "window", "windshield"]
        interior_parts = ["seat", "dashboard", "steering_wheel", "console"]
        
        for obj_type in object_types:
            if obj_type in exterior_parts:
                categories["exterior"] += 0.2
            elif obj_type in interior_parts:
                categories["interior"] += 0.2
        
        # Add damage category
        if anomalies:
            categories["damage"] = min(1.0, len(anomalies) * 0.3)
        
        # Normalize
        total = sum(categories.values())
        if total > 0:
            for key in categories:
                categories[key] = categories[key] / total
        
        return categories
    
    def generate_visual_report(self, result: ImageAnalysisResult, output_path: str) -> str:
        """Generate visual report with annotations"""
        try:
            # Load original image
            image_data = {"image_url": result.image_url}
            image = self._load_image(image_data)
            
            if image is None:
                return ""
            
            # Convert to PIL Image for drawing
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load font
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Draw bounding boxes for detected objects
            for obj in result.detected_objects:
                bbox = obj.get("bounding_box", {})
                if bbox:
                    x_min = int(bbox.get("x_min", 0) * pil_image.width)
                    y_min = int(bbox.get("y_min", 0) * pil_image.height)
                    x_max = int(bbox.get("x_max", 0) * pil_image.width)
                    y_max = int(bbox.get("y_max", 0) * pil_image.height)
                    
                    # Draw rectangle
                    draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=2)
                    
                    # Draw label
                    label = f"{obj.get('object_type', 'unknown')}: {obj.get('confidence', 0):.2f}"
                    draw.text((x_min, y_min - 25), label, fill="green", font=font)
            
            # Draw bounding boxes for anomalies
            for anomaly in result.anomalies:
                location = anomaly.get("location", {})
                size = anomaly.get("size", {})
                if location and size:
                    x = int(location.get("x", 0) * pil_image.width)
                    y = int(location.get("y", 0) * pil_image.height)
                    w = int(size.get("width", 0) * pil_image.width)
                    h = int(size.get("height", 0) * pil_image.height)
                    
                    x_min = x - w // 2
                    y_min = y - h // 2
                    x_max = x + w // 2
                    y_max = y + h // 2
                    
                    # Draw rectangle with color based on severity
                    severity = anomaly.get("severity", "low")
                    color_map = {
                        "low": "blue",
                        "medium": "yellow",
                        "high": "orange",
                        "critical": "red"
                    }
                    color = color_map.get(severity, "white")
                    
                    draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=2)
                    
                    # Draw label
                    label = f"{anomaly.get('type', 'unknown')}: {severity}"
                    draw.text((x_min, y_min - 25), label, fill=color, font=font)
            
            # Save image
            pil_image.save(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating visual report: {e}")
            return ""
    
    def process_batch(self, image_data_list: List[Dict[str, Any]]) -> List[ImageAnalysisResult]:
        """Process multiple images in batch"""
        results = []
        
        for image_data in image_data_list:
            try:
                result = self.process_image(image_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing image {image_data.get('image_id', 'unknown')}: {e}")
                continue
        
        return results


# Singleton instance
image_processor = AIImageProcessor()
