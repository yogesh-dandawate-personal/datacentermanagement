"""Add analytics and reporting tables for Sprint 9

Revision ID: 007_analytics_reporting
Revises: 005_add_agent_audit_tables
Create Date: 2024-03-10

Sprint 9: Advanced Analytics & Reporting
- Emissions trends with forecasting
- Energy analysis and pattern detection
- Water usage tracking
- Waste metrics
- Sustainability scoring
- Scheduled reports
- Report templates
- Report distribution
- Benchmarking (industry, peer)
- Notification system (email, Slack, SMS, webhook)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers
revision = '007_analytics_reporting'
down_revision = '005_add_agent_audit_tables'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================================
    # ANALYTICS TABLES
    # ============================================================================

    # Emissions trends table
    op.create_table(
        'emissions_trends',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('trend_date', sa.DateTime, nullable=False, index=True),
        sa.Column('period_type', sa.String(50), nullable=False, index=True),
        sa.Column('scope_1', sa.Numeric(18, 6), default=0),
        sa.Column('scope_2', sa.Numeric(18, 6), default=0),
        sa.Column('scope_3', sa.Numeric(18, 6), default=0),
        sa.Column('total_emissions', sa.Numeric(18, 6), default=0),
        sa.Column('forecast_scope_1', sa.Numeric(18, 6)),
        sa.Column('forecast_scope_2', sa.Numeric(18, 6)),
        sa.Column('forecast_scope_3', sa.Numeric(18, 6)),
        sa.Column('forecast_total', sa.Numeric(18, 6)),
        sa.Column('forecast_confidence', sa.Numeric(5, 2)),
        sa.Column('trend_direction', sa.String(20)),
        sa.Column('percentage_change', sa.Numeric(8, 2)),
        sa.Column('anomaly_detected', sa.Boolean, default=False),
        sa.Column('anomaly_severity', sa.String(20)),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Energy analysis table
    op.create_table(
        'energy_analysis',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('analysis_date', sa.DateTime, nullable=False, index=True),
        sa.Column('period_start', sa.DateTime, nullable=False),
        sa.Column('period_end', sa.DateTime, nullable=False),
        sa.Column('total_consumption', sa.Numeric(18, 6), nullable=False),
        sa.Column('peak_demand', sa.Numeric(18, 6)),
        sa.Column('average_demand', sa.Numeric(18, 6)),
        sa.Column('load_factor', sa.Numeric(5, 2)),
        sa.Column('peak_hours', JSON),
        sa.Column('off_peak_hours', JSON),
        sa.Column('seasonal_pattern', sa.String(50)),
        sa.Column('anomalies_detected', sa.Integer, default=0),
        sa.Column('anomaly_details', JSON),
        sa.Column('optimization_score', sa.Numeric(5, 2)),
        sa.Column('potential_savings_kwh', sa.Numeric(18, 6)),
        sa.Column('potential_savings_usd', sa.Numeric(18, 2)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Water usage table
    op.create_table(
        'water_usage',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('facility_id', UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('measurement_date', sa.DateTime, nullable=False, index=True),
        sa.Column('period_type', sa.String(50), nullable=False),
        sa.Column('total_volume', sa.Numeric(18, 6), nullable=False),
        sa.Column('cooling_water', sa.Numeric(18, 6)),
        sa.Column('potable_water', sa.Numeric(18, 6)),
        sa.Column('recycled_water', sa.Numeric(18, 6)),
        sa.Column('wue_ratio', sa.Numeric(8, 4)),
        sa.Column('recycling_rate', sa.Numeric(5, 2)),
        sa.Column('waste_water_volume', sa.Numeric(18, 6)),
        sa.Column('trend_direction', sa.String(20)),
        sa.Column('percentage_change', sa.Numeric(8, 2)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Waste metrics table
    op.create_table(
        'waste_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('facility_id', UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('measurement_date', sa.DateTime, nullable=False, index=True),
        sa.Column('period_type', sa.String(50), nullable=False),
        sa.Column('total_waste', sa.Numeric(18, 6), nullable=False),
        sa.Column('e_waste', sa.Numeric(18, 6)),
        sa.Column('general_waste', sa.Numeric(18, 6)),
        sa.Column('hazardous_waste', sa.Numeric(18, 6)),
        sa.Column('recycled_waste', sa.Numeric(18, 6)),
        sa.Column('landfill_waste', sa.Numeric(18, 6)),
        sa.Column('recycling_rate', sa.Numeric(5, 2)),
        sa.Column('diversion_rate', sa.Numeric(5, 2)),
        sa.Column('disposal_cost', sa.Numeric(12, 2)),
        sa.Column('recycling_revenue', sa.Numeric(12, 2)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Sustainability scores table
    op.create_table(
        'sustainability_scores',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('score_date', sa.DateTime, nullable=False, index=True),
        sa.Column('score_period', sa.String(50), nullable=False),
        sa.Column('overall_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('environmental_score', sa.Numeric(5, 2)),
        sa.Column('social_score', sa.Numeric(5, 2)),
        sa.Column('governance_score', sa.Numeric(5, 2)),
        sa.Column('emissions_score', sa.Numeric(5, 2)),
        sa.Column('energy_score', sa.Numeric(5, 2)),
        sa.Column('water_score', sa.Numeric(5, 2)),
        sa.Column('waste_score', sa.Numeric(5, 2)),
        sa.Column('score_calculation', JSON),
        sa.Column('improvement_areas', JSON),
        sa.Column('strengths', JSON),
        sa.Column('percentile_rank', sa.Integer),
        sa.Column('industry_average', sa.Numeric(5, 2)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Optimization opportunities table
    op.create_table(
        'optimization_opportunities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('opportunity_type', sa.String(100), nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('priority', sa.String(20), nullable=False, index=True),
        sa.Column('estimated_savings_usd', sa.Numeric(18, 2)),
        sa.Column('estimated_savings_kwh', sa.Numeric(18, 6)),
        sa.Column('estimated_emissions_reduction', sa.Numeric(18, 6)),
        sa.Column('implementation_effort', sa.String(20)),
        sa.Column('implementation_cost', sa.Numeric(18, 2)),
        sa.Column('payback_period_months', sa.Integer),
        sa.Column('status', sa.String(50), default='identified', index=True),
        sa.Column('assigned_to', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('identified_at', sa.DateTime, nullable=False, index=True),
        sa.Column('implemented_at', sa.DateTime),
        sa.Column('implementation_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # ============================================================================
    # ADVANCED REPORTING TABLES
    # ============================================================================

    # Report templates advanced
    op.create_table(
        'report_templates_advanced',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('template_name', sa.String(255), nullable=False, index=True),
        sa.Column('template_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('sections', JSON, nullable=False),
        sa.Column('data_sources', JSON),
        sa.Column('charts', JSON),
        sa.Column('page_layout', JSON),
        sa.Column('branding', JSON),
        sa.Column('is_default', sa.Boolean, default=False),
        sa.Column('is_public', sa.Boolean, default=False),
        sa.Column('category', sa.String(100)),
        sa.Column('tags', JSON),
        sa.Column('usage_count', sa.Integer, default=0),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Scheduled reports table
    op.create_table(
        'scheduled_reports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('report_templates_advanced.id', ondelete='SET NULL'), nullable=True),
        sa.Column('schedule_name', sa.String(255), nullable=False, index=True),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('schedule_cron', sa.String(100), nullable=False),
        sa.Column('schedule_timezone', sa.String(50), default='UTC'),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('report_config', JSON, default={}),
        sa.Column('include_sections', JSON),
        sa.Column('delivery_channels', JSON),
        sa.Column('formats', JSON),
        sa.Column('last_run_at', sa.DateTime, index=True),
        sa.Column('next_run_at', sa.DateTime, index=True),
        sa.Column('last_run_status', sa.String(50)),
        sa.Column('failure_count', sa.Integer, default=0),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Report distribution table
    op.create_table(
        'report_distributions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('distribution_name', sa.String(255), nullable=False),
        sa.Column('distribution_type', sa.String(50), nullable=False, index=True),
        sa.Column('email_recipients', JSON),
        sa.Column('email_subject_template', sa.String(500)),
        sa.Column('email_body_template', sa.Text),
        sa.Column('slack_webhook_url', sa.String(500)),
        sa.Column('slack_channel', sa.String(100)),
        sa.Column('slack_message_template', sa.Text),
        sa.Column('webhook_url', sa.String(500)),
        sa.Column('webhook_method', sa.String(10), default='POST'),
        sa.Column('webhook_headers', JSON),
        sa.Column('sftp_host', sa.String(255)),
        sa.Column('sftp_port', sa.Integer, default=22),
        sa.Column('sftp_username', sa.String(100)),
        sa.Column('sftp_password', sa.String(500)),
        sa.Column('sftp_path', sa.String(500)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Report delivery logs table
    op.create_table(
        'report_delivery_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('scheduled_report_id', UUID(as_uuid=True), sa.ForeignKey('scheduled_reports.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('report_id', UUID(as_uuid=True), sa.ForeignKey('reports.id', ondelete='SET NULL'), nullable=True),
        sa.Column('delivery_attempt_at', sa.DateTime, nullable=False, index=True),
        sa.Column('delivery_status', sa.String(50), nullable=False, index=True),
        sa.Column('delivery_channel', sa.String(50)),
        sa.Column('recipients', JSON),
        sa.Column('files_delivered', JSON),
        sa.Column('http_status_code', sa.Integer),
        sa.Column('response_time_ms', sa.Integer),
        sa.Column('error_message', sa.Text),
        sa.Column('error_details', JSON),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('max_retries', sa.Integer, default=3),
        sa.Column('next_retry_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, nullable=False)
    )

    # Report generation history table
    op.create_table(
        'report_generation_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('scheduled_report_id', UUID(as_uuid=True), sa.ForeignKey('scheduled_reports.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('report_id', UUID(as_uuid=True), sa.ForeignKey('reports.id', ondelete='SET NULL'), nullable=True),
        sa.Column('generation_started_at', sa.DateTime, nullable=False, index=True),
        sa.Column('generation_completed_at', sa.DateTime),
        sa.Column('generation_duration_ms', sa.Integer),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('report_period_start', sa.DateTime),
        sa.Column('report_period_end', sa.DateTime),
        sa.Column('data_points_processed', sa.Integer),
        sa.Column('query_time_ms', sa.Integer),
        sa.Column('render_time_ms', sa.Integer),
        sa.Column('export_time_ms', sa.Integer),
        sa.Column('output_formats', JSON),
        sa.Column('output_files', JSON),
        sa.Column('error_message', sa.Text),
        sa.Column('error_stacktrace', sa.Text),
        sa.Column('triggered_by', sa.String(50)),
        sa.Column('triggered_by_user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False)
    )

    # ============================================================================
    # BENCHMARKING TABLES
    # ============================================================================

    # Benchmarks table
    op.create_table(
        'benchmarks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('benchmark_name', sa.String(255), nullable=False, index=True),
        sa.Column('metric_type', sa.String(100), nullable=False, index=True),
        sa.Column('industry', sa.String(100), index=True),
        sa.Column('sector', sa.String(100)),
        sa.Column('region', sa.String(100), index=True),
        sa.Column('organization_size', sa.String(50)),
        sa.Column('average_value', sa.Numeric(18, 6), nullable=False),
        sa.Column('median_value', sa.Numeric(18, 6)),
        sa.Column('best_in_class', sa.Numeric(18, 6)),
        sa.Column('worst_in_class', sa.Numeric(18, 6)),
        sa.Column('percentile_25', sa.Numeric(18, 6)),
        sa.Column('percentile_50', sa.Numeric(18, 6)),
        sa.Column('percentile_75', sa.Numeric(18, 6)),
        sa.Column('percentile_90', sa.Numeric(18, 6)),
        sa.Column('unit', sa.String(50)),
        sa.Column('sample_size', sa.Integer),
        sa.Column('data_year', sa.Integer, nullable=False, index=True),
        sa.Column('data_quarter', sa.Integer),
        sa.Column('source_name', sa.String(255)),
        sa.Column('source_url', sa.String(500)),
        sa.Column('confidence_level', sa.Numeric(5, 2)),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Peer groups table
    op.create_table(
        'peer_groups',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('group_name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('industry', sa.String(100)),
        sa.Column('sector', sa.String(100)),
        sa.Column('region', sa.String(100)),
        sa.Column('size_range', sa.String(50)),
        sa.Column('custom_criteria', JSON),
        sa.Column('member_organizations', JSON),
        sa.Column('member_count', sa.Integer, default=0),
        sa.Column('avg_performance', JSON),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_public', sa.Boolean, default=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Comparison results table
    op.create_table(
        'comparison_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('benchmark_id', UUID(as_uuid=True), sa.ForeignKey('benchmarks.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('comparison_date', sa.DateTime, nullable=False, index=True),
        sa.Column('period_start', sa.DateTime, nullable=False),
        sa.Column('period_end', sa.DateTime, nullable=False),
        sa.Column('organization_value', sa.Numeric(18, 6), nullable=False),
        sa.Column('organization_percentile', sa.Integer),
        sa.Column('vs_average_delta', sa.Numeric(18, 6)),
        sa.Column('vs_average_percent', sa.Numeric(8, 2)),
        sa.Column('vs_median_delta', sa.Numeric(18, 6)),
        sa.Column('vs_median_percent', sa.Numeric(8, 2)),
        sa.Column('vs_best_in_class_delta', sa.Numeric(18, 6)),
        sa.Column('vs_best_in_class_percent', sa.Numeric(8, 2)),
        sa.Column('performance_rating', sa.String(50), index=True),
        sa.Column('rating_description', sa.Text),
        sa.Column('peer_group_id', UUID(as_uuid=True), sa.ForeignKey('peer_groups.id', ondelete='SET NULL'), nullable=True),
        sa.Column('peer_rank', sa.Integer),
        sa.Column('peer_count', sa.Integer),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Benchmark gaps table
    op.create_table(
        'benchmark_gaps',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('comparison_result_id', UUID(as_uuid=True), sa.ForeignKey('comparison_results.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('gap_type', sa.String(100), nullable=False, index=True),
        sa.Column('current_value', sa.Numeric(18, 6), nullable=False),
        sa.Column('target_value', sa.Numeric(18, 6), nullable=False),
        sa.Column('gap_value', sa.Numeric(18, 6), nullable=False),
        sa.Column('gap_percentage', sa.Numeric(8, 2), nullable=False),
        sa.Column('improvement_required', sa.Numeric(18, 6)),
        sa.Column('estimated_timeline_months', sa.Integer),
        sa.Column('difficulty_level', sa.String(20)),
        sa.Column('recommendations', JSON),
        sa.Column('estimated_investment', sa.Numeric(18, 2)),
        sa.Column('estimated_annual_savings', sa.Numeric(18, 2)),
        sa.Column('roi_months', sa.Integer),
        sa.Column('status', sa.String(50), default='identified', index=True),
        sa.Column('progress_percentage', sa.Integer, default=0),
        sa.Column('assigned_to', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Benchmark alerts table
    op.create_table(
        'benchmark_alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('comparison_result_id', UUID(as_uuid=True), sa.ForeignKey('comparison_results.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('alert_type', sa.String(100), nullable=False, index=True),
        sa.Column('alert_severity', sa.String(20), nullable=False, index=True),
        sa.Column('alert_message', sa.Text, nullable=False),
        sa.Column('metric_name', sa.String(100)),
        sa.Column('current_value', sa.Numeric(18, 6)),
        sa.Column('benchmark_value', sa.Numeric(18, 6)),
        sa.Column('deviation_percent', sa.Numeric(8, 2)),
        sa.Column('is_sent', sa.Boolean, default=False),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('acknowledged_at', sa.DateTime),
        sa.Column('acknowledged_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('resolution_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True)
    )

    # ============================================================================
    # NOTIFICATION SYSTEM TABLES
    # ============================================================================

    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('notification_type', sa.String(100), nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('message_html', sa.Text),
        sa.Column('source_entity_type', sa.String(100)),
        sa.Column('source_entity_id', UUID(as_uuid=True)),
        sa.Column('related_data', JSON),
        sa.Column('priority', sa.String(20), nullable=False, default='medium', index=True),
        sa.Column('urgency', sa.String(20), default='normal'),
        sa.Column('severity', sa.String(20)),
        sa.Column('delivery_channels', JSON, default=[]),
        sa.Column('recipients', JSON),
        sa.Column('status', sa.String(50), default='pending', index=True),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('acknowledged_at', sa.DateTime),
        sa.Column('acknowledged_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('resolved_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('resolution_notes', sa.Text),
        sa.Column('auto_resolve', sa.Boolean, default=False),
        sa.Column('auto_resolved', sa.Boolean, default=False),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('tags', JSON),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Notification preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('email_enabled', sa.Boolean, default=True),
        sa.Column('email_address', sa.String(255)),
        sa.Column('email_digest', sa.Boolean, default=False),
        sa.Column('email_digest_time', sa.String(5)),
        sa.Column('slack_enabled', sa.Boolean, default=False),
        sa.Column('slack_user_id', sa.String(255)),
        sa.Column('slack_channel', sa.String(100)),
        sa.Column('sms_enabled', sa.Boolean, default=False),
        sa.Column('sms_phone_number', sa.String(20)),
        sa.Column('webhook_enabled', sa.Boolean, default=False),
        sa.Column('webhook_url', sa.String(500)),
        sa.Column('notification_types', JSON, default={}),
        sa.Column('minimum_priority', sa.String(20), default='low'),
        sa.Column('critical_only_off_hours', sa.Boolean, default=True),
        sa.Column('quiet_hours_enabled', sa.Boolean, default=False),
        sa.Column('quiet_hours_start', sa.String(5)),
        sa.Column('quiet_hours_end', sa.String(5)),
        sa.Column('quiet_hours_timezone', sa.String(50), default='UTC'),
        sa.Column('max_notifications_per_hour', sa.Integer, default=10),
        sa.Column('max_notifications_per_day', sa.Integer, default=100),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Notification logs table
    op.create_table(
        'notification_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('notification_id', UUID(as_uuid=True), sa.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('delivery_channel', sa.String(50), nullable=False, index=True),
        sa.Column('recipient', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('attempt_count', sa.Integer, default=1),
        sa.Column('max_attempts', sa.Integer, default=3),
        sa.Column('queued_at', sa.DateTime, nullable=False),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('delivered_at', sa.DateTime),
        sa.Column('failed_at', sa.DateTime),
        sa.Column('http_status_code', sa.Integer),
        sa.Column('response_message', sa.Text),
        sa.Column('response_time_ms', sa.Integer),
        sa.Column('error_message', sa.Text),
        sa.Column('error_code', sa.String(50)),
        sa.Column('retry_scheduled_at', sa.DateTime),
        sa.Column('external_id', sa.String(255)),
        sa.Column('tracking_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True)
    )

    # Notification channels table
    op.create_table(
        'notification_channels',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('channel_name', sa.String(255), nullable=False),
        sa.Column('channel_type', sa.String(50), nullable=False, index=True),
        sa.Column('smtp_host', sa.String(255)),
        sa.Column('smtp_port', sa.Integer, default=587),
        sa.Column('smtp_username', sa.String(255)),
        sa.Column('smtp_password', sa.String(500)),
        sa.Column('smtp_use_tls', sa.Boolean, default=True),
        sa.Column('smtp_from_email', sa.String(255)),
        sa.Column('smtp_from_name', sa.String(255)),
        sa.Column('sendgrid_api_key', sa.String(500)),
        sa.Column('sendgrid_from_email', sa.String(255)),
        sa.Column('slack_webhook_url', sa.String(500)),
        sa.Column('slack_bot_token', sa.String(500)),
        sa.Column('slack_default_channel', sa.String(100)),
        sa.Column('twilio_account_sid', sa.String(255)),
        sa.Column('twilio_auth_token', sa.String(500)),
        sa.Column('twilio_from_number', sa.String(20)),
        sa.Column('sns_access_key', sa.String(255)),
        sa.Column('sns_secret_key', sa.String(500)),
        sa.Column('sns_region', sa.String(50)),
        sa.Column('webhook_url', sa.String(500)),
        sa.Column('webhook_method', sa.String(10), default='POST'),
        sa.Column('webhook_headers', JSON),
        sa.Column('webhook_auth_type', sa.String(50)),
        sa.Column('rate_limit_per_minute', sa.Integer, default=60),
        sa.Column('rate_limit_per_hour', sa.Integer, default=1000),
        sa.Column('rate_limit_per_day', sa.Integer, default=10000),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('is_healthy', sa.Boolean, default=True),
        sa.Column('last_health_check', sa.DateTime),
        sa.Column('consecutive_failures', sa.Integer, default=0),
        sa.Column('total_sent', sa.Integer, default=0),
        sa.Column('total_failed', sa.Integer, default=0),
        sa.Column('last_sent_at', sa.DateTime),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Notification templates table
    op.create_table(
        'notification_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('template_name', sa.String(255), nullable=False, index=True),
        sa.Column('template_type', sa.String(100), nullable=False),
        sa.Column('subject_template', sa.String(500)),
        sa.Column('message_template', sa.Text, nullable=False),
        sa.Column('message_html_template', sa.Text),
        sa.Column('slack_blocks_template', JSON),
        sa.Column('required_variables', JSON),
        sa.Column('optional_variables', JSON),
        sa.Column('is_default', sa.Boolean, default=False),
        sa.Column('usage_count', sa.Integer, default=0),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # ============================================================================
    # INDEXES FOR PERFORMANCE (Time-series and analytics queries)
    # ============================================================================

    # Emissions trends indexes
    op.create_index('idx_emissions_trends_org_date', 'emissions_trends', ['organization_id', 'trend_date'])
    op.create_index('idx_emissions_trends_period', 'emissions_trends', ['period_type', 'trend_date'])

    # Energy analysis indexes
    op.create_index('idx_energy_analysis_org_period', 'energy_analysis', ['organization_id', 'period_start', 'period_end'])

    # Benchmarking indexes
    op.create_index('idx_benchmarks_composite', 'benchmarks', ['metric_type', 'industry', 'region', 'data_year'])
    op.create_index('idx_comparison_results_org_date', 'comparison_results', ['organization_id', 'comparison_date'])

    # Notification indexes
    op.create_index('idx_notifications_status_created', 'notifications', ['status', 'created_at'])
    op.create_index('idx_notification_logs_channel_status', 'notification_logs', ['delivery_channel', 'status'])

    # Scheduled reports indexes
    op.create_index('idx_scheduled_reports_next_run', 'scheduled_reports', ['is_active', 'next_run_at'])


def downgrade():
    # Drop tables in reverse order (children first due to foreign keys)
    op.drop_table('notification_templates')
    op.drop_table('notification_channels')
    op.drop_table('notification_logs')
    op.drop_table('notification_preferences')
    op.drop_table('notifications')

    op.drop_table('benchmark_alerts')
    op.drop_table('benchmark_gaps')
    op.drop_table('comparison_results')
    op.drop_table('peer_groups')
    op.drop_table('benchmarks')

    op.drop_table('report_generation_history')
    op.drop_table('report_delivery_logs')
    op.drop_table('report_distributions')
    op.drop_table('scheduled_reports')
    op.drop_table('report_templates_advanced')

    op.drop_table('optimization_opportunities')
    op.drop_table('sustainability_scores')
    op.drop_table('waste_metrics')
    op.drop_table('water_usage')
    op.drop_table('energy_analysis')
    op.drop_table('emissions_trends')
