-- MikroBot Production Database Initialization
-- Creates optimized tables for high-frequency trading signals

-- Create extensions for UUID and timing
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create optimized indexes for time-series data
-- Will be used by Django migrations but optimized for trading workload

-- Create dedicated tablespace for MCP data (optional, for performance)
-- CREATE TABLESPACE mcp_data LOCATION '/var/lib/postgresql/mcp_data';

-- MCP Agent status tracking
CREATE TABLE IF NOT EXISTS mcp_agent_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'starting',
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    process_id INTEGER,
    version VARCHAR(20),
    config_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fast agent lookups
CREATE INDEX IF NOT EXISTS idx_mcp_agent_status_name ON mcp_agent_status(agent_name);
CREATE INDEX IF NOT EXISTS idx_mcp_agent_status_heartbeat ON mcp_agent_status(last_heartbeat);

-- Kafka topic management
CREATE TABLE IF NOT EXISTS kafka_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_name VARCHAR(100) NOT NULL UNIQUE,
    partition_count INTEGER NOT NULL DEFAULT 3,
    replication_factor INTEGER NOT NULL DEFAULT 1,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default topics for MikroBot MCP
INSERT INTO kafka_topics (topic_name, partition_count, config) VALUES 
('pure-signals', 3, '{"retention.ms": 604800000, "cleanup.policy": "delete"}'),
('processed-signals', 3, '{"retention.ms": 2592000000, "cleanup.policy": "delete"}'),
('trade-executions', 1, '{"retention.ms": 7776000000, "cleanup.policy": "delete"}'),
('system-events', 1, '{"retention.ms": 2592000000, "cleanup.policy": "delete"}')
ON CONFLICT (topic_name) DO NOTHING;

-- Performance monitoring tables
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metric_type VARCHAR(20) NOT NULL, -- counter, gauge, histogram
    labels JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create hypertable for time-series performance metrics (if TimescaleDB available)
-- SELECT create_hypertable('performance_metrics', 'timestamp', if_not_exists => TRUE);

-- Indexes for fast metric queries
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_time ON performance_metrics(metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);

-- Signal processing audit trail
CREATE TABLE IF NOT EXISTS signal_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id UUID NOT NULL,
    stage VARCHAR(50) NOT NULL, -- received, analyzed, approved, executed, failed
    processor VARCHAR(50) NOT NULL,
    processing_time_ms INTEGER,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for audit trail
CREATE INDEX IF NOT EXISTS idx_signal_audit_signal_id ON signal_audit_trail(signal_id);
CREATE INDEX IF NOT EXISTS idx_signal_audit_stage_time ON signal_audit_trail(stage, created_at DESC);

-- MCP configuration management
CREATE TABLE IF NOT EXISTS mcp_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    config_type VARCHAR(20) NOT NULL DEFAULT 'runtime',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default MCP configurations
INSERT INTO mcp_configuration (config_key, config_value, config_type, description) VALUES 
('mcp.processing.threads', '4', 'runtime', 'Number of signal processing threads'),
('mcp.heartbeat.interval_seconds', '10', 'runtime', 'Heartbeat interval in seconds'),
('mcp.risk.max_signals_per_minute', '100', 'safety', 'Maximum signals to process per minute'),
('mcp.kafka.consumer_group', '"mikrobot-mcp-group"', 'kafka', 'Kafka consumer group ID'),
('mcp.logging.level', '"INFO"', 'logging', 'Default logging level')
ON CONFLICT (config_key) DO NOTHING;

-- Grant permissions to mikrobot_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mikrobot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mikrobot_user;

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply automatic timestamp updates
CREATE TRIGGER update_mcp_agent_status_updated_at BEFORE UPDATE ON mcp_agent_status 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcp_configuration_updated_at BEFORE UPDATE ON mcp_configuration 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for Django models (will be created by migrations, but optimized here)
-- These will improve Django ORM performance significantly

COMMENT ON DATABASE mikrobot_production IS 'MikroBot MCP Production Database - High-frequency trading signal processing';