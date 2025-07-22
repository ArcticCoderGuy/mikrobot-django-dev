# MikroBot Django API Documentation

## Overview

This API provides endpoints for managing trading signals and trades for the MikroBot PURE Signal Detector system.

**Base URL:** `http://localhost:8000/`

## Authentication

All endpoints require authentication using Django's session authentication or token authentication.

**Login:** `POST /api-auth/login/`

## API Endpoints

### 1. Signals API

#### Get All Signals
```
GET /api/v1/signals/
```

**Query Parameters:**
- `status` - Filter by status (pending, approved, rejected, executed, expired)
- `direction` - Filter by direction (BUY, SELL)
- `symbol` - Filter by symbol (e.g., EURUSD)
- `source_name` - Filter by source name
- `signal_strength` - Filter by strength (weak, medium, strong)
- `search` - Search in symbol and source_name
- `ordering` - Order by field (e.g., `-received_at`)

#### LLM Analysis Endpoints

**Analyze Single Signal:**
```
POST /api/v1/signals/{id}/analyze_with_llm/
```

**Response:**
```json
{
  "signal_id": "uuid-string",
  "is_valid": true,
  "confidence": 0.85,
  "stop_loss": 1.12000,
  "take_profit": 1.13500,
  "risk_score": 25.5,
  "reasoning": "Strong H1 BOS with clean M15 retest. Good market structure.",
  "error_message": null,
  "new_status": "approved"
}
```

**Bulk Analyze Signals:**
```
POST /api/v1/signals/bulk_analyze_llm/
```

