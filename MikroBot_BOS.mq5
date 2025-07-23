//+------------------------------------------------------------------+
//| MikroBot_BOS.mq5                                                 |
//| PURE Signal Detector: H1 BOS → M15 Break-and-Retest → Django     |
//| Copyright 2025, NorthFox1975 - FoxInTheCode.fi                   |
//+------------------------------------------------------------------+
#property copyright "NorthFox1975 - FoxInTheCode.fi"
#property version   "1.04"
#property description "PURE SIGNAL DETECTOR - Only sends JSON to Django MCP"

#include <Trade\Trade.mqh>

//--- Input parameters
input group "=== SIGNAL DETECTION ==="
input double   InpPipTrigger = 0.6;           // Pip trigger for 3rd candle
input int      InpLookbackBars = 20;          // H1 bars to look back for structure

input group "=== DJANGO MCP ==="
input string   InpDjangoURL = "http://127.0.0.1:8000/api/v1/pure-signal/";
input string   InpTimeframeURL = "http://127.0.0.1:8000/api/v1/pure-signal/timeframes/";
input int      InpTimeoutMS = 5000;           // HTTP timeout milliseconds
input bool     InpSendToDjango = true;        // Send signals to Django MCP
input bool     InpAutoTimeframes = true;     // Auto-fetch timeframes from Django

//--- Global variables
struct BOSData {
    datetime    time;
    double      price;
    bool        is_bullish;
    bool        is_valid;
    double      structure_level;
};

struct RetestData {
    bool        waiting_for_retest;
    double      bos_level;
    bool        is_bullish_setup;
    int         candle_count;
    double      first_break_high;
    double      first_break_low;
    bool        break_confirmed;
    int         timeout_counter;
};

struct TimeframeConfig {
    string      higher_timeframe;
    string      lower_timeframe;
    string      combination;
    datetime    last_update;
    bool        is_valid;
};

