-- ============================================
-- PERSONAL TRADING INTELLIGENCE SYSTEM
-- Database Initialization Script
-- ============================================
-- This runs automatically on first PostgreSQL startup
-- via docker-entrypoint-initdb.d

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUMS
-- ============================================

CREATE TYPE asset_type AS ENUM ('crypto', 'stock', 'commodity', 'index', 'macro');
CREATE TYPE news_category AS ENUM ('crypto', 'macro', 'stock', 'general', 'commodity');
CREATE TYPE sentiment_type AS ENUM ('positive', 'negative', 'neutral', 'unknown');
CREATE TYPE market_impact AS ENUM ('high', 'medium', 'low', 'unknown');
CREATE TYPE timeframe_type AS ENUM ('1m', '5m', '15m', '1h', '4h', '1d', '1w');
CREATE TYPE macro_event_type AS ENUM ('fomc', 'cpi', 'pce', 'nfp', 'gdp', 'unemployment', 'rate_decision', 'treasury_auction', 'other');
CREATE TYPE analysis_type AS ENUM ('market_report', 'news_analysis', 'macro_analysis', 'sentiment_analysis');
CREATE TYPE bias_type AS ENUM ('bullish', 'bearish', 'neutral');
CREATE TYPE signal_type AS ENUM ('technical', 'news', 'macro', 'sentiment', 'composite');
CREATE TYPE direction_type AS ENUM ('bullish', 'bearish', 'neutral');
CREATE TYPE alert_type AS ENUM ('high_impact_news', 'macro_event', 'price_move', 'technical_signal', 'system');
CREATE TYPE importance_type AS ENUM ('critical', 'high', 'medium', 'low');
CREATE TYPE trade_direction AS ENUM ('long', 'short');
CREATE TYPE trade_status AS ENUM ('open', 'closed', 'cancelled');
CREATE TYPE prediction_horizon AS ENUM ('1h', '4h', '24h', '7d');
CREATE TYPE ai_provider_type AS ENUM ('local', 'openai', 'gemini', 'grok', 'claude');
CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'critical');
CREATE TYPE freshness_status AS ENUM ('live', 'recent', 'stale', 'expired');

-- ============================================
-- TABLES
-- ============================================

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    asset_type asset_type NOT NULL,
    exchange VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Watchlists
CREATE TABLE IF NOT EXISTS watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS watchlist_items (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(watchlist_id, asset_id)
);

-- News Sources
CREATE TABLE IF NOT EXISTS news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    source_type VARCHAR(20) NOT NULL DEFAULT 'rss',
    category news_category NOT NULL DEFAULT 'general',
    is_active BOOLEAN DEFAULT true,
    rate_limit_per_min INTEGER DEFAULT 60,
    last_fetched_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- News
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source_id INTEGER REFERENCES news_sources(id) ON DELETE SET NULL,
    source_name VARCHAR(100),
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    summary TEXT,
    asset_id INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    category news_category DEFAULT 'general',
    sentiment sentiment_type DEFAULT 'unknown',
    sentiment_score FLOAT,
    importance_score FLOAT DEFAULT 0 CHECK (importance_score >= 0 AND importance_score <= 10),
    market_impact market_impact DEFAULT 'unknown',
    related_assets TEXT[],
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    embedding vector(768),
    dedup_hash VARCHAR(64) UNIQUE,
    freshness_status freshness_status DEFAULT 'recent',
    is_processed BOOLEAN DEFAULT false,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- News Clusters
