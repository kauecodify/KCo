"""
PDF Generator for Vehicle Reports
KCo Fleet Intelligence Platform - Old But Gold TR8 IVSTO
Generates professional PDF reports for vehicle analysis, anomalies, and maintenance
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import uuid
import logging
from io import BytesIO

# Try to import reportlab, fall back to mock if not available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not installed. PDF generation will be disabled. Install with: pip install reportlab")

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF reports for vehicle analysis"""
    
    def __init__(self):
        self.font_name = "Helvetica"
        self.font_size_title = 18
        self.font_size_heading = 14
        self.font_size_body = 10
        self.font_size_small = 8
        self.primary_color = colors.HexColor("#00d4ff")
        self.secondary_color = colors.HexColor("#9d4edd")
        self.text_color = colors.HexColor("#0a0a0f")
        self.bg_color = colors.HexColor("#f8f9fa")
        self.border_color = colors.HexColor("#00d4ff")
    
    def create_vehicle_report(
        self,
        vehicle_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        telemetry: Optional[Dict[str, Any]] = None,
        image_analysis: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Create comprehensive vehicle report PDF
        
        Args:
            vehicle_data: Vehicle information
            anomalies: List of detected anomalies
            telemetry: Telemetry data (optional)
            image_analysis: Image analysis results (optional)
            output_path: Output file path (optional, returns bytes if None)
            
        Returns:
            Tuple of (success, path_or_error)
        """
        if not REPORTLAB_AVAILABLE:
            return False, "ReportLab not installed"
        
        try:
            # Create buffer for PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                leftMargin=0.5 * inch,
                rightMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch,
                title=f"KCo Vehicle Report - {vehicle_data.get('license_plate', 'N/A')}"
            )
            
            # Build story
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=self.font_size_title,
                textColor=self.primary_color,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName=self.font_name + "-Bold"
            )
            
            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=self.font_size_heading,
                textColor=self.secondary_color,
                spaceAfter=12,
                spaceBefore=12,
                fontName=self.font_name + "-Bold"
            )
            
            body_style = ParagraphStyle(
                "CustomBody",
                parent=styles["Normal"],
                fontSize=self.font_size_body,
                textColor=self.text_color,
                spaceAfter=6,
                fontName=self.font_name
            )
            
            small_style = ParagraphStyle(
                "CustomSmall",
                parent=styles["Normal"],
                fontSize=self.font_size_small,
                textColor=self.text_color,
                spaceAfter=4,
                fontName=self.font_name
            )
            
            # Header
            story.append(self._create_header(doc, vehicle_data))
            story.append(Spacer(1, 0.2 * inch))
            
            # Title
            story.append(Paragraph("VEHICLE ANALYSIS REPORT", title_style))
            story.append(Paragraph("Old But Gold TR8 IVSTO", ParagraphStyle("Subtitle", fontSize=12, textColor=self.secondary_color, alignment=TA_CENTER)))
            story.append(Spacer(1, 0.2 * inch))
            story.append(HRFlowable(width="100%", thickness=1, lineCap="round", color=self.border_color))
            story.append(Spacer(1, 0.2 * inch))
            
            # Vehicle Information
            story.append(Paragraph("VEHICLE INFORMATION", heading_style))
            story.append(self._create_vehicle_info_table(vehicle_data))
            story.append(Spacer(1, 0.2 * inch))
            
            # Anomalies Summary
            if anomalies:
                story.append(Paragraph("ANOMALY DETECTION SUMMARY", heading_style))
                story.append(self._create_anomalies_table(anomalies))
                story.append(Spacer(1, 0.2 * inch))
            
            # Telemetry Data
            if telemetry:
                story.append(Paragraph("TELEMETRY DATA", heading_style))
                story.append(self._create_telemetry_table(telemetry))
                story.append(Spacer(1, 0.2 * inch))
            
            # Image Analysis
            if image_analysis:
                story.append(Paragraph("IMAGE ANALYSIS RESULTS", heading_style))
                story.append(self._create_image_analysis_table(image_analysis))
                story.append(Spacer(1, 0.2 * inch))
            
            # Financial Impact
            story.append(Paragraph("FINANCIAL IMPACT ASSESSMENT", heading_style))
            story.append(self._create_financial_table(vehicle_data, anomalies))
            story.append(Spacer(1, 0.2 * inch))
            
            # Recommendations
            story.append(Paragraph("RECOMMENDATIONS", heading_style))
            story.append(self._create_recommendations(vehicle_data, anomalies, telemetry, image_analysis))
            story.append(Spacer(1, 0.2 * inch))
            
            # Footer
            story.append(HRFlowable(width="100%", thickness=1, lineCap="round", color=self.border_color))
            story.append(Spacer(1, 0.1 * inch))
            story.append(self._create_footer())
            
            # Build PDF
            doc.build(story)
            
            # Save to file or return bytes
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(buffer.getvalue())
                return True, output_path
            else:
                # Return base64 encoded PDF
                import base64
                pdf_bytes = buffer.getvalue()
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
                return True, pdf_base64
                
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return False, str(e)
    
    def _create_header(self, doc, vehicle_data: Dict[str, Any]) -> Table:
        """Create document header with KCo branding"""
        data = [
            [
                Image("/workspace/github__kauecodify__KCo/docs/kco-logo.png", width=2 * inch, height=0.5 * inch) if os.path.exists("/workspace/github__kauecodify__KCo/docs/kco-logo.png") else Paragraph("KCo", ParagraphStyle("Logo", fontSize=24, textColor=self.primary_color, fontName=self.font_name + "-Bold")),
                Paragraph(f"Report ID: {uuid.uuid4()}", ParagraphStyle("ReportID", fontSize=10, textColor=self.text_color, alignment=TA_RIGHT))
            ],
            [
                Paragraph("Fleet Intelligence Platform", ParagraphStyle("Tagline", fontSize=10, textColor=self.secondary_color)),
                Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", ParagraphStyle("Date", fontSize=10, textColor=self.text_color, alignment=TA_RIGHT))
            ]
        ]
        
        table = Table(data, colWidths=[4 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return table
    
    def _create_vehicle_info_table(self, vehicle_data: Dict[str, Any]) -> Table:
        """Create vehicle information table"""
        data = [
            [Paragraph("<b>VIN</b>", body_style), Paragraph(vehicle_data.get("vin", "N/A"), body_style)],
            [Paragraph("<b>License Plate</b>", body_style), Paragraph(vehicle_data.get("license_plate", "N/A"), body_style)],
            [Paragraph("<b>Make/Model</b>", body_style), Paragraph(f"{vehicle_data.get('make', 'N/A')} {vehicle_data.get('model', '')}", body_style)],
            [Paragraph("<b>Year</b>", body_style), Paragraph(str(vehicle_data.get("year", "N/A")), body_style)],
            [Paragraph("<b>Country</b>", body_style), Paragraph(vehicle_data.get("country", "N/A").upper(), body_style)],
            [Paragraph("<b>Status</b>", body_style), self._get_status_badge(vehicle_data.get("status", "active"))],
            [Paragraph("<b>Instrumented</b>", body_style), Paragraph("Yes" if vehicle_data.get("instrumented", False) else "No", body_style)],
        ]
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def _get_status_badge(self, status: str) -> Paragraph:
        """Create status badge with color coding"""
        colors_map = {
            "active": colors.green,
            "maintenance": colors.orange,
            "retired": colors.red,
            "pending": colors.yellow
        }
        color = colors_map.get(status.lower(), self.text_color)
        
        return Paragraph(
            f'<b><font color="{color.toHex()}">{status.upper()}</font></b>',
            ParagraphStyle("Status", fontSize=10, textColor=self.text_color)
        )
    
    def _create_anomalies_table(self, anomalies: List[Dict[str, Any]]) -> Table:
        """Create anomalies summary table"""
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_anomalies = sorted(anomalies, key=lambda x: severity_order.get(x.get("severity", "low").lower(), 4))
        
        data = [
            [Paragraph("<b>#</b>", body_style), 
             Paragraph("<b>Type</b>", body_style), 
             Paragraph("<b>Severity</b>", body_style), 
             Paragraph("<b>Description</b>", body_style), 
             Paragraph("<b>Repair Cost</b>", body_style)]
        ]
        
        for i, anomaly in enumerate(sorted_anomalies, 1):
            severity_color = self._get_severity_color(anomaly.get("severity", "low"))
            data.append([
                Paragraph(str(i), body_style),
                Paragraph(anomaly.get("type", "Unknown"), body_style),
                Paragraph(f'<font color="{severity_color}">{anomaly.get("severity", "low").upper()}</font>', body_style),
                Paragraph(anomaly.get("description", "N/A"), body_style),
                Paragraph(f"${anomaly.get('repair_cost', 0):.2f}", body_style)
            ])
        
        # Add summary row
        total_cost = sum(float(a.get("repair_cost", 0)) for a in anomalies)
        data.append([
            Paragraph("<b>TOTAL</b>", ParagraphStyle("Total", fontSize=10, textColor=self.text_color, fontName=self.font_name + "-Bold")),
            Paragraph("", body_style),
            Paragraph("", body_style),
            Paragraph("", body_style),
            Paragraph(f"<b>${total_cost:.2f}</b>", ParagraphStyle("Total", fontSize=10, textColor=self.primary_color, fontName=self.font_name + "-Bold"))
        ])
        
        table = Table(data, colWidths=[0.5 * inch, 1 * inch, 1 * inch, 2.5 * inch, 1 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_color),
            ('BACKGROUND', (0, -1), (-1, -1), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors_map = {
            "critical": "#ff0000",
            "high": "#ff6600",
            "medium": "#ffcc00",
            "low": "#00cc00"
        }
        return colors_map.get(severity.lower(), "#000000")
    
    def _create_telemetry_table(self, telemetry: Dict[str, Any]) -> Table:
        """Create telemetry data table"""
        data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Unit</b>", body_style), Paragraph("<b>Status</b>", body_style)],
            [Paragraph("Speed", body_style), Paragraph(str(telemetry.get("speed", 0)), body_style), Paragraph("km/h", body_style), self._get_telemetry_status("speed", telemetry.get("speed"))],
            [Paragraph("Engine RPM", body_style), Paragraph(str(telemetry.get("engine_rpm", 0)), body_style), Paragraph("RPM", body_style), self._get_telemetry_status("engine_rpm", telemetry.get("engine_rpm"))],
            [Paragraph("Engine Temp", body_style), Paragraph(f"{telemetry.get('engine_temperature', 0):.1f}", body_style), Paragraph("C", body_style), self._get_telemetry_status("engine_temperature", telemetry.get("engine_temperature"))],
            [Paragraph("Oil Pressure", body_style), Paragraph(f"{telemetry.get('oil_pressure', 0):.1f}", body_style), Paragraph("psi", body_style), self._get_telemetry_status("oil_pressure", telemetry.get("oil_pressure"))],
            [Paragraph("Battery Voltage", body_style), Paragraph(f"{telemetry.get('battery_voltage', 0):.2f}", body_style), Paragraph("V", body_style), self._get_telemetry_status("battery_voltage", telemetry.get("battery_voltage"))],
            [Paragraph("Fuel Level", body_style), Paragraph(f"{telemetry.get('fuel_level', 0):.1f}%", body_style), Paragraph("%", body_style), self._get_telemetry_status("fuel_level", telemetry.get("fuel_level"))],
        ]
        
        # Add OBD-II codes if present
        obd_codes = telemetry.get("obd_codes", [])
        if obd_codes:
            data.append([
                Paragraph("OBD-II Codes", body_style),
                Paragraph(", ".join(obd_codes), body_style),
                Paragraph("", body_style),
                Paragraph("<b>WARNING</b>", ParagraphStyle("Warning", fontSize=10, textColor=colors.red))
            ])
        
        table = Table(data, colWidths=[1.5 * inch, 1.5 * inch, 1 * inch, 1 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def _get_telemetry_status(self, metric: str, value) -> Paragraph:
        """Get status indicator for telemetry value"""
        thresholds = settings.ANOMALY_THRESHOLDS
        
        if metric in thresholds:
            threshold = thresholds[metric]
            if value > threshold:
                return Paragraph("<b>ALERT</b>", ParagraphStyle("Alert", fontSize=10, textColor=colors.red))
        
        return Paragraph("OK", ParagraphStyle("OK", fontSize=10, textColor=colors.green))
    
    def _create_image_analysis_table(self, image_analysis: Dict[str, Any]) -> Table:
        """Create image analysis results table"""
        detected_objects = image_analysis.get("detected_objects", [])
        anomalies = image_analysis.get("anomalies", [])
        damage_assessment = image_analysis.get("damage_assessment", {})
        
        data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style)],
            [Paragraph("Confidence Score", body_style), Paragraph(f"{image_analysis.get('confidence_score', 0) * 100:.2f}%", body_style)],
            [Paragraph("Processing Time", body_style), Paragraph(f"{image_analysis.get('processing_time_ms', 0):.2f} ms", body_style)],
            [Paragraph("Model Version", body_style), Paragraph(image_analysis.get("model_version", "N/A"), body_style)],
            [Paragraph("Objects Detected", body_style), Paragraph(str(len(detected_objects)), body_style)],
            [Paragraph("Anomalies Found", body_style), Paragraph(str(len(anomalies)), body_style)],
            [Paragraph("Damage Score", body_style), Paragraph(f"{damage_assessment.get('damage_score', 0) * 100:.1f}%", body_style)],
        ]
        
        if damage_assessment:
            data.append([
                Paragraph("Est. Repair Cost", body_style),
                Paragraph(f"${damage_assessment.get('estimated_repair_cost', 0):.2f}", body_style)
            ])
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def _create_financial_table(self, vehicle_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> Table:
        """Create financial impact assessment table"""
        country = vehicle_data.get("country", "br")
        country_data = settings.COUNTRIES.get(country, settings.COUNTRIES["br"])
        
        total_repair_cost = sum(float(a.get("repair_cost", 0)) for a in anomalies)
        monthly_revenue = country_data.get("revenue_per_vehicle", 0)
        
        # Calculate impact
        downtime_days = max(1, len(anomalies))  # At least 1 day for any anomaly
        lost_revenue = (downtime_days / 30) * monthly_revenue
        
        data = [
            [Paragraph("<b>Item</b>", body_style), Paragraph("<b>Amount (USD)</b>", body_style)],
            [Paragraph("Repair Cost (Estimated)", body_style), Paragraph(f"${total_repair_cost:.2f}", body_style)],
            [Paragraph("Downtime Lost Revenue", body_style), Paragraph(f"${lost_revenue:.2f}", body_style)],
            [Paragraph("Total Financial Impact", body_style), Paragraph(f"<b>${total_repair_cost + lost_revenue:.2f}</b>", ParagraphStyle("Total", fontSize=10, textColor=self.primary_color, fontName=self.font_name + "-Bold"))],
        ]
        
        table = Table(data, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_color),
            ('BACKGROUND', (0, -1), (-1, -1), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def _create_recommendations(self, vehicle_data: Dict[str, Any], anomalies: List[Dict[str, Any]], 
                                  telemetry: Optional[Dict[str, Any]], image_analysis: Optional[Dict[str, Any]]) -> List:
        """Create recommendations section"""
        recommendations = []
        
        # Generate recommendations based on data
        if anomalies:
            critical_anomalies = [a for a in anomalies if a.get("severity") == "critical"]
            high_anomalies = [a for a in anomalies if a.get("severity") == "high"]
            
            if critical_anomalies:
                recommendations.append(Paragraph(
                    f"IMMEDIATE ACTION REQUIRED: {len(critical_anomalies)} critical anomaly(ies) detected. Vehicle should be taken out of service immediately.",
                    ParagraphStyle("Critical", fontSize=10, textColor=colors.red, fontName=self.font_name + "-Bold")
                ))
            
            if high_anomalies:
                recommendations.append(Paragraph(
                    f"SCHEDULE MAINTENANCE: {len(high_anomalies)} high severity anomaly(ies) require attention within 24-48 hours.",
                    ParagraphStyle("High", fontSize=10, textColor=colors.orange, fontName=self.font_name + "-Bold")
                ))
        
        if telemetry:
            obd_codes = telemetry.get("obd_codes", [])
            if obd_codes:
                recommendations.append(Paragraph(
                    f"DIAGNOSTIC REQUIRED: {len(obd_codes)} OBD-II code(s) detected. Professional diagnostic scan recommended.",
                    ParagraphStyle("Diagnostic", fontSize=10, textColor=colors.orange, fontName=self.font_name + "-Bold")
                ))
        
        if image_analysis:
            damage_score = image_analysis.get("damage_assessment", {}).get("damage_score", 0)
            if damage_score > 0.5:
                recommendations.append(Paragraph(
                    f"VEHICLE CONDITION: Significant damage detected ({damage_score * 100:.1f}% score). Consider comprehensive inspection.",
                    ParagraphStyle("Damage", fontSize=10, textColor=colors.orange, fontName=self.font_name + "-Bold")
                ))
        
        # Add standard recommendations
        recommendations.append(Paragraph(
            "Regular maintenance schedule should be followed to prevent costly repairs.",
            body_style
        ))
        
        recommendations.append(Paragraph(
            "All anomalies should be documented in the vehicle maintenance log.",
            body_style
        ))
        
        # If no issues found
        if not anomalies and not telemetry and not image_analysis:
            recommendations.append(Paragraph(
                "No issues detected. Vehicle is in good operating condition.",
                ParagraphStyle("Good", fontSize=10, textColor=colors.green, fontName=self.font_name + "-Bold")
            ))
        
        return recommendations
    
    def _create_footer(self) -> Table:
        """Create document footer"""
        data = [
            [
                Paragraph("KCo Fleet Intelligence Platform", small_style),
                Paragraph("Old But Gold TR8 IVSTO", small_style)
            ],
            [
                Paragraph(f"Pre-Seed Target: ${settings.PRE_SEED_TARGET:,.0f} USD", small_style),
                Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", small_style)
            ],
            [
                Paragraph("Confidential - For internal use only", small_style),
                Paragraph("Page <page>", small_style)
            ]
        ]
        
        table = Table(data, colWidths=[4 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return table
    
    def create_batch_report(
        self,
        vehicle_reports: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Create batch report for multiple vehicles
        
        Args:
            vehicle_reports: List of vehicle report data
            output_path: Output file path
            
        Returns:
            Tuple of (success, path_or_error)
        """
        if not REPORTLAB_AVAILABLE:
            return False, "ReportLab not installed"
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                leftMargin=0.5 * inch,
                rightMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch,
                title="KCo Batch Vehicle Report"
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                "BatchTitle",
                parent=styles["Heading1"],
                fontSize=20,
                textColor=self.primary_color,
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            story.append(Paragraph("BATCH VEHICLE REPORTS", title_style))
            story.append(Paragraph(f"Total Vehicles: {len(vehicle_reports)}", ParagraphStyle("Subtitle", fontSize=12, textColor=self.secondary_color, alignment=TA_CENTER)))
            story.append(Spacer(1, 0.2 * inch))
            story.append(HRFlowable(width="100%", thickness=1, lineCap="round", color=self.border_color))
            
            # Summary table
            story.append(Paragraph("SUMMARY", ParagraphStyle("Heading", fontSize=14, textColor=self.secondary_color)))
            story.append(self._create_batch_summary_table(vehicle_reports))
            story.append(PageBreak())
            
            # Individual reports
            for vehicle_report in vehicle_reports:
                story.append(Paragraph(f"Vehicle: {vehicle_report.get('vehicle', {}).get('license_plate', 'N/A')}", ParagraphStyle("VehicleTitle", fontSize=14, textColor=self.primary_color)))
                story.append(Spacer(1, 0.1 * inch))
                
                # Add vehicle info
                story.append(self._create_vehicle_info_table(vehicle_report.get("vehicle", {})))
                
                # Add anomalies if present
                if vehicle_report.get("anomalies"):
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(Paragraph("Anomalies:", ParagraphStyle("Section", fontSize=12, textColor=self.secondary_color)))
                    story.append(self._create_anomalies_table(vehicle_report.get("anomalies", [])))
                
                story.append(PageBreak())
            
            # Footer
            story.append(HRFlowable(width="100%", thickness=1, lineCap="round", color=self.border_color))
            story.append(Spacer(1, 0.1 * inch))
            story.append(self._create_footer())
            
            doc.build(story)
            
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(buffer.getvalue())
                return True, output_path
            else:
                import base64
                pdf_bytes = buffer.getvalue()
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
                return True, pdf_base64
                
        except Exception as e:
            logger.error(f"Error generating batch report: {e}")
            return False, str(e)
    
    def _create_batch_summary_table(self, vehicle_reports: List[Dict[str, Any]]) -> Table:
        """Create batch summary table"""
        total_vehicles = len(vehicle_reports)
        total_anomalies = sum(len(v.get("anomalies", [])) for v in vehicle_reports)
        total_repair_cost = sum(
            sum(float(a.get("repair_cost", 0)) for a in v.get("anomalies", []))
            for v in vehicle_reports
        )
        
        critical_count = sum(
            len([a for a in v.get("anomalies", []) if a.get("severity") == "critical"])
            for v in vehicle_reports
        )
        high_count = sum(
            len([a for a in v.get("anomalies", []) if a.get("severity") == "high"])
            for v in vehicle_reports
        )
        medium_count = sum(
            len([a for a in v.get("anomalies", []) if a.get("severity") == "medium"])
            for v in vehicle_reports
        )
        low_count = sum(
            len([a for a in v.get("anomalies", []) if a.get("severity") == "low"])
            for v in vehicle_reports
        )
        
        data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Count</b>", body_style)],
            [Paragraph("Total Vehicles", body_style), Paragraph(str(total_vehicles), body_style)],
            [Paragraph("Total Anomalies", body_style), Paragraph(str(total_anomalies), body_style)],
            [Paragraph("Critical Anomalies", body_style), Paragraph(str(critical_count), ParagraphStyle("Critical", fontSize=10, textColor=colors.red))],
            [Paragraph("High Severity", body_style), Paragraph(str(high_count), ParagraphStyle("High", fontSize=10, textColor=colors.orange))],
            [Paragraph("Medium Severity", body_style), Paragraph(str(medium_count), ParagraphStyle("Medium", fontSize=10, textColor=colors.yellow))],
            [Paragraph("Low Severity", body_style), Paragraph(str(low_count), ParagraphStyle("Low", fontSize=10, textColor=colors.green))],
            [Paragraph("Total Repair Cost", body_style), Paragraph(f"<b>${total_repair_cost:,.2f}</b>", ParagraphStyle("Total", fontSize=10, textColor=self.primary_color, fontName=self.font_name + "-Bold"))],
        ]
        
        table = Table(data, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_color),
            ('BACKGROUND', (0, -1), (-1, -1), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def generate_vehicle_report_pdf(
        self,
        vehicle_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Generate comprehensive PDF report for a specific vehicle
        
        Args:
            vehicle_id: Vehicle ID
            start_date: Start date for report (optional)
            end_date: End date for report (optional)
            output_path: Output file path
            
        Returns:
            Tuple of (success, path_or_error)
        """
        # This would typically fetch data from the database
        # For now, return a placeholder
        if not REPORTLAB_AVAILABLE:
            return False, "ReportLab not installed"
        
        # Mock data for demonstration
        vehicle_data = {
            "id": vehicle_id,
            "vin": "BR001" + vehicle_id,
            "license_plate": vehicle_id,
            "make": "Test",
            "model": "Vehicle",
            "year": 2024,
            "country": "br",
            "status": "active",
            "instrumented": True
        }
        
        anomalies = [
            {
                "type": "dent",
                "severity": "medium",
                "description": "Dent on driver side door",
                "repair_cost": 500.00
            },
            {
                "type": "scratch",
                "severity": "low",
                "description": "Scratch on hood",
                "repair_cost": 200.00
            }
        ]
        
        telemetry = {
            "speed": 85,
            "engine_rpm": 2500,
            "engine_temperature": 85.5,
            "oil_pressure": 45.0,
            "battery_voltage": 12.6,
            "fuel_level": 65.0,
            "obd_codes": []
        }
        
        image_analysis = {
            "confidence_score": 0.95,
            "processing_time_ms": 150,
            "model_version": "v2.1.0",
            "detected_objects": [
                {"type": "tire", "confidence": 0.98},
                {"type": "door", "confidence": 0.95}
            ],
            "anomalies": [
                {"type": "dent", "severity": "medium"},
                {"type": "scratch", "severity": "low"}
            ],
            "damage_assessment": {
                "damage_score": 0.35,
                "estimated_repair_cost": 700.00
            }
        }
        
        return self.create_vehicle_report(
            vehicle_data=vehicle_data,
            anomalies=anomalies,
            telemetry=telemetry,
            image_analysis=image_analysis,
            output_path=output_path
        )


# Singleton instance
pdf_generator = PDFGenerator()