BOSData        g_h1_bos;
RetestData     g_m15_retest;
TimeframeConfig g_timeframes;
datetime       g_last_h1_time = 0;
datetime       g_last_m15_time = 0;
datetime       g_last_timeframe_check = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    // Validate inputs
    if (InpPipTrigger <= 0) {
        Print("❌ Error: Pip trigger must be positive");
        return INIT_PARAMETERS_INCORRECT;
    }
    
    if (InpLookbackBars < 5 || InpLookbackBars > 100) {
        Print("❌ Error: Lookback bars must be between 5-100");
        return INIT_PARAMETERS_INCORRECT;
    }
    
    if (StringLen(InpDjangoURL) < 10) {
        Print("❌ Error: Invalid Django URL");
        return INIT_PARAMETERS_INCORRECT;
    }
    
    // Initialize structures
    InitializeBOSData();
    InitializeRetestData();
    InitializeTimeframeConfig();
    
    // Fetch initial timeframe settings from Django
    if (InpAutoTimeframes) {
        FetchTimeframeSettings();
    }
    
    // Check history availability
    int h1_bars = Bars(_Symbol, PERIOD_H1);
    int m15_bars = Bars(_Symbol, PERIOD_M15);
    
    if (h1_bars < InpLookbackBars + 10) {
        Print("⚠️ Warning: Limited H1 history. Available: ", h1_bars);
    }
    
    if (m15_bars < 100) {
        Print("⚠️ Warning: Limited M15 history. Available: ", m15_bars);
    }
    
    // Startup message
    Print("🦊 MikroBot PURE Signal Detector v1.04 Started!");
    Print("📊 Configuration: ", g_timeframes.combination, " BOS (", InpLookbackBars, " bars) → Break-and-Retest → ", InpPipTrigger, " pip trigger");
    Print("🎯 Mode: PURE DETECTOR - No trading calculations, only signals to Django MCP");
    Print("🌐 Django endpoint: ", InpDjangoURL);
    Print("⏰ Timeframe endpoint: ", InpTimeframeURL);
    Print("🔄 Auto-timeframes: ", (InpAutoTimeframes ? "ENABLED" : "DISABLED"));
    Print("✅ Initialization complete - Ready for signal detection");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    // Determine shutdown reason
    string reason_text = "";
    switch(reason) {
        case REASON_PROGRAM:    reason_text = "EA stopped manually"; break;
        case REASON_REMOVE:     reason_text = "EA removed from chart"; break;
        case REASON_RECOMPILE:  reason_text = "EA recompiled"; break;
        case REASON_CHARTCHANGE: reason_text = "Chart symbol/period changed"; break;
        case REASON_CHARTCLOSE: reason_text = "Chart closed"; break;
        case REASON_PARAMETERS: reason_text = "Input parameters changed"; break;
        case REASON_ACCOUNT:    reason_text = "Account changed"; break;
        case REASON_TEMPLATE:   reason_text = "Template applied"; break;
        case REASON_INITFAILED: reason_text = "Initialization failed"; break;
        case REASON_CLOSE:      reason_text = "Terminal closing"; break;
        default:                reason_text = "Unknown reason: " + IntegerToString(reason); break;
    }
    
    Print("🛑 MikroBot Signal Detector Shutdown");
    Print("📄 Reason: ", reason_text);
    
    // Log final state if monitoring was active
    if (g_m15_retest.waiting_for_retest) {
        Print("📊 Active monitoring terminated:");
        Print("   - Setup: ", (g_m15_retest.is_bullish_setup ? "BULLISH" : "BEARISH"));
        Print("   - BOS Level: ", DoubleToString(g_m15_retest.bos_level, _Digits));
        Print("   - Candle Count: ", g_m15_retest.candle_count);
        Print("   - Break Confirmed: ", (g_m15_retest.break_confirmed ? "YES" : "NO"));
    }
    
    // Clean up global variables
    InitializeBOSData();
    InitializeRetestData();
    InitializeTimeframeConfig();
    
    // Reset time trackers
    g_last_h1_time = 0;
    g_last_m15_time = 0;
    g_last_timeframe_check = 0;
    
    Print("🧹 Cleanup completed");
    Print("👋 MikroBot Signal Detector shutdown complete");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Check for timeframe updates every 5 minutes
    if (InpAutoTimeframes && (TimeCurrent() - g_last_timeframe_check) >= 300) {
        CheckTimeframeUpdates();
        g_last_timeframe_check = TimeCurrent();
    }
    
    // Check for new H1 candle
    if (IsNewCandle(PERIOD_H1, g_last_h1_time)) {
        CheckH1_BOS();
    }
    
    // Check for new M15 candle (only if waiting for retest)
    if (g_m15_retest.waiting_for_retest && IsNewCandle(PERIOD_M15, g_last_m15_time)) {
        CheckM15_BreakAndRetest();
    }
}

//+------------------------------------------------------------------+
//| Chart event function                                             |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam) {
    // Handle chart events for debugging/monitoring if needed
    switch(id) {
        case CHARTEVENT_KEYDOWN:
            if (lparam == 'R' || lparam == 'r') {
                // Reset monitoring on 'R' key press
                Print("🔄 Manual reset triggered");
                InitializeBOSData();
                InitializeRetestData();
                
            } else if (lparam == 'T' || lparam == 't') {
                // Manual timeframe update on 'T' key press
                Print("🔄 Manual timeframe update triggered");
                if (InpAutoTimeframes) {
                    FetchTimeframeSettings();
                } else {
                    Print("⚠️ Auto-timeframes disabled");
                }
            }
            break;
            
        case CHARTEVENT_OBJECT_CLICK:
            // Could add manual signal testing here if needed
            break;
    }
}

//+------------------------------------------------------------------+
//| Check for new candle                                             |
//+------------------------------------------------------------------+
bool IsNewCandle(ENUM_TIMEFRAMES timeframe, datetime &last_time) {
    datetime current_time = iTime(_Symbol, timeframe, 0);
    if (current_time != last_time && current_time > 0) {
        last_time = current_time;
        return true;
    }
    return false;
}

//+------------------------------------------------------------------+
//| Initialize BOS data structure                                    |
//+------------------------------------------------------------------+
void InitializeBOSData() {
    g_h1_bos.time = 0;
    g_h1_bos.price = 0;
    g_h1_bos.is_bullish = false;
    g_h1_bos.is_valid = false;
    g_h1_bos.structure_level = 0;
}