CREATE TABLE IF NOT EXISTS news_clusters (
    id SERIAL PRIMARY KEY,
    cluster_hash VARCHAR(64) UNIQUE NOT NULL,
    primary_news_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    member_count INTEGER DEFAULT 1,
    cluster_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news_cluster_members (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER NOT NULL REFERENCES news_clusters(id) ON DELETE CASCADE,
    news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(cluster_id, news_id)
);

-- Market Prices
CREATE TABLE IF NOT EXISTS market_prices (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC,
    timeframe timeframe_type NOT NULL,
    source VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(asset_id, timestamp, timeframe)
);

-- Market Indicators
CREATE TABLE IF NOT EXISTS market_indicators (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    timeframe timeframe_type NOT NULL,
    rsi_14 FLOAT,
    macd FLOAT,
    macd_signal FLOAT,
    macd_hist FLOAT,
    ema_20 FLOAT,
    ema_50 FLOAT,
    ema_200 FLOAT,
    atr_14 FLOAT,
    bollinger_upper FLOAT,
    bollinger_middle FLOAT,
    bollinger_lower FLOAT,
    vwap FLOAT,
    volume NUMERIC,
    volatility FLOAT,
    support FLOAT,
    resistance FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(asset_id, timestamp, timeframe)
);

-- Macro Events
CREATE TABLE IF NOT EXISTS macro_events (
    id SERIAL PRIMARY KEY,
    event_type macro_event_type NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    previous_value FLOAT,
    forecast_value FLOAT,
    actual_value FLOAT,
    surprise FLOAT,
    unit VARCHAR(20),
    source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Macro Data
CREATE TABLE IF NOT EXISTS macro_data (
    id SERIAL PRIMARY KEY,
    series_id VARCHAR(100) NOT NULL,
    series_name VARCHAR(200),
    value FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50) NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(series_id, timestamp)
);

-- AI Analysis
CREATE TABLE IF NOT EXISTS ai_analysis (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_type analysis_type NOT NULL,
    bias bias_type,
    confidence FLOAT,
    reference_price FLOAT,
    bull_case TEXT,
    bear_case TEXT,
    base_case TEXT,
    key_levels JSONB,
    invalidation FLOAT,
    catalysts TEXT[],
    conflicting_evidence TEXT[],
    model_used VARCHAR(100),
    provider ai_provider_type,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    estimated_cost FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Signals
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    signal_type signal_type NOT NULL,
    direction direction_type NOT NULL,
    strength FLOAT DEFAULT 0 CHECK (strength >= 0 AND strength <= 1),
    description TEXT,
    source_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type alert_type NOT NULL,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    title VARCHAR(500),
    message TEXT,
    importance importance_type DEFAULT 'medium',
    affected_assets TEXT[],
    expected_impact TEXT,
    confidence FLOAT,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    bias bias_type NOT NULL,
    confidence FLOAT,
    reference_price FLOAT,
    target_price FLOAT,
    invalidation_price FLOAT,
    horizon prediction_horizon NOT NULL,
    analysis_id INTEGER REFERENCES ai_analysis(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prediction Results
CREATE TABLE IF NOT EXISTS prediction_results (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actual_price FLOAT,
    direction_correct BOOLEAN,
    return_pct FLOAT,
    mae FLOAT,
    mfe FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trades
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    direction trade_direction NOT NULL,
    entry_price FLOAT NOT NULL,
    exit_price FLOAT,
    stop_loss FLOAT,
    take_profit FLOAT,
    position_size FLOAT,
    exit_time TIMESTAMP WITH TIME ZONE,
    pnl FLOAT,
    pnl_pct FLOAT,
    mfe FLOAT,
    mae FLOAT,
    holding_time_hours FLOAT,
    status trade_status DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trade Features
CREATE TABLE IF NOT EXISTS trade_features (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER NOT NULL REFERENCES trades(id) ON DELETE CASCADE,
    market_regime VARCHAR(50),
    rsi_at_entry FLOAT,
    ema_20_at_entry FLOAT,
    ema_50_at_entry FLOAT,
    ema_200_at_entry FLOAT,
    volume_at_entry FLOAT,
    volatility_at_entry FLOAT,
    news_context TEXT,
    macro_context TEXT,
    sentiment_at_entry FLOAT,
    setup_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trade Notes
CREATE TABLE IF NOT EXISTS trade_notes (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER NOT NULL REFERENCES trades(id) ON DELETE CASCADE,
    my_reasoning TEXT,
    my_decision TEXT,
    lessons TEXT,
    mistakes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Logs
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level log_level NOT NULL DEFAULT 'info',
    service VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Usage
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost FLOAT DEFAULT 0,
    reason VARCHAR(200),
    asset VARCHAR(20),
    task VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model Evaluations
CREATE TABLE IF NOT EXISTS model_evaluations (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    eval_type VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    details JSONB,
    benchmark_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_news_timestamp ON news (timestamp DESC);
CREATE INDEX idx_news_asset ON news (asset_id, timestamp DESC);
CREATE INDEX idx_news_category ON news (category, importance_score DESC);
CREATE INDEX idx_news_dedup ON news (dedup_hash);
CREATE INDEX idx_news_freshness ON news (freshness_status, timestamp DESC);
CREATE INDEX idx_news_embedding ON news USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_market_prices_lookup ON market_prices (asset_id, timeframe, timestamp DESC);
CREATE INDEX idx_market_indicators_lookup ON market_indicators (asset_id, timeframe, timestamp DESC);

CREATE INDEX idx_macro_events_time ON macro_events (scheduled_time);
CREATE INDEX idx_macro_data_series ON macro_data (series_id, timestamp DESC);

CREATE INDEX idx_ai_analysis_asset ON ai_analysis (asset_id, timestamp DESC);
CREATE INDEX idx_trades_user ON trades (user_id, timestamp DESC);
CREATE INDEX idx_api_usage_date ON api_usage (timestamp DESC);
CREATE INDEX idx_system_logs_timestamp ON system_logs (timestamp DESC);
CREATE INDEX idx_signals_asset ON signals (asset_id, timestamp DESC);
CREATE INDEX idx_alerts_sent ON alerts (is_sent, timestamp DESC);

-- ============================================
-- TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_news_updated
    BEFORE UPDATE ON news
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================
-- SEED DATA — Initial Assets
-- ============================================

INSERT INTO assets (symbol, name, asset_type, exchange, is_active) VALUES
    ('BTC', 'Bitcoin', 'crypto', 'Binance', true),
    ('ETH', 'Ethereum', 'crypto', 'Binance', true),
    ('SOL', 'Solana', 'crypto', 'Binance', true),
    ('XRP', 'Ripple', 'crypto', 'Binance', true),
    ('GOLD', 'Gold Futures', 'commodity', 'COMEX', true),
    ('SILVER', 'Silver Futures', 'commodity', 'COMEX', true),
    ('OIL', 'Crude Oil Futures', 'commodity', 'NYMEX', true),
    ('NVDA', 'NVIDIA Corporation', 'stock', 'NASDAQ', true),
    ('TSLA', 'Tesla Inc', 'stock', 'NASDAQ', true),
    ('AAPL', 'Apple Inc', 'stock', 'NASDAQ', true),
    ('MSFT', 'Microsoft Corporation', 'stock', 'NASDAQ', true),
    ('COIN', 'Coinbase Global', 'stock', 'NASDAQ', true),
    ('MSTR', 'MicroStrategy', 'stock', 'NASDAQ', true)
ON CONFLICT (symbol) DO NOTHING;

-- ============================================
-- SEED DATA — News Sources (candidates, verify in Phase 2)
-- ============================================

INSERT INTO news_sources (name, url, source_type, category, is_active, rate_limit_per_min) VALUES
    ('CoinDesk', 'https://www.coindesk.com/arc/outboundfeeds/rss/', 'rss', 'crypto', true, 30),
    ('CoinTelegraph', 'https://cointelegraph.com/rss', 'rss', 'crypto', true, 30),
    ('Fed Press Releases', 'https://www.federalreserve.gov/feeds/press_all.xml', 'rss', 'macro', true, 30),
    ('NVDA IR', 'https://investor.nvidia.com/rss/news-releases.xml', 'rss', 'stock', true, 30),
    ('TSLA IR', 'https://ir.tesla.com/rss/news-releases.xml', 'rss', 'stock', true, 30),
    ('AAPL IR', 'https://investor.apple.com/rss/news.rss', 'rss', 'stock', true, 30),
    ('MSFT IR', 'https://www.microsoft.com/en-us/investor/rss-feed', 'rss', 'stock', true, 30)
ON CONFLICT DO NOTHING;
