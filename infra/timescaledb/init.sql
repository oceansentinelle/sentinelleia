-- Ocean Sentinel V3.0 MAS - TimescaleDB Initialization
-- Date: 26 March 2026
-- Agent: Data Engineer

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create sensor_data table (hypertable for time-series data)
CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    parameter VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION,
    unit VARCHAR(20),
    quality_code INTEGER,
    source VARCHAR(100),
    metadata JSONB
);

-- Convert to hypertable (partitioned by time, 1 day chunks)
SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_sensor_data_station_time ON sensor_data (station_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_parameter_time ON sensor_data (parameter, time DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_time ON sensor_data (time DESC);

-- Enable compression (compress data older than 7 days, 10:1 ratio expected)
ALTER TABLE sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'station_id,parameter',
    timescaledb.compress_orderby = 'time DESC'
);

-- Add compression policy (compress chunks older than 7 days)
SELECT add_compression_policy('sensor_data', INTERVAL '7 days', if_not_exists => TRUE);

-- Create continuous aggregate for hourly statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_data_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    station_id,
    parameter,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*) AS sample_count
FROM sensor_data
GROUP BY bucket, station_id, parameter
WITH NO DATA;

-- Refresh policy for continuous aggregate (refresh every hour)
SELECT add_continuous_aggregate_policy('sensor_data_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Create predictions table (ML model outputs)
CREATE TABLE IF NOT EXISTS predictions (
    time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    predicted_value DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    metadata JSONB
);

-- Convert predictions to hypertable
SELECT create_hypertable('predictions', 'time', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    metadata JSONB
);

-- Index for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts (time DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_station ON alerts (station_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts (resolved, time DESC);

-- Create retention policy (delete raw data older than 1 year)
SELECT add_retention_policy('sensor_data', INTERVAL '1 year', if_not_exists => TRUE);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oceansentinel;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oceansentinel;

-- Insert sample data for testing (Bouée 13 Arcachon)
INSERT INTO sensor_data (time, station_id, parameter, value, unit, quality_code, source, metadata)
VALUES
    (NOW(), 'BARAG', 'temperature', 15.2, '°C', 1, 'Hub''Eau Quadrige', '{"location": "Bassin Arcachon"}'),
    (NOW(), 'BARAG', 'salinity', 35.1, 'PSU', 1, 'Hub''Eau Quadrige', '{"location": "Bassin Arcachon"}'),
    (NOW(), 'BARAG', 'ph', 8.1, 'pH', 1, 'Hub''Eau Quadrige', '{"location": "Bassin Arcachon"}'),
    (NOW(), 'BARAG', 'dissolved_oxygen', 7.8, 'mg/L', 1, 'Hub''Eau Quadrige', '{"location": "Bassin Arcachon"}')
ON CONFLICT DO NOTHING;

-- Vacuum and analyze
VACUUM ANALYZE sensor_data;
VACUUM ANALYZE predictions;
VACUUM ANALYZE alerts;