//+------------------------------------------------------------------+
//| Initialize Retest data structure                                 |
//+------------------------------------------------------------------+
void InitializeRetestData() {
    g_m15_retest.waiting_for_retest = false;
    g_m15_retest.bos_level = 0;
    g_m15_retest.is_bullish_setup = false;
    g_m15_retest.candle_count = 0;
    g_m15_retest.first_break_high = 0;
    g_m15_retest.first_break_low = 0;
    g_m15_retest.break_confirmed = false;
    g_m15_retest.timeout_counter = 0;
}

//+------------------------------------------------------------------+
//| Initialize Timeframe Configuration                               |
//+------------------------------------------------------------------+
void InitializeTimeframeConfig() {
    g_timeframes.higher_timeframe = "H1";
    g_timeframes.lower_timeframe = "M15";
    g_timeframes.combination = "H1/M15";
    g_timeframes.last_update = 0;
    g_timeframes.is_valid = true;
}

//+------------------------------------------------------------------+
//| Check for H1 Break of Structure                                  |
//+------------------------------------------------------------------+
void CheckH1_BOS() {
    // Validate sufficient history
    int available_bars = Bars(_Symbol, PERIOD_H1);
    if (available_bars < InpLookbackBars + 5) {
        Print("⚠️ Insufficient H1 history for BOS analysis: ", available_bars, " bars");
        return;
    }
    
    // Get current closed candle data (index 1 = previous completed candle)
    double current_high = iHigh(_Symbol, PERIOD_H1, 1);
    double current_low = iLow(_Symbol, PERIOD_H1, 1);
    double current_close = iClose(_Symbol, PERIOD_H1, 1);
    
    // Validate price data
    if (current_high <= 0 || current_low <= 0 || current_close <= 0) {
        Print("❌ Invalid H1 price data");
        return;
    }
    
    // Determine structure levels from lookback period
    double structure_high = 0;
    double structure_low = DBL_MAX;
    int valid_bars = 0;
    
    for (int i = 2; i <= InpLookbackBars + 1; i++) {
        double high = iHigh(_Symbol, PERIOD_H1, i);
        double low = iLow(_Symbol, PERIOD_H1, i);
        
        // Skip invalid bars
        if (high <= 0 || low <= 0) {
            continue;
        }
        
        valid_bars++;
        if (high > structure_high) structure_high = high;
        if (low < structure_low) structure_low = low;
    }
    
    // Ensure we have enough valid data
    if (valid_bars < (InpLookbackBars / 2)) {
        Print("⚠️ Insufficient valid H1 data for structure analysis");
        return;
    }
    
    if (structure_high <= 0 || structure_low >= DBL_MAX) {
        Print("❌ Could not determine valid structure levels");
        return;
    }
    
    // Analyze for BULLISH Break of Structure
    if (current_close > structure_high && current_high > structure_high) {
        double pip_value = GetPipValue();
        double breakout_pips = (current_close - structure_high) / pip_value;
        
        // Require minimum 2 pip breakout to avoid false signals
        if (breakout_pips >= 2.0) {
            Print("🔥 BULLISH H1 BOS DETECTED!");
            Print("   Close: ", DoubleToString(current_close, _Digits));
            Print("   Structure High: ", DoubleToString(structure_high, _Digits));
            Print("   Breakout: ", DoubleToString(breakout_pips, 1), " pips");
            
            // Store BOS data
            g_h1_bos.time = iTime(_Symbol, PERIOD_H1, 1);
            g_h1_bos.price = current_close;
            g_h1_bos.is_bullish = true;
            g_h1_bos.is_valid = true;
            g_h1_bos.structure_level = structure_high;
            
            // Start M15 retest monitoring
            StartM15Retest(true, structure_high);
        }
    }
    // Analyze for BEARISH Break of Structure
    else if (current_close < structure_low && current_low < structure_low) {
        double pip_value = GetPipValue();
        double breakout_pips = (structure_low - current_close) / pip_value;
        
        // Require minimum 2 pip breakout to avoid false signals
        if (breakout_pips >= 2.0) {
            Print("🔥 BEARISH H1 BOS DETECTED!");
            Print("   Close: ", DoubleToString(current_close, _Digits));
            Print("   Structure Low: ", DoubleToString(structure_low, _Digits));
            Print("   Breakout: ", DoubleToString(breakout_pips, 1), " pips");
            
            // Store BOS data
            g_h1_bos.time = iTime(_Symbol, PERIOD_H1, 1);
            g_h1_bos.price = current_close;
            g_h1_bos.is_bullish = false;
            g_h1_bos.is_valid = true;
            g_h1_bos.structure_level = structure_low;
            
            // Start M15 retest monitoring
            StartM15Retest(false, structure_low);
        }
    }
}

