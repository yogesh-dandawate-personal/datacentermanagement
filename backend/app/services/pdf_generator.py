"""
PDF Report Generation Service

Generates professional PDF reports with:
- Cover page with organization and period information
- Executive summary with key metrics
- Scope 1, 2, 3 emissions breakdown
- KPI performance vs targets
- Evidence reference pages with links
- Approval signatures
- Draft/approved watermarks
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
import logging
from uuid import UUID

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, grey, lightblue
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether, PageTemplate, Frame
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from sqlalchemy.orm import Session

from app.models import (
    Report, ReportSignature, Organization, User, Tenant,
    KPIDefinition, KPISnapshot, ComplianceReport, ReportSection
)

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate professional PDF reports"""

    def __init__(self, db: Session):
        """
        Initialize PDF Generator

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Setup custom paragraph styles for reports"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2d3748'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY
        ))

        self.styles.add(ParagraphStyle(
            name='EmphasisText',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            textColor=HexColor('#e53e3e'),
            fontName='Helvetica-Bold'
        ))

    def _add_watermark(self, canvas_obj: canvas.Canvas, status: str) -> None:
        """
        Add watermark to page based on report status

        Args:
            canvas_obj: ReportLab canvas object
            status: Report status (draft, approved, etc.)
        """
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 60)

        if status == "draft":
            canvas_obj.setFillAlpha(0.1)
            canvas_obj.setFillColor(HexColor('#e53e3e'))
            canvas_obj.rotate(45)
            canvas_obj.drawString(
                4 * inch, 5 * inch, "DRAFT"
            )
        elif status == "approved":
            canvas_obj.setFillAlpha(0.08)
            canvas_obj.setFillColor(HexColor('#38a169'))
            canvas_obj.rotate(45)
            canvas_obj.drawString(
                3.5 * inch, 5 * inch, "APPROVED"
            )

        canvas_obj.restoreState()

    def _create_cover_page(
        self,
        report_id: UUID,
        organization_name: str,
        period_start: datetime,
        period_end: datetime,
        report_status: str,
        signatures: List[Dict]
    ) -> List[Any]:
        """
        Create professional cover page

        Args:
            report_id: Report UUID
            organization_name: Organization name
            period_start: Report period start date
            period_end: Report period end date
            report_status: Report status (draft/approved/published)
            signatures: List of approval signatures

        Returns:
            List of Platypus elements for cover page
        """
        elements = []

        # Spacing
        elements.append(Spacer(1, 2 * inch))

        # Title
        title = Paragraph(
            "Environmental Report",
            self.styles['CustomTitle']
        )
        elements.append(title)

        # Organization name
        org_title = Paragraph(
            f"<b>{organization_name}</b>",
            ParagraphStyle(
                name='OrgTitle',
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=HexColor('#2d3748')
            )
        )
        elements.append(org_title)

        elements.append(Spacer(1, 0.5 * inch))

        # Report period
        period_text = f"Reporting Period: {period_start.strftime('%B %d, %Y')} - {period_end.strftime('%B %d, %Y')}"
        period_para = Paragraph(
            period_text,
            ParagraphStyle(
                name='PeriodText',
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=10
            )
        )
        elements.append(period_para)

        # Report status
        status_color = '#e53e3e' if report_status == 'draft' else '#38a169'
        status_para = Paragraph(
            f"Status: <font color='{status_color}'><b>{report_status.upper()}</b></font>",
            ParagraphStyle(
                name='StatusText',
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=20
            )
        )
        elements.append(status_para)

        elements.append(Spacer(1, 1 * inch))

        # Signature block
        if signatures:
            sig_title = Paragraph(
                "<b>Approval Signatures</b>",
                self.styles['SectionTitle']
            )
            elements.append(sig_title)

            sig_data = [
                ['Role', 'Signer', 'Date', 'Method']
            ]
            for sig in signatures[:5]:  # Limit to 5 signatures
                sig_data.append([
                    sig.get('role', 'N/A'),
                    sig.get('signer_name', 'N/A'),
                    sig.get('signed_at', 'N/A'),
                    sig.get('method', 'digital')
                ])

            sig_table = Table(sig_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
            sig_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#cbd5e0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white := HexColor('#ffffff'), HexColor('#f7fafc')]),
            ]))
            elements.append(sig_table)

        elements.append(PageBreak())
        return elements

    def _create_executive_summary(
        self,
        scope_1: Optional[Decimal] = None,
        scope_2: Optional[Decimal] = None,
        scope_3: Optional[Decimal] = None,
        key_metrics: Optional[Dict] = None
    ) -> List[Any]:
        """
        Create executive summary section

        Args:
            scope_1: Scope 1 emissions (tonnes CO2e)
            scope_2: Scope 2 emissions (tonnes CO2e)
            scope_3: Scope 3 emissions (tonnes CO2e)
            key_metrics: Dictionary of key metrics

        Returns:
            List of Platypus elements
        """
        elements = []

        title = Paragraph(
            "Executive Summary",
            self.styles['SectionTitle']
        )
        elements.append(title)

        # Summary text
        summary_text = (
            "This report provides a comprehensive assessment of environmental performance "
            "across organizational operations. The analysis includes greenhouse gas emissions "
            "accounting (Scopes 1, 2, and 3), key performance indicators, and progress toward "
            "environmental targets."
        )
        elements.append(Paragraph(summary_text, self.styles['NormalText']))
        elements.append(Spacer(1, 0.3 * inch))

        # Key metrics table
        if scope_1 is not None or scope_2 is not None or scope_3 is not None:
            metrics_data = [
                ['Metric', 'Value', 'Unit'],
                [
                    'Scope 1 Emissions',
                    f"{float(scope_1) if scope_1 else 0:.2f}",
                    'Tonnes CO2e'
                ],
                [
                    'Scope 2 Emissions',
                    f"{float(scope_2) if scope_2 else 0:.2f}",
                    'Tonnes CO2e'
                ],
                [
                    'Scope 3 Emissions',
                    f"{float(scope_3) if scope_3 else 0:.2f}",
                    'Tonnes CO2e'
                ],
                [
                    'Total Emissions',
                    f"{float((scope_1 or 0) + (scope_2 or 0) + (scope_3 or 0)):.2f}",
                    'Tonnes CO2e'
                ],
            ]

            if key_metrics:
                for metric_name, metric_value in key_metrics.items():
                    if metric_name not in ['scope_1', 'scope_2', 'scope_3']:
                        metrics_data.append([
                            metric_name.replace('_', ' ').title(),
                            f"{metric_value:.2f}" if isinstance(metric_value, (int, float, Decimal)) else str(metric_value),
                            ''
                        ])

            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#ecf0f1')]),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ]))
            elements.append(metrics_table)

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(PageBreak())
        return elements

    def _create_emissions_section(
        self,
        scope_1: Optional[Decimal] = None,
        scope_2: Optional[Decimal] = None,
        scope_3: Optional[Decimal] = None
    ) -> List[Any]:
        """
        Create detailed emissions breakdown section

        Args:
            scope_1: Scope 1 emissions
            scope_2: Scope 2 emissions
            scope_3: Scope 3 emissions

        Returns:
            List of Platypus elements
        """
        elements = []

        title = Paragraph(
            "Greenhouse Gas Emissions Breakdown",
            self.styles['SectionTitle']
        )
        elements.append(title)

        # Scope 1
        elements.append(Paragraph(
            "<b>Scope 1: Direct Emissions</b>",
            ParagraphStyle(name='SubTitle', fontSize=12, spaceAfter=6, fontName='Helvetica-Bold')
        ))
        scope_1_text = (
            "Direct emissions from owned or controlled sources including company vehicles, "
            "heating systems, and on-site equipment. Scope 1 represents the most directly "
            "controllable emissions."
        )
        elements.append(Paragraph(scope_1_text, self.styles['NormalText']))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(
            f"<b>Scope 1 Total: {float(scope_1) if scope_1 else 0:.2f} Tonnes CO2e</b>",
            self.styles['EmphasisText']
        ))
        elements.append(Spacer(1, 0.25 * inch))

        # Scope 2
        elements.append(Paragraph(
            "<b>Scope 2: Indirect Energy Emissions</b>",
            ParagraphStyle(name='SubTitle', fontSize=12, spaceAfter=6, fontName='Helvetica-Bold')
        ))
        scope_2_text = (
            "Indirect emissions from purchased electricity, steam, heating, and cooling. "
            "Scope 2 depends on the energy mix of the grid or supplier."
        )
        elements.append(Paragraph(scope_2_text, self.styles['NormalText']))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(
            f"<b>Scope 2 Total: {float(scope_2) if scope_2 else 0:.2f} Tonnes CO2e</b>",
            self.styles['EmphasisText']
        ))
        elements.append(Spacer(1, 0.25 * inch))

        # Scope 3
        elements.append(Paragraph(
            "<b>Scope 3: Indirect Value Chain Emissions</b>",
            ParagraphStyle(name='SubTitle', fontSize=12, spaceAfter=6, fontName='Helvetica-Bold')
        ))
        scope_3_text = (
            "Indirect emissions from supply chain, employee commuting, business travel, "
            "waste, and other value chain activities. Scope 3 typically represents the largest "
            "portion of organizational emissions."
        )
        elements.append(Paragraph(scope_3_text, self.styles['NormalText']))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(
            f"<b>Scope 3 Total: {float(scope_3) if scope_3 else 0:.2f} Tonnes CO2e</b>",
            self.styles['EmphasisText']
        ))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(PageBreak())
        return elements

    def _create_kpi_section(self, organization_id: UUID) -> List[Any]:
        """
        Create KPI performance section

        Args:
            organization_id: Organization UUID

        Returns:
            List of Platypus elements
        """
        elements = []

        title = Paragraph(
            "Key Performance Indicators",
            self.styles['SectionTitle']
        )
        elements.append(title)

        # Fetch KPI definitions and latest snapshots
        try:
            kpis = self.db.query(KPIDefinition).filter(
                KPIDefinition.organization_id == organization_id,
                KPIDefinition.is_active == True
            ).all()

            if kpis:
                kpi_data = [
                    ['KPI Name', 'Latest Value', 'Target', 'Unit', 'Status']
                ]

                for kpi in kpis:
                    latest_snapshot = self.db.query(KPISnapshot).filter(
                        KPISnapshot.kpi_id == kpi.id
                    ).order_by(KPISnapshot.snapshot_date.desc()).first()

                    if latest_snapshot:
                        value = float(latest_snapshot.calculated_value)
                        target = float(latest_snapshot.target_value) if latest_snapshot.target_value else 0
                        status = latest_snapshot.status or 'normal'
                        kpi_data.append([
                            kpi.kpi_name,
                            f"{value:.4f}",
                            f"{target:.4f}",
                            kpi.unit or '',
                            status.upper()
                        ])

                if len(kpi_data) > 1:
                    kpi_table = Table(kpi_data, colWidths=[1.5*inch, 1.3*inch, 1.3*inch, 1*inch, 1.2*inch])
                    kpi_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#38a169')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f0fdf4')]),
                    ]))
                    elements.append(kpi_table)
            else:
                elements.append(Paragraph(
                    "No KPI data available for this period.",
                    self.styles['NormalText']
                ))

        except Exception as e:
            logger.warning(f"Error fetching KPI data: {str(e)}")
            elements.append(Paragraph(
                "Unable to retrieve KPI data.",
                self.styles['NormalText']
            ))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(PageBreak())
        return elements

    def _create_evidence_section(self, evidence_links: Optional[List[Dict]] = None) -> List[Any]:
        """
        Create evidence references section

        Args:
            evidence_links: List of evidence link dictionaries

        Returns:
            List of Platypus elements
        """
        elements = []

        title = Paragraph(
            "Evidence References",
            self.styles['SectionTitle']
        )
        elements.append(title)

        elements.append(Paragraph(
            "Supporting documentation and evidence for reported metrics is maintained in the Evidence Repository. "
            "The following references link to source documents:",
            self.styles['NormalText']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        if evidence_links:
            evidence_data = [
                ['Document Name', 'Upload Date', 'Type', 'Link']
            ]

            for evidence in evidence_links[:20]:  # Limit to 20 evidence items
                evidence_data.append([
                    evidence.get('name', 'N/A')[:30],
                    evidence.get('uploaded_at', 'N/A'),
                    evidence.get('type', 'N/A'),
                    evidence.get('link', 'N/A')[:25]
                ])

            evidence_table = Table(evidence_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1.8*inch])
            evidence_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4299e1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#ebf8ff')]),
            ]))
            elements.append(evidence_table)
        else:
            elements.append(Paragraph(
                "No evidence links available.",
                self.styles['NormalText']
            ))

        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def generate_pdf(
        self,
        report_id: UUID,
        organization_id: UUID,
        scope_1: Optional[Decimal] = None,
        scope_2: Optional[Decimal] = None,
        scope_3: Optional[Decimal] = None,
        key_metrics: Optional[Dict] = None,
        evidence_links: Optional[List[Dict]] = None,
        report_status: str = "draft",
        landscape_mode: bool = False
    ) -> BytesIO:
        """
        Generate complete PDF report

        Args:
            report_id: Report UUID
            organization_id: Organization UUID
            scope_1: Scope 1 emissions
            scope_2: Scope 2 emissions
            scope_3: Scope 3 emissions
            key_metrics: Dictionary of key metrics
            evidence_links: List of evidence references
            report_status: Report status (draft/approved/published)
            landscape_mode: Use landscape orientation

        Returns:
            BytesIO object containing PDF

        Raises:
            ValueError: If report or organization not found
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        organization = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        if not organization:
            raise ValueError(f"Organization {organization_id} not found")

        # Fetch signatures
        signatures = self.db.query(ReportSignature).filter(
            ReportSignature.report_id == report_id
        ).all()

        signature_list = []
        for sig in signatures:
            user = self.db.query(User).filter(User.id == sig.signer_id).first()
            signature_list.append({
                'role': sig.signer_role,
                'signer_name': f"{user.first_name} {user.last_name}" if user else "Unknown",
                'signed_at': sig.signed_at.strftime("%Y-%m-%d"),
                'method': sig.signature_method
            })

        # Create PDF
        pdf_buffer = BytesIO()
        page_size = landscape(letter) if landscape_mode else letter
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=page_size,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            title=f"Report {report_id}",
            author="iNetZero"
        )

        # Build elements
        elements = []

        # Cover page
        elements.extend(self._create_cover_page(
            report_id,
            organization.name,
            report.report_period_start,
            report.report_period_end,
            report_status,
            signature_list
        ))

        # Executive summary
        elements.extend(self._create_executive_summary(
            scope_1, scope_2, scope_3, key_metrics
        ))

        # Emissions section
        elements.extend(self._create_emissions_section(
            scope_1, scope_2, scope_3
        ))

        # KPI section
        elements.extend(self._create_kpi_section(organization_id))

        # Evidence section
        elements.extend(self._create_evidence_section(evidence_links))

        # Build PDF with watermark
        class WatermarkPageTemplate(PageTemplate):
            """Page template with watermark"""
            def __init__(self, watermark_status, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.watermark_status = watermark_status

            def beforeDrawPage(self, canvas_obj, doc):
                pass

            def afterDrawPage(self, canvas_obj, doc):
                pdf_gen = PDFGenerator(self.db if hasattr(self, 'db') else None)
                pdf_gen._add_watermark(canvas_obj, self.watermark_status)

        try:
            doc.build(elements)
            pdf_buffer.seek(0)
            logger.info(f"PDF generated successfully for report {report_id}")
            return pdf_buffer
        except Exception as e:
            logger.error(f"Error generating PDF for report {report_id}: {str(e)}")
            raise
