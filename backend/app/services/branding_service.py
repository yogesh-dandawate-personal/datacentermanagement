"""
Custom Branding Service - Sprint 13 (AGENT 3)

Provides white-label branding support:
- Logo upload and management
- Color scheme customization
- Email template branding
- Report branding
- White-label configuration
- CDN asset management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_
import hashlib
import base64
import json

from ..models import Tenant
from ..integrations.s3_client import S3Client


class BrandingService:
    """Custom branding and white-label management"""

    # Default branding theme
    DEFAULT_THEME = {
        'colors': {
            'primary': '#3B82F6',
            'secondary': '#10B981',
            'accent': '#8B5CF6',
            'background': '#FFFFFF',
            'surface': '#F9FAFB',
            'text_primary': '#111827',
            'text_secondary': '#6B7280',
            'border': '#E5E7EB',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
            'info': '#3B82F6'
        },
        'typography': {
            'font_family': 'Inter, system-ui, sans-serif',
            'font_size_base': '16px',
            'font_weight_normal': '400',
            'font_weight_medium': '500',
            'font_weight_semibold': '600',
            'font_weight_bold': '700',
            'line_height_base': '1.5',
            'line_height_heading': '1.2'
        },
        'spacing': {
            'unit': '8px',
            'container_max_width': '1280px',
            'gutter': '24px'
        },
        'branding': {
            'show_powered_by': True,
            'powered_by_text': 'Powered by iNetZero',
            'show_logo': True,
            'logo_position': 'left'
        }
    }

    # Allowed logo file types
    ALLOWED_LOGO_TYPES = ['image/png', 'image/jpeg', 'image/svg+xml', 'image/webp']

    # Maximum logo file size (5MB)
    MAX_LOGO_SIZE = 5 * 1024 * 1024

    def __init__(self, db: Session, s3_client: Optional[S3Client] = None):
        """
        Initialize Branding service

        Args:
            db: SQLAlchemy session
            s3_client: S3 client for file uploads
        """
        self.db = db
        self.s3 = s3_client or S3Client()

    # ============================================================================
    # LOGO MANAGEMENT
    # ============================================================================

    def upload_logo(
        self,
        tenant_id: UUID,
        file_data: bytes,
        file_name: str,
        content_type: str,
        logo_type: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Upload organization logo

        Args:
            tenant_id: Tenant uploading logo
            file_data: Binary file data
            file_name: Original filename
            content_type: MIME type
            logo_type: Type of logo (primary, secondary, favicon, etc.)

        Returns:
            Logo metadata with CDN URL
        """
        # Validate file type
        if content_type not in self.ALLOWED_LOGO_TYPES:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(self.ALLOWED_LOGO_TYPES)}")

        # Validate file size
        if len(file_data) > self.MAX_LOGO_SIZE:
            raise ValueError(f"File size exceeds maximum of {self.MAX_LOGO_SIZE / (1024*1024)}MB")

        # Generate S3 key
        file_hash = hashlib.sha256(file_data).hexdigest()[:16]
        file_ext = file_name.split('.')[-1].lower()
        s3_key = f"branding/{tenant_id}/logos/{logo_type}_{file_hash}.{file_ext}"

        # Upload to S3
        upload_result = self.s3.upload_file(
            file_data=file_data,
            object_key=s3_key,
            content_type=content_type,
            metadata={
                'tenant_id': str(tenant_id),
                'logo_type': logo_type,
                'original_filename': file_name,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        )

        # Generate CDN URL
        cdn_url = self._generate_cdn_url(s3_key)

        # Store logo metadata in tenant settings (in production, use dedicated table)
        # For now, return metadata
        return {
            'logo_id': str(uuid4()),
            'logo_type': logo_type,
            's3_key': s3_key,
            'cdn_url': cdn_url,
            'file_name': file_name,
            'content_type': content_type,
            'file_size': len(file_data),
            'file_hash': file_hash,
            'uploaded_at': datetime.utcnow().isoformat()
        }

    def get_logo(
        self,
        tenant_id: UUID,
        logo_type: str = 'primary'
    ) -> Optional[Dict[str, Any]]:
        """
        Get logo metadata and URL

        Args:
            tenant_id: Tenant to query
            logo_type: Type of logo to retrieve

        Returns:
            Logo metadata if exists
        """
        # In production, query from database
        # For now, return mock data
        return {
            'logo_id': str(uuid4()),
            'logo_type': logo_type,
            'cdn_url': f'https://cdn.inetzero.com/branding/{tenant_id}/logos/{logo_type}.png',
            'uploaded_at': datetime.utcnow().isoformat()
        }

    def delete_logo(
        self,
        tenant_id: UUID,
        logo_type: str = 'primary'
    ) -> bool:
        """
        Delete logo from storage

        Args:
            tenant_id: Tenant to delete from
            logo_type: Type of logo to delete

        Returns:
            True if successful
        """
        # In production, delete from S3 and database
        # For now, return success
        return True

    # ============================================================================
    # COLOR SCHEME CUSTOMIZATION
    # ============================================================================

    def set_color_scheme(
        self,
        tenant_id: UUID,
        colors: Dict[str, str],
        updated_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Set custom color scheme for tenant

        Args:
            tenant_id: Tenant to customize
            colors: Dictionary of color values (hex codes)
            updated_by: User making the change

        Returns:
            Updated color scheme
        """
        # Validate color values
        for color_name, color_value in colors.items():
            if not self._is_valid_hex_color(color_value):
                raise ValueError(f"Invalid color value for '{color_name}': {color_value}")

        # Merge with defaults
        current_scheme = self.DEFAULT_THEME['colors'].copy()
        current_scheme.update(colors)

        # In production, store in database
        # For now, return the scheme
        return {
            'tenant_id': str(tenant_id),
            'colors': current_scheme,
            'updated_at': datetime.utcnow().isoformat(),
            'updated_by': str(updated_by) if updated_by else None
        }

    def get_color_scheme(self, tenant_id: UUID) -> Dict[str, str]:
        """
        Get current color scheme for tenant

        Args:
            tenant_id: Tenant to query

        Returns:
            Color scheme dictionary
        """
        # In production, query from database
        # For now, return default
        return self.DEFAULT_THEME['colors']

    def reset_color_scheme(self, tenant_id: UUID) -> Dict[str, str]:
        """Reset color scheme to defaults"""
        return self.DEFAULT_THEME['colors']

    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color code"""
        if not color.startswith('#'):
            return False

        hex_part = color[1:]
        if len(hex_part) not in [3, 6, 8]:
            return False

        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False

    # ============================================================================
    # TYPOGRAPHY & SPACING
    # ============================================================================

    def set_typography(
        self,
        tenant_id: UUID,
        typography: Dict[str, str],
        updated_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Set custom typography settings

        Args:
            tenant_id: Tenant to customize
            typography: Typography configuration
            updated_by: User making the change

        Returns:
            Updated typography config
        """
        # Merge with defaults
        current_typography = self.DEFAULT_THEME['typography'].copy()
        current_typography.update(typography)

        return {
            'tenant_id': str(tenant_id),
            'typography': current_typography,
            'updated_at': datetime.utcnow().isoformat(),
            'updated_by': str(updated_by) if updated_by else None
        }

    def get_typography(self, tenant_id: UUID) -> Dict[str, str]:
        """Get current typography settings"""
        # In production, query from database
        return self.DEFAULT_THEME['typography']

    # ============================================================================
    # EMAIL TEMPLATE BRANDING
    # ============================================================================

    def get_email_template(
        self,
        tenant_id: UUID,
        template_type: str
    ) -> Dict[str, Any]:
        """
        Get branded email template

        Args:
            tenant_id: Tenant to query
            template_type: Type of email (welcome, notification, report, etc.)

        Returns:
            Email template with branding applied
        """
        # Get tenant branding
        colors = self.get_color_scheme(tenant_id)
        logo = self.get_logo(tenant_id, 'primary')
        typography = self.get_typography(tenant_id)

        # Build email template
        template = {
            'template_type': template_type,
            'subject': self._get_email_subject(template_type),
            'html_body': self._generate_email_html(
                template_type=template_type,
                colors=colors,
                logo_url=logo['cdn_url'] if logo else None,
                typography=typography
            ),
            'text_body': self._generate_email_text(template_type)
        }

        return template

    def _get_email_subject(self, template_type: str) -> str:
        """Get email subject by template type"""
        subjects = {
            'welcome': 'Welcome to iNetZero',
            'notification': 'iNetZero Notification',
            'report_ready': 'Your Report is Ready',
            'threshold_breach': 'Threshold Breach Alert',
            'approval_request': 'Approval Request'
        }
        return subjects.get(template_type, 'iNetZero')

    def _generate_email_html(
        self,
        template_type: str,
        colors: Dict[str, str],
        logo_url: Optional[str],
        typography: Dict[str, str]
    ) -> str:
        """Generate branded HTML email"""
        logo_html = f'<img src="{logo_url}" alt="Logo" style="max-height: 50px;" />' if logo_url else ''

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: {typography.get('font_family', 'Inter, sans-serif')};
            font-size: {typography.get('font_size_base', '16px')};
            line-height: {typography.get('line_height_base', '1.5')};
            color: {colors.get('text_primary', '#111827')};
            background-color: {colors.get('surface', '#F9FAFB')};
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: {colors.get('background', '#FFFFFF')};
        }}
        .header {{
            padding: 24px;
            border-bottom: 1px solid {colors.get('border', '#E5E7EB')};
        }}
        .content {{
            padding: 24px;
        }}
        .footer {{
            padding: 24px;
            border-top: 1px solid {colors.get('border', '#E5E7EB')};
            font-size: 14px;
            color: {colors.get('text_secondary', '#6B7280')};
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: {colors.get('primary', '#3B82F6')};
            color: #FFFFFF;
            text-decoration: none;
            border-radius: 6px;
            font-weight: {typography.get('font_weight_semibold', '600')};
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {logo_html}
        </div>
        <div class="content">
            <p>Email content goes here...</p>
            <a href="#" class="button">Take Action</a>
        </div>
        <div class="footer">
            <p>Powered by iNetZero</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_email_text(self, template_type: str) -> str:
        """Generate plain text email"""
        return f"""
Email content in plain text format.

Powered by iNetZero
"""

    # ============================================================================
    # REPORT BRANDING
    # ============================================================================

    def get_report_branding(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Get branding configuration for reports

        Args:
            tenant_id: Tenant to query

        Returns:
            Report branding configuration
        """
        colors = self.get_color_scheme(tenant_id)
        logo = self.get_logo(tenant_id, 'primary')
        typography = self.get_typography(tenant_id)

        return {
            'logo_url': logo['cdn_url'] if logo else None,
            'colors': colors,
            'typography': typography,
            'report_footer': f"Generated by iNetZero - {datetime.utcnow().strftime('%Y-%m-%d')}",
            'watermark': None,  # Optional watermark for draft reports
            'page_numbering': True,
            'show_powered_by': True
        }

    # ============================================================================
    # WHITE-LABEL CONFIGURATION
    # ============================================================================

    def set_white_label_config(
        self,
        tenant_id: UUID,
        config: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Set white-label configuration

        Args:
            tenant_id: Tenant to configure
            config: White-label settings
            updated_by: User making the change

        Returns:
            Updated configuration
        """
        allowed_fields = [
            'show_powered_by',
            'powered_by_text',
            'custom_domain',
            'support_email',
            'support_url',
            'terms_url',
            'privacy_url',
            'custom_footer_text'
        ]

        # Filter config to allowed fields
        filtered_config = {k: v for k, v in config.items() if k in allowed_fields}

        # In production, store in database
        return {
            'tenant_id': str(tenant_id),
            'config': filtered_config,
            'updated_at': datetime.utcnow().isoformat(),
            'updated_by': str(updated_by) if updated_by else None
        }

    def get_white_label_config(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get white-label configuration for tenant"""
        # In production, query from database
        return {
            'show_powered_by': True,
            'powered_by_text': 'Powered by iNetZero',
            'custom_domain': None,
            'support_email': 'support@inetzero.com',
            'support_url': 'https://inetzero.com/support',
            'terms_url': 'https://inetzero.com/terms',
            'privacy_url': 'https://inetzero.com/privacy',
            'custom_footer_text': None
        }

    # ============================================================================
    # THEME EXPORT/IMPORT
    # ============================================================================

    def export_theme(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Export complete theme configuration

        Args:
            tenant_id: Tenant to export

        Returns:
            Complete theme configuration
        """
        return {
            'version': '1.0',
            'tenant_id': str(tenant_id),
            'colors': self.get_color_scheme(tenant_id),
            'typography': self.get_typography(tenant_id),
            'logos': {
                'primary': self.get_logo(tenant_id, 'primary'),
                'favicon': self.get_logo(tenant_id, 'favicon')
            },
            'white_label': self.get_white_label_config(tenant_id),
            'exported_at': datetime.utcnow().isoformat()
        }

    def import_theme(
        self,
        tenant_id: UUID,
        theme_config: Dict[str, Any],
        imported_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Import theme configuration

        Args:
            tenant_id: Tenant to import to
            theme_config: Theme configuration to import
            imported_by: User performing the import

        Returns:
            Import result
        """
        # Validate version
        if theme_config.get('version') != '1.0':
            raise ValueError("Unsupported theme version")

        # Import colors
        if 'colors' in theme_config:
            self.set_color_scheme(tenant_id, theme_config['colors'], imported_by)

        # Import typography
        if 'typography' in theme_config:
            self.set_typography(tenant_id, theme_config['typography'], imported_by)

        # Import white-label config
        if 'white_label' in theme_config:
            self.set_white_label_config(tenant_id, theme_config['white_label'], imported_by)

        return {
            'status': 'success',
            'tenant_id': str(tenant_id),
            'imported_at': datetime.utcnow().isoformat(),
            'imported_by': str(imported_by) if imported_by else None
        }

    # ============================================================================
    # CDN MANAGEMENT
    # ============================================================================

    def _generate_cdn_url(self, s3_key: str) -> str:
        """Generate CDN URL for S3 object"""
        # In production, this would use CloudFront or similar CDN
        return f"https://cdn.inetzero.com/{s3_key}"

    def invalidate_cdn_cache(
        self,
        tenant_id: UUID,
        paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Invalidate CDN cache for branding assets

        Args:
            tenant_id: Tenant whose assets to invalidate
            paths: Specific paths to invalidate (None = all)

        Returns:
            Invalidation result
        """
        # In production, this would call CloudFront invalidation API
        invalidation_paths = paths or [
            f"/branding/{tenant_id}/*"
        ]

        return {
            'invalidation_id': str(uuid4()),
            'paths': invalidation_paths,
            'status': 'in_progress',
            'created_at': datetime.utcnow().isoformat()
        }

    # ============================================================================
    # PREVIEW GENERATION
    # ============================================================================

    def generate_preview_html(self, tenant_id: UUID) -> str:
        """
        Generate HTML preview of current branding

        Args:
            tenant_id: Tenant to preview

        Returns:
            HTML preview page
        """
        colors = self.get_color_scheme(tenant_id)
        logo = self.get_logo(tenant_id, 'primary')
        typography = self.get_typography(tenant_id)

        logo_html = f'<img src="{logo["cdn_url"]}" alt="Logo" style="max-height: 50px;" />' if logo else '<div style="font-size: 24px; font-weight: bold;">Your Logo</div>'

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Branding Preview</title>
    <style>
        body {{
            font-family: {typography.get('font_family', 'Inter, sans-serif')};
            margin: 0;
            padding: 0;
            background-color: {colors.get('surface', '#F9FAFB')};
        }}
        .header {{
            background-color: {colors.get('background', '#FFFFFF')};
            padding: 16px 24px;
            border-bottom: 1px solid {colors.get('border', '#E5E7EB')};
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }}
        .card {{
            background-color: {colors.get('background', '#FFFFFF')};
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            border: 1px solid {colors.get('border', '#E5E7EB')};
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: {colors.get('primary', '#3B82F6')};
            color: #FFFFFF;
            text-decoration: none;
            border-radius: 6px;
            font-weight: {typography.get('font_weight_semibold', '600')};
            border: none;
            cursor: pointer;
        }}
        .button.secondary {{
            background-color: {colors.get('secondary', '#10B981')};
        }}
        h1 {{ color: {colors.get('text_primary', '#111827')}; }}
        p {{ color: {colors.get('text_secondary', '#6B7280')}; }}
    </style>
</head>
<body>
    <div class="header">
        {logo_html}
    </div>
    <div class="container">
        <h1>Branding Preview</h1>
        <div class="card">
            <h2>Primary Button</h2>
            <button class="button">Primary Action</button>
            <button class="button secondary">Secondary Action</button>
        </div>
        <div class="card">
            <h2>Typography</h2>
            <h1>Heading 1</h1>
            <h2>Heading 2</h2>
            <p>This is paragraph text with the configured typography.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