//+------------------------------------------------------------------+
//| Start M15 Break-and-Retest monitoring                            |
//+------------------------------------------------------------------+
void StartM15Retest(bool is_bullish, double bos_level) {
    // Clean slate for new monitoring
    InitializeRetestData();
    
    // Configure retest monitoring
    g_m15_retest.waiting_for_retest = true;
    g_m15_retest.bos_level = bos_level;
    g_m15_retest.is_bullish_setup = is_bullish;
    
    Print("📊 M15 RETEST MONITORING STARTED");
    Print("   Direction: ", (is_bullish ? "BULLISH" : "BEARISH"));
    Print("   BOS Level: ", DoubleToString(bos_level, _Digits));
    Print("   Waiting for initial break and 3-candle retest pattern...");
}

//+------------------------------------------------------------------+
//| Check M15 Break-and-Retest pattern                               |
//+------------------------------------------------------------------+
void CheckM15_BreakAndRetest() {
    if (!g_m15_retest.waiting_for_retest) return;
    
    // Increment counters
    g_m15_retest.candle_count++;
    g_m15_retest.timeout_counter++;
    
    // Timeout protection (24 hours = 96 M15 candles)
    if (g_m15_retest.timeout_counter > 96) {
        Print("⏰ M15 Retest monitoring timeout (24 hours) - Resetting");
        InitializeRetestData();
        return;
    }
    
    // Get current M15 candle data (previous closed candle)
    double m15_high = iHigh(_Symbol, PERIOD_M15, 1);
    double m15_low = iLow(_Symbol, PERIOD_M15, 1);
    double m15_close = iClose(_Symbol, PERIOD_M15, 1);
    
    // Validate M15 price data
    if (m15_high <= 0 || m15_low <= 0 || m15_close <= 0) {
        Print("❌ Invalid M15 price data - skipping candle");
        return;
    }
    
    // PHASE 1: Detect initial break of BOS level
    if (!g_m15_retest.break_confirmed) {
        bool break_detected = false;
        
        if (g_m15_retest.is_bullish_setup) {
            // Bullish setup: look for break above BOS level
            if (m15_close > g_m15_retest.bos_level && m15_high > g_m15_retest.bos_level) {
                break_detected = true;
            }
        } else {
            // Bearish setup: look for break below BOS level
            if (m15_close < g_m15_retest.bos_level && m15_low < g_m15_retest.bos_level) {
                break_detected = true;
            }
        }
        
        if (break_detected) {
            g_m15_retest.break_confirmed = true;
            g_m15_retest.first_break_high = m15_high;
            g_m15_retest.first_break_low = m15_low;
            g_m15_retest.candle_count = 1; // Reset counter for retest phase
            
            Print("✅ M15 INITIAL BREAK CONFIRMED!");
            Print("   Break Candle: H=", DoubleToString(m15_high, _Digits), 
                  " L=", DoubleToString(m15_low, _Digits), 
                  " C=", DoubleToString(m15_close, _Digits));
            Print("   Now waiting for 3rd candle trigger...");
        }
        return;
    }
    
    // PHASE 2: Monitor for 3rd candle trigger
    if (g_m15_retest.candle_count == 3) {
        double pip_value = GetPipValue();
        double trigger_distance = InpPipTrigger * pip_value;
        
        bool signal_triggered = false;
        string signal_direction = "";
        double trigger_price = 0;
        
        if (g_m15_retest.is_bullish_setup) {
            // Bullish: 3rd candle high must exceed first break candle high + 0.6 pips
            double trigger_level = g_m15_retest.first_break_high + trigger_distance;
            
            if (m15_high >= trigger_level) {
                signal_triggered = true;
                signal_direction = "BUY";
                trigger_price = trigger_level;
            }
        } else {
            // Bearish: 3rd candle low must break first break candle low - 0.6 pips
            double trigger_level = g_m15_retest.first_break_low - trigger_distance;
            
            if (m15_low <= trigger_level) {
                signal_triggered = true;
                signal_direction = "SELL";
                trigger_price = trigger_level;
            }
        }
        
        if (signal_triggered) {
            Print("🚨 SIGNAL TRIGGERED!");
            Print("   Direction: ", signal_direction);
            Print("   Trigger Price: ", DoubleToString(trigger_price, _Digits));
            Print("   3rd Candle: H=", DoubleToString(m15_high, _Digits), 
                  " L=", DoubleToString(m15_low, _Digits));
            
            // Send pure signal to Django MCP
            if (InpSendToDjango) {
                SendPureSignalToDjango(signal_direction, trigger_price);
            }
            
            // Reset monitoring for next opportunity
            InitializeRetestData();
            Print("🔄 Monitoring reset - Ready for next BOS opportunity");
        }
    }
}

