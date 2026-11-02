-- KCo Database Initialization
-- Old But Gold TR8 IVSTO
-- PostgreSQL 15+

-- Create database if not exists
CREATE DATABASE kco_production;

-- Connect to database
\c kco_production

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS ml;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
SET search_path TO public, ml, analytics;

-- ==================== CORE TABLES ====================

-- Countries
CREATE TABLE IF NOT EXISTS countries (
    code VARCHAR(2) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert countries
INSERT INTO countries (code, name, currency, timezone) VALUES
    ('br', 'Brazil', 'BRL', 'America/Sao_Paulo'),
    ('mx', 'Mexico', 'MXN', 'America/Mexico_City')
    ON CONFLICT (code) DO NOTHING;

-- Vehicle Brands
CREATE TABLE IF NOT EXISTS vehicle_brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) REFERENCES countries(code),
    logo_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vehicle Models
CREATE TABLE IF NOT EXISTS vehicle_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES vehicle_brands(id),
    name VARCHAR(100) NOT NULL,
    year_start INTEGER,
    year_end INTEGER,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vin VARCHAR(17) UNIQUE,
    license_plate VARCHAR(20),
    brand_id UUID REFERENCES vehicle_brands(id),
    model_id UUID REFERENCES vehicle_models(id),
    year INTEGER,
    color VARCHAR(50),
    country_code VARCHAR(2) REFERENCES countries(code),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'retired', 'sold')),
    
    -- Fleet information
    fleet_id VARCHAR(50),
    subscription_plan VARCHAR(50) DEFAULT 'standard',
    monthly_cost DECIMAL(10, 2),
    
    -- Instrumentation
    is_instrumented BOOLEAN DEFAULT FALSE,
    instrumentation_date TIMESTAMP WITH TIME ZONE,
    telemetry_enabled BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vehicles
CREATE INDEX IF NOT EXISTS idx_vehicles_country ON vehicles(country_code);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_vin ON vehicles(vin);
CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate ON vehicles(license_plate);