**Request Body:**
```json
{
  "signal_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

**LLM Statistics:**
```
GET /api/v1/signals/llm_stats/
```

**Response:**
```json
{
  "total_signals": 100,
  "llm_analyzed": 75,
  "llm_approved": 45,
  "llm_rejected": 30,
  "llm_approval_rate": 60.0,
  "average_confidence": 0.752
}
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/signals/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-string",
      "source_name": "PURE Signal Detector",
      "symbol": "EURUSD",
      "direction": "BUY",
      "entry_price": "1.12345",
      "stop_loss": "1.12000",
      "take_profit": "1.13000",
      "signal_strength": "medium",
      "received_at": "2025-01-17T10:30:00Z",
      "signal_timestamp": "2025-01-17T10:29:45Z",
      "status": "pending",
      "rejection_reason": null,
      "raw_signal_data": {
        "ea_name": "MikroBot_BOS",
        "ea_version": "1.04",
        "trigger_price": 1.12345,
        "h1_bos_level": 1.12000
      },
      "risk_reward_ratio": 1.8,
      "is_valid": true
    }
  ]
}
```

#### Create Signal
```
POST /api/v1/signals/
```

**Request Body:**
```json
{
  "source_name": "PURE Signal Detector",
  "symbol": "EURUSD",
  "direction": "BUY",
  "entry_price": "1.12345",
  "stop_loss": "1.12000",
  "take_profit": "1.13000",
  "signal_strength": "medium",
  "signal_timestamp": "2025-01-17T10:30:00Z",
  "raw_signal_data": {}
}
```

#### Signal Actions

**Approve Signal:**
```
POST /api/v1/signals/{id}/approve/
```

**Reject Signal:**
```
POST /api/v1/signals/{id}/reject/
```
```json
{
  "rejection_reason": "Low confidence signal"
}
```

**Execute Signal:**
```
POST /api/v1/signals/{id}/execute/
```

#### Signal Statistics
```
GET /api/v1/signals/stats/
```

**Response:**
```json
{
  "total_signals": 150,
  "pending": 5,
  "approved": 20,
  "rejected": 15,
  "executed": 100,
  "expired": 10,
  "by_source": {
    "PURE Signal Detector": 150
  },
  "by_symbol": {
    "EURUSD": 75,
    "GBPUSD": 50,
    "USDJPY": 25
  },
  "by_direction": {
    "BUY": 80,
    "SELL": 70
  }
}
```

### 2. Webhook Endpoints

#### PURE Signal Detector Webhook
```
POST /api/v1/pure-signal/                                    # Basic signal storage
POST /api/v1/pure-signal/?auto_llm=true                      # Auto-trigger LLM analysis
POST /api/v1/pure-signal/?auto_llm=true&auto_execute=true    # Full automation
POST /api/v1/pure-signal/?auto_llm=true&auto_execute=true&volume=0.01  # Custom volume
```

**Request Body (from MQL5):**
```json
{
  "ea_name": "MikroBot_BOS",
  "ea_version": "1.04",
  "signal_type": "BOS_RETEST",
  "symbol": "EURUSD",
  "direction": "BUY",
  "trigger_price": 1.12345,
  "h1_bos_level": 1.12000,
  "h1_bos_direction": "BULLISH",
  "m15_break_high": 1.12350,
  "m15_break_low": 1.12100,
  "pip_trigger": 0.6,
  "timestamp": "2025-01-17T10:30:00Z",
  "timeframe": "M15",
  "account": 12345678
}
```

**Response:**
```json
{
  "status": "success",
  "signal_id": "uuid-string",
  "message": "Signal received and stored successfully",
  "next_step": "await_llm_analysis"
}
```

#### Webhook Status Check
```
GET /api/v1/pure-signal/status/
```

#### LLM Approval Webhook
```
POST /api/v1/llm-approval/
```

**Request Body:**
```json
{
  "signal_id": "uuid-string",
  "approval_decision": "approved",
  "llm_reasoning": "Strong BOS pattern with good R:R ratio"
}
```

### 3. Trading API

#### Get All Trades
```
GET /api/v1/trades/
```

#### MT5 Integration Endpoints

**Execute Approved Signal:**
```
POST /api/v1/trades/execute_signal/
```

**Request Body:**
```json
{
  "signal_id": "uuid-string",
  "volume": 0.01
}
```

**Response:**
```json
{
  "message": "Trade executed successfully. Ticket: 123456789",
  "trade_id": "trade-uuid",
  "mt5_ticket": 123456789,
  "signal_id": "signal-uuid"
}
```

**Close MT5 Trade:**
```
POST /api/v1/trades/{id}/close_mt5_trade/
```

**Sync Trade with MT5:**
```
POST /api/v1/trades/{id}/sync_with_mt5/
```

**Get MT5 Account Info:**
```
GET /api/v1/trades/mt5_account_info/
```

**Response:**
```json
{
  "login": 12345678,
  "server": "MetaQuotes-Demo",
  "currency": "USD",
  "company": "MetaQuotes Software Corp.",
  "balance": 10000.00,
  "equity": 10000.00,
  "margin": 0.00,
  "free_margin": 10000.00,
  "margin_level": 0.00,
  "profit": 0.00
}
```

**Bulk Sync All Trades:**
```
POST /api/v1/trades/bulk_sync_mt5/
```

**Query Parameters:**
- `status` - Filter by status (pending, opened, closed_profit, closed_loss, etc.)
- `direction` - Filter by direction (BUY, SELL)
- `symbol` - Filter by symbol
- `exit_reason` - Filter by exit reason
- `search` - Search in symbol, mt5_ticket, notes
- `ordering` - Order by field (e.g., `-execution_time`)

#### Create Trade
```
POST /api/v1/trades/
```

**Request Body:**
```json
{
  "mql5_signal": "signal-uuid",
  "mt5_ticket": 123456789,
  "mt5_order_type": "ORDER_TYPE_BUY",
  "symbol": "EURUSD",
  "direction": "BUY",
  "entry_price": "1.12345",
  "stop_loss": "1.12000",
  "take_profit": "1.13000",
  "volume": "0.10",
  "signal_time": "2025-01-17T10:30:00Z",
  "execution_time": "2025-01-17T10:30:15Z",
  "notes": "Trade executed from approved signal"
}
```

#### Create Trade from Signal
```
POST /api/v1/trades/create_from_signal/
```

**Request Body:**
```json
{
  "signal_id": "uuid-string",
  "mt5_ticket": 123456789,
  "mt5_order_type": "ORDER_TYPE_BUY",
  "volume": "0.10",
  "execution_time": "2025-01-17T10:30:15Z",
  "actual_entry_price": "1.12350",
  "actual_stop_loss": "1.12000",
  "actual_take_profit": "1.13000",
  "notes": "Trade executed with slippage"
}
```

#### Close Trade
```
POST /api/v1/trades/{id}/close_trade/
```

**Request Body:**
```json
{
  "exit_price": "1.12800",
  "exit_reason": "take_profit",
  "gross_profit_loss": "45.50",
  "commission": "2.50",
  "swap": "0.00",
  "max_drawdown": "15.00",
  "max_profit": "50.00"
}
```

#### Trading Statistics
```
GET /api/v1/trades/statistics/
```

**Response:**
```json
{
  "total_trades": 100,
  "active_trades": 5,
  "closed_trades": 95,
  "total_pnl": 1250.50,
  "win_rate": 65.26,
  "profitable_trades": 62,
  "losing_trades": 33,
  "average_profit": 45.20,
  "average_loss": -25.80,
  "symbol_breakdown": [
    {
      "symbol": "EURUSD",
      "count": 50,
      "pnl": 750.25
    }
  ],
  "direction_breakdown": [
    {
      "direction": "BUY",
      "count": 55,
      "pnl": 680.30
    }
  ]
}
```

#### Get Active Trades
```
GET /api/v1/trades/active_trades/
```

#### Get Recent Trades
```
GET /api/v1/trades/recent_trades/
```

#### Get Profitable Trades
```
GET /api/v1/trades/profitable_trades/
```

#### Get Losing Trades
```
GET /api/v1/trades/losing_trades/
```

### 4. Trading Sessions API

#### Get All Sessions
```
GET /api/v1/sessions/
```

#### Create Session
```
POST /api/v1/sessions/
```

**Request Body:**
```json
{
  "session_name": "London Session",
  "start_time": "2025-01-17T08:00:00Z",
  "end_time": "2025-01-17T17:00:00Z"
}
```

#### Add Trades to Session
```
POST /api/v1/sessions/{id}/add_trades/
```

**Request Body:**
```json
{
  "trade_ids": ["trade-uuid-1", "trade-uuid-2"]
}
```

#### Get Active Session
```
GET /api/v1/sessions/active_session/
```

## Signal → Trade Workflow

1. **Signal Detection**: MQL5 EA detects signal and sends to webhook
2. **Signal Storage**: Django receives and stores signal with `pending` status
3. **LLM Analysis**: External LLM analyzes signal and sends approval/rejection
4. **Signal Approval**: Signal status updated to `approved` or `rejected`
5. **Trade Creation**: Approved signal converted to trade via `/create_from_signal/`
6. **Trade Execution**: Trade executed in MT5, status updated to `opened`
7. **Trade Monitoring**: Real-time monitoring of trade performance
8. **Trade Closure**: Trade closed either by TP/SL or manual intervention

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "status": "error",
  "message": "Error description",
  "errors": {
    "field_name": ["Field-specific error messages"]
  }
}
```

## Rate Limiting

No rate limiting is currently implemented, but it's recommended for production use.

## WebSocket Support

Not currently implemented but planned for real-time updates.

## Testing

Use the Django admin interface at `/admin/` to view and manage signals and trades.

For API testing, use tools like:
- Postman
- curl
- Django REST Framework's browsable API at `/api/v1/`

## PURE Signal Detector Integration

The PURE Signal Detector EA should be configured with:
- **Django URL**: `http://localhost:8000/api/v1/pure-signal/`
- **Timeout**: 5000ms
- **Content-Type**: `application/json`

The webhook endpoint accepts signals with the exact JSON format provided by the MQL5 EA.