//+------------------------------------------------------------------+
//| Get pip value for current symbol                                 |
//+------------------------------------------------------------------+
double GetPipValue() {
    double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
    int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
    
    // Handle JPY pairs specifically
    string currency_profit = SymbolInfoString(_Symbol, SYMBOL_CURRENCY_PROFIT);
    if (StringFind(currency_profit, "JPY") >= 0) {
        return point; // JPY pairs: pip = point
    } else {
        // Major pairs: pip = point * 10 for 5-digit brokers
        return (digits == 5) ? point * 10 : point;
    }
}

//+------------------------------------------------------------------+
//| Send PURE signal to Django MCP - NO trading calculations        |
//+------------------------------------------------------------------+
void SendPureSignalToDjango(string direction, double trigger_price) {
    // Create ISO 8601 timestamp
    MqlDateTime dt;
    TimeCurrent(dt);
    string timestamp = StringFormat("%04d-%02d-%02dT%02d:%02d:%02dZ", 
        dt.year, dt.mon, dt.day, dt.hour, dt.min, dt.sec);
    
    // Escape symbol name for JSON safety
    string safe_symbol = _Symbol;
    StringReplace(safe_symbol, "\"", "\\\"");
    
    // Create PURE signal JSON - No SL/TP/Risk calculations
    string json_data = StringFormat(
        "{"
        "\"ea_name\":\"MikroBot_BOS\","
        "\"ea_version\":\"1.04\","
        "\"signal_type\":\"BOS_RETEST\","
        "\"symbol\":\"%s\","
        "\"direction\":\"%s\","
        "\"trigger_price\":%.5f,"
        "\"h1_bos_level\":%.5f,"
        "\"h1_bos_direction\":\"%s\","
        "\"m15_break_high\":%.5f,"
        "\"m15_break_low\":%.5f,"
        "\"pip_trigger\":%.1f,"
        "\"timestamp\":\"%s\","
        "\"timeframe\":\"%s\","
        "\"timeframe_combination\":\"%s\","
        "\"higher_timeframe\":\"%s\","
        "\"lower_timeframe\":\"%s\","
        "\"account\":%d"
        "}",
        safe_symbol,
        direction,
        trigger_price,
        g_m15_retest.bos_level,
        (g_m15_retest.is_bullish_setup ? "BULLISH" : "BEARISH"),
        g_m15_retest.first_break_high,
        g_m15_retest.first_break_low,
        InpPipTrigger,
        timestamp,
        g_timeframes.lower_timeframe,
        g_timeframes.combination,
        g_timeframes.higher_timeframe,
        g_timeframes.lower_timeframe,
        (int)AccountInfoInteger(ACCOUNT_LOGIN)
    );
    
    Print("📡 Sending PURE signal to Django MCP (", StringLen(json_data), " bytes)");
    
    // Prepare HTTP request
    char post_data[];
    ArrayResize(post_data, StringLen(json_data));
    StringToCharArray(json_data, post_data, 0, StringLen(json_data));
    
    char response_data[];
    string response_headers;
    string headers = "Content-Type: application/json\r\nUser-Agent: MikroBot-BOS/1.04\r\n";
    
    // Execute HTTP POST request
    int http_result = WebRequest(
        "POST",
        InpDjangoURL,
        headers,
        InpTimeoutMS,
        post_data,
        response_data,
        response_headers
    );
    
    // Handle response
    if (http_result == 200) {
        string response = CharArrayToString(response_data);
        Print("✅ Django MCP confirmed signal receipt: ", response);
    } else if (http_result == -1) {
        Print("❌ WebRequest failed: URL not allowed or network error");
        Print("💡 Check: Tools → Options → Expert Advisors → Allow WebRequest for: ", InpDjangoURL);
    } else {
        Print("❌ Django MCP responded with HTTP ", http_result);
        if (ArraySize(response_data) > 0) {
            string error_response = CharArrayToString(response_data);
            Print("📄 Error details: ", error_response);
        }
    }
}