-- Telemetry Data
CREATE TABLE IF NOT EXISTS telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Location
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    altitude DECIMAL(10, 2),
    speed DECIMAL(10, 2),
    heading DECIMAL(10, 2),
    
    -- Engine
    engine_rpm DECIMAL(10, 2),
    engine_temperature DECIMAL(10, 2),
    engine_load DECIMAL(5, 2),
    throttle_position DECIMAL(5, 2),
    
    -- Fluids
    oil_pressure DECIMAL(10, 2),
    oil_temperature DECIMAL(10, 2),
    fuel_level DECIMAL(5, 2),
    fuel_pressure DECIMAL(10, 2),
    
    -- Electrical
    battery_voltage DECIMAL(5, 2),
    alternator_voltage DECIMAL(5, 2),
    
    -- Vibration
    vibration_x DECIMAL(10, 4),
    vibration_y DECIMAL(10, 4),
    vibration_z DECIMAL(10, 4),
    
    -- OBD-II
    obd_codes TEXT[],
    
    -- Environment
    ambient_temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Index
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for telemetry
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle ON telemetry(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_timestamp ON telemetry(vehicle_id, timestamp);

-- Anomalies
CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    telemetry_id UUID REFERENCES telemetry(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Anomaly details
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'low' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    value DECIMAL(20, 4),
    threshold DECIMAL(20, 4),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Resolution
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for anomalies
CREATE INDEX IF NOT EXISTS idx_anomalies_vehicle ON anomalies(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_resolved ON anomalies(is_resolved);

-- Image Analysis
CREATE TABLE IF NOT EXISTS images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    image_url VARCHAR(500),
    image_path VARCHAR(500),
    image_hash VARCHAR(64),
    
    -- Image metadata
    width INTEGER,
    height INTEGER,
    format VARCHAR(20),
    size_bytes BIGINT,
    
    -- Processing
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(20) DEFAULT 'pending',
    
    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Image Analysis Results
CREATE TABLE IF NOT EXISTS image_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Detection results
    detected_objects JSONB DEFAULT '[]',
    anomalies JSONB DEFAULT '[]',
    damage_assessment JSONB DEFAULT '{}',
    
    -- Processing metadata
    processing_time_ms DECIMAL(10, 2),
    confidence_score DECIMAL(5, 4),
    model_version VARCHAR(50),
    
    -- Categories
    categories JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for image analysis
CREATE INDEX IF NOT EXISTS idx_image_analysis_image ON image_analysis(image_id);
CREATE INDEX IF NOT EXISTS idx_image_analysis_vehicle ON image_analysis(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_image_analysis_timestamp ON image_analysis(analysis_timestamp);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    
    -- Company
    company_id UUID,
    company_name VARCHAR(200),
    department VARCHAR(100),
    position VARCHAR(100),
    
    -- Preferences
    country_code VARCHAR(2) DEFAULT 'br',
    language VARCHAR(10) DEFAULT 'pt',
    timezone VARCHAR(50),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);

-- Companies
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    cnpj VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country_code VARCHAR(2) REFERENCES countries(code),
    zip_code VARCHAR(20),
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- Subscription
    subscription_plan VARCHAR(50) DEFAULT 'standard',
    subscription_status VARCHAR(20) DEFAULT 'active',
    subscription_start_date TIMESTAMP WITH TIME ZONE,
    subscription_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Maintenance Records
CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    
    -- Maintenance details
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    cost DECIMAL(10, 2),
    parts_replaced TEXT[],
    labor_hours DECIMAL(10, 2),
    
    -- Scheduling
    scheduled_date TIMESTAMP WITH TIME ZONE,
    completed_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    
    -- Provider
    provider_id UUID,
    provider_name VARCHAR(200),
    provider_contact VARCHAR(100),
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for maintenance
CREATE INDEX IF NOT EXISTS idx_maintenance_vehicle ON maintenance_records(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance_records(status);
CREATE INDEX IF NOT EXISTS idx_maintenance_date ON maintenance_records(scheduled_date);

-- LOWDATAESC Sync Log
CREATE TABLE IF NOT EXISTS lowdataesc_sync_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_type VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    record_id UUID,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    request_data JSONB,
    response_data JSONB,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for sync log
CREATE INDEX IF NOT EXISTS idx_lowdataesc_sync_type ON lowdataesc_sync_log(sync_type);
CREATE INDEX IF NOT EXISTS idx_lowdataesc_status ON lowdataesc_sync_log(status);
CREATE INDEX IF NOT EXISTS idx_lowdataesc_timestamp ON lowdataesc_sync_log(created_at);

-- ==================== ML SCHEMA ====================

-- ML Models
CREATE TABLE IF NOT EXISTS ml.models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Model files
    model_path VARCHAR(500),
    config_path VARCHAR(500),
    weights_path VARCHAR(500),
    
    -- Performance
    accuracy DECIMAL(5, 4),
    precision DECIMAL(5, 4),
    recall DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    
    -- Training metadata
    dataset_size INTEGER,
    training_time_seconds INTEGER,
    trained_by VARCHAR(100),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Training Runs
CREATE TABLE IF NOT EXISTS ml.training_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml.models(id),
    
    -- Run details
    run_name VARCHAR(100),
    parameters JSONB DEFAULT '{}',
    
    -- Metrics
    metrics JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Predictions
CREATE TABLE IF NOT EXISTS ml.predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml.models(id),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    telemetry_id UUID REFERENCES telemetry(id) ON DELETE SET NULL,
    image_id UUID REFERENCES images(id) ON DELETE SET NULL,
    
    -- Prediction data
    prediction JSONB DEFAULT '{}',
    confidence DECIMAL(5, 4),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ML tables
CREATE INDEX IF NOT EXISTS idx_ml_models_name ON ml.models(name);
CREATE INDEX IF NOT EXISTS idx_ml_models_type ON ml.models(model_type);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_model ON ml.predictions(model_id);

-- ==================== ANALYTICS SCHEMA ====================

-- Financial Metrics
CREATE TABLE IF NOT EXISTS analytics.financial_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    country_code VARCHAR(2) REFERENCES countries(code),
    
    -- Revenue
    total_revenue DECIMAL(15, 2),
    subscription_revenue DECIMAL(15, 2),
    licensing_revenue DECIMAL(15, 2),
    service_revenue DECIMAL(15, 2),
    
    -- Costs
    total_costs DECIMAL(15, 2),
    operational_costs DECIMAL(15, 2),
    maintenance_costs DECIMAL(15, 2),
    infrastructure_costs DECIMAL(15, 2),
    
    -- Metrics
    profit DECIMAL(15, 2),
    profit_margin DECIMAL(5, 4),
    roi DECIMAL(5, 4),
    
    -- Fleet metrics
    active_vehicles INTEGER,
    new_vehicles INTEGER,
    retired_vehicles INTEGER,
    
    -- User metrics
    active_users INTEGER,
    new_users INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for financial metrics
CREATE INDEX IF NOT EXISTS idx_analytics_financial_date ON analytics.financial_metrics(date);
CREATE INDEX IF NOT EXISTS idx_analytics_financial_country ON analytics.financial_metrics(country_code);

-- User Activity
CREATE TABLE IF NOT EXISTS analytics.user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    activity_data JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for user activity
CREATE INDEX IF NOT EXISTS idx_analytics_activity_user ON analytics.user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_activity_type ON analytics.user_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_analytics_activity_timestamp ON analytics.user_activity(created_at);

-- ==================== TRIGGERS ====================

-- Update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_vehicles_timestamp
    BEFORE UPDATE ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_telemetry_timestamp
    BEFORE UPDATE ON telemetry
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_anomalies_timestamp
    BEFORE UPDATE ON anomalies
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_companies_timestamp
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_maintenance_timestamp
    BEFORE UPDATE ON maintenance_records
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ==================== VIEWS ====================

-- Fleet Overview
CREATE OR REPLACE VIEW v_fleet_overview AS
SELECT 
    v.country_code,
    c.name AS country_name,
    COUNT(v.id) AS total_vehicles,
    COUNT(CASE WHEN v.status = 'active' THEN 1 END) AS active_vehicles,
    COUNT(CASE WHEN v.is_instrumented = TRUE THEN 1 END) AS instrumented_vehicles,
    AVG(v.monthly_cost) AS avg_monthly_cost,
    SUM(v.monthly_cost) AS total_monthly_cost
FROM vehicles v
JOIN countries c ON v.country_code = c.code
GROUP BY v.country_code, c.name;

-- Anomaly Statistics
CREATE OR REPLACE VIEW v_anomaly_stats AS
SELECT 
    a.vehicle_id,
    v.license_plate,
    v.make,
    v.model,
    a.anomaly_type,
    a.severity,
    COUNT(a.id) AS anomaly_count,
    MAX(a.timestamp) AS last_anomaly
FROM anomalies a
JOIN vehicles v ON a.vehicle_id = v.id
GROUP BY a.vehicle_id, v.license_plate, v.make, v.model, a.anomaly_type, a.severity;

-- Financial Summary
CREATE OR REPLACE VIEW v_financial_summary AS
SELECT 
    fm.date,
    fm.country_code,
    c.name AS country_name,
    fm.total_revenue,
    fm.total_costs,
    fm.profit,
    fm.profit_margin,
    fm.roi,
    fm.active_vehicles
FROM analytics.financial_metrics fm
JOIN countries c ON fm.country_code = c.code
ORDER BY fm.date DESC;

-- ==================== COMMENTS ====================

COMMENT ON TABLE vehicles IS 'Fleet vehicles with instrumentation and telemetry capabilities';
COMMENT ON TABLE telemetry IS 'Real-time vehicle telemetry data';
COMMENT ON TABLE anomalies IS 'Detected anomalies from telemetry and image analysis';
COMMENT ON TABLE images IS 'Vehicle images for analysis';
COMMENT ON TABLE image_analysis IS 'Results from image processing and analysis';
COMMENT ON TABLE users IS 'System users with access to the platform';
COMMENT ON TABLE companies IS 'Companies using the KCo platform';
COMMENT ON TABLE maintenance_records IS 'Vehicle maintenance history';
COMMENT ON TABLE lowdataesc_sync_log IS 'Log of data synchronization with LOWDATAESC';

-- ==================== SEED DATA ====================

-- Insert sample vehicle brands
INSERT INTO vehicle_brands (name, country_code, logo_url) VALUES
    ('Volkswagen', 'br', 'https://example.com/logos/vw.png'),
    ('Chevrolet', 'br', 'https://example.com/logos/chevrolet.png'),
    ('Fiat', 'br', 'https://example.com/logos/fiat.png'),
    ('Ford', 'br', 'https://example.com/logos/ford.png'),
    ('Nissan', 'mx', 'https://example.com/logos/nissan.png'),
    ('Volkswagen', 'mx', 'https://example.com/logos/vw.png'),
    ('Toyota', 'mx', 'https://example.com/logos/toyota.png')
    ON CONFLICT (name, country_code) DO NOTHING;

-- Insert sample vehicle models
INSERT INTO vehicle_models (brand_id, name, year_start, year_end, category) VALUES
    ((SELECT id FROM vehicle_brands WHERE name = 'Volkswagen' AND country_code = 'br'), 'Gol', 2020, 2024, 'Hatchback'),
    ((SELECT id FROM vehicle_brands WHERE name = 'Chevrolet' AND country_code = 'br'), 'Onix', 2019, 2024, 'Hatchback'),
    ((SELECT id FROM vehicle_brands WHERE name = 'Nissan' AND country_code = 'mx'), 'Versa', 2020, 2024, 'Sedan'),
    ((SELECT id FROM vehicle_brands WHERE name = 'Volkswagen' AND country_code = 'mx'), 'Jetta', 2019, 2024, 'Sedan')
    ON CONFLICT (brand_id, name, year_start) DO NOTHING;

-- Insert sample companies
INSERT INTO companies (name, cnpj, country_code, subscription_plan) VALUES
    ('Localiza', '00000000000191', 'br', 'enterprise'),
    ('Movida', '00000000000272', 'br', 'enterprise'),
    ('AXA Mexico', '00000000000353', 'mx', 'enterprise'),
    ('Banorte', '00000000000434', 'mx', 'enterprise')
    ON CONFLICT (name, country_code) DO NOTHING;

-- Insert sample vehicles
INSERT INTO vehicles (vin, license_plate, brand_id, model_id, year, country_code, status, is_instrumented, instrumentation_date, monthly_cost) VALUES
    ('9BWZZZ45Z7G123456', 'ABC1234', 
     (SELECT id FROM vehicle_brands WHERE name = 'Volkswagen' AND country_code = 'br'),
     (SELECT id FROM vehicle_models WHERE name = 'Gol' AND brand_id = (SELECT id FROM vehicle_brands WHERE name = 'Volkswagen' AND country_code = 'br')),
     2022, 'br', 'active', TRUE, NOW() - INTERVAL '6 months', 8500.00),
    ('9C2ZZZ45Z8G234567', 'DEF5678',
     (SELECT id FROM vehicle_brands WHERE name = 'Chevrolet' AND country_code = 'br'),
     (SELECT id FROM vehicle_models WHERE name = 'Onix' AND brand_id = (SELECT id FROM vehicle_brands WHERE name = 'Chevrolet' AND country_code = 'br')),
     2023, 'br', 'active', TRUE, NOW() - INTERVAL '4 months', 7500.00),
    ('3VWLL7AJ7BM123456', 'GHI9012',
     (SELECT id FROM vehicle_brands WHERE name = 'Nissan' AND country_code = 'mx'),
     (SELECT id FROM vehicle_models WHERE name = 'Versa' AND brand_id = (SELECT id FROM vehicle_brands WHERE name = 'Nissan' AND country_code = 'mx')),
     2022, 'mx', 'active', TRUE, NOW() - INTERVAL '3 months', 12000.00),
    ('3VWLL7AJ8CM234567', 'JKL3456',
     (SELECT id FROM vehicle_brands WHERE name = 'Volkswagen' AND country_code = 'mx'),
     (SELECT id FROM vehicle_models WHERE name = 'Jetta' AND brand_id = (SELECT id FROM vehicle_brands WHERE name = 'Volkswagen' AND country_code = 'mx')),
     2023, 'mx', 'active', TRUE, NOW() - INTERVAL '2 months', 10000.00)
    ON CONFLICT (vin) DO NOTHING;

-- ==================== FUNCTIONS ====================

-- Function to get fleet statistics
CREATE OR REPLACE FUNCTION get_fleet_stats(country_code VARCHAR(2))
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'country', country_code,
        'total_vehicles', COUNT(v.id),
        'active_vehicles', COUNT(CASE WHEN v.status = 'active' THEN 1 END),
        'instrumented_vehicles', COUNT(CASE WHEN v.is_instrumented = TRUE THEN 1 END),
        'avg_monthly_cost', AVG(v.monthly_cost),
        'total_monthly_cost', SUM(v.monthly_cost)
    ) INTO result
    FROM vehicles v
    WHERE v.country_code = country_code;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to get anomaly statistics
CREATE OR REPLACE FUNCTION get_anomaly_stats(vehicle_id UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'vehicle_id', vehicle_id,
        'total_anomalies', COUNT(a.id),
        'by_severity', json_build_object(
            'low', COUNT(CASE WHEN a.severity = 'low' THEN 1 END),
            'medium', COUNT(CASE WHEN a.severity = 'medium' THEN 1 END),
            'high', COUNT(CASE WHEN a.severity = 'high' THEN 1 END),
            'critical', COUNT(CASE WHEN a.severity = 'critical' THEN 1 END)
        ),
        'by_type', (
            SELECT json_object_agg(anomaly_type, count)
            FROM anomalies
            WHERE vehicle_id = get_anomaly_stats.vehicle_id
            GROUP BY anomaly_type
        ),
        'last_anomaly', MAX(a.timestamp)
    ) INTO result
    FROM anomalies a
    WHERE a.vehicle_id = vehicle_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ==================== FINAL MESSAGE ====================

SELECT 'KCo Database initialized successfully!' AS message;
SELECT 'Old But Gold TR8 IVSTO - Pre-Seed: $30M+ USD' AS tagline;