//+------------------------------------------------------------------+
//| Fetch timeframe settings from Django                            |
//+------------------------------------------------------------------+
void FetchTimeframeSettings() {
    // Create JSON request for timeframe settings
    string json_request = StringFormat(
        "{"
        "\"action\":\"GET_TIMEFRAMES\","
        "\"symbol\":\"%s\""
        "}",
        _Symbol
    );
    
    Print("📡 Fetching timeframe settings from Django...");
    
    // Prepare HTTP request
    char post_data[];
    ArrayResize(post_data, StringLen(json_request));
    StringToCharArray(json_request, post_data, 0, StringLen(json_request));
    
    char response_data[];
    string response_headers;
    string headers = "Content-Type: application/json\r\nUser-Agent: MikroBot-BOS/1.04\r\n";
    
    // Execute HTTP POST request
    int http_result = WebRequest(
        "POST",
        InpTimeframeURL,
        headers,
        InpTimeoutMS,
        post_data,
        response_data,
        response_headers
    );
    
    // Handle response
    if (http_result == 200) {
        string response = CharArrayToString(response_data);
        Print("✅ Django timeframe response: ", response);
        
        // Parse response for timeframe settings
        ParseTimeframeResponse(response);
    } else {
        Print("❌ Failed to fetch timeframes from Django, HTTP code: ", http_result);
        Print("💡 Using default timeframes: H1/M15");
    }
}

//+------------------------------------------------------------------+
//| Parse timeframe response from Django                            |
//+------------------------------------------------------------------+
void ParseTimeframeResponse(string response) {
    // Simple JSON parsing for timeframe settings
    // Look for "timeframe_combination":"H1/M15" pattern
    
    int combo_pos = StringFind(response, "timeframe_combination");
    if (combo_pos >= 0) {
        int start_quote = StringFind(response, "\"", combo_pos + 20);
        int end_quote = StringFind(response, "\"", start_quote + 1);
        
        if (start_quote >= 0 && end_quote > start_quote) {
            string new_combination = StringSubstr(response, start_quote + 1, end_quote - start_quote - 1);
            
            // Parse combination (e.g., "H1/M15")
            int slash_pos = StringFind(new_combination, "/");
            if (slash_pos > 0) {
                string higher = StringSubstr(new_combination, 0, slash_pos);
                string lower = StringSubstr(new_combination, slash_pos + 1);
                
                // Update global timeframe settings
                bool settings_changed = (g_timeframes.combination != new_combination);
                
                g_timeframes.higher_timeframe = higher;
                g_timeframes.lower_timeframe = lower;
                g_timeframes.combination = new_combination;
                g_timeframes.last_update = TimeCurrent();
                g_timeframes.is_valid = true;
                
                if (settings_changed) {
                    Print("⚡ Timeframe settings updated: ", new_combination);
                    Print("   Higher TF: ", higher);
                    Print("   Lower TF: ", lower);
                    
                    // Reset monitoring when timeframes change
                    InitializeBOSData();
                    InitializeRetestData();
                } else {
                    Print("✅ Timeframe settings confirmed: ", new_combination);
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Check for timeframe updates                                     |
//+------------------------------------------------------------------+
void CheckTimeframeUpdates() {
    // Only check if it's been more than 5 minutes since last update
    if ((TimeCurrent() - g_timeframes.last_update) >= 300) {
        FetchTimeframeSettings();
    }
}

//+------------------------------------------------------------------+
//| End of MikroBot_BOS.mq5 - PURE SIGNAL DETECTOR                  |
//+------------------------------------------------------------------+