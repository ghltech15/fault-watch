import React, { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:8000';

// Fetch helper with error handling
const fetchAPI = async (endpoint) => {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    return null;
  }
};

const FaultWatchDashboard = () => {
  // State for API data
  const [dashboardData, setDashboardData] = useState(null);
  const [watchlistSignals, setWatchlistSignals] = useState([]);
  const [shanghaiPremium, setShanghaiPremium] = useState(null);
  const [bankDivergence, setBankDivergence] = useState([]);
  const [regionalBanks, setRegionalBanks] = useState(null);
  const [cotData, setCotData] = useState(null);
  const [nakedShorts, setNakedShorts] = useState(null);
  const [theories, setTheories] = useState([]);
  const [contagion, setContagion] = useState(null);

  // UI state
  const [time, setTime] = useState(new Date());
  const [tickerOffset, setTickerOffset] = useState(0);
  const [hoveredBank, setHoveredBank] = useState(null);
  const [showPulse, setShowPulse] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch all data
  const fetchAllData = useCallback(async () => {
    try {
      const [
        dashboard,
        signals,
        shanghai,
        divergence,
        regionals,
        cot,
        shorts,
        theoriesData,
        contagionData
      ] = await Promise.all([
        fetchAPI('/api/dashboard'),
        fetchAPI('/api/watchlist/signals'),
        fetchAPI('/api/watchlist/shanghai-premium'),
        fetchAPI('/api/watchlist/bank-divergence'),
        fetchAPI('/api/watchlist/regional-banks'),
        fetchAPI('/api/watchlist/cot'),
        fetchAPI('/api/naked-shorts'),
        fetchAPI('/api/theories'),
        fetchAPI('/api/contagion')
      ]);

      if (dashboard) setDashboardData(dashboard);
      if (signals) setWatchlistSignals(signals.signals || []);
      if (shanghai) setShanghaiPremium(shanghai);
      if (divergence) setBankDivergence(divergence.all_banks || []);
      if (regionals) setRegionalBanks(regionals);
      if (cot) setCotData(cot);
      if (shorts) setNakedShorts(shorts);
      if (theoriesData) setTheories(theoriesData);
      if (contagionData) setContagion(contagionData);

      setLastUpdate(new Date());
      setLoading(false);
      setError(null);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchAllData]);

  // Clock timer
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Animate ticker tape
  useEffect(() => {
    const ticker = setInterval(() => {
      setTickerOffset(prev => prev - 1);
    }, 30);
    return () => clearInterval(ticker);
  }, []);

  // Pulse effect
  useEffect(() => {
    const pulse = setInterval(() => setShowPulse(p => !p), 1000);
    return () => clearInterval(pulse);
  }, []);

  // Helper functions
  const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined) return '—';
    return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  };

  const formatBillions = (num) => {
    if (!num) return '—';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(1)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`;
    return `$${num.toLocaleString()}`;
  };

  const getCountdown = (dateStr) => {
    const target = new Date(dateStr);
    const now = new Date();
    const diff = target - now;
    if (diff <= 0) return { days: 0, hours: 0, mins: 0, secs: 0, expired: true };
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diff % (1000 * 60)) / 1000);
    return { days, hours, mins, secs, expired: false };
  };

  const getRiskColor = (risk) => {
    if (risk >= 8) return '#ff3b5c';
    if (risk >= 6) return '#ff8c42';
    if (risk >= 4) return '#fbbf24';
    return '#00f5d4';
  };

  const getStatusColor = (status) => {
    const colors = {
      'critical': '#ff3b5c',
      'warning': '#ff8c42',
      'elevated': '#fbbf24',
      'active': '#00f5d4',
      'long': '#4ade80',
      'LONG': '#4ade80',
      'SHORT': '#ff8c42',
      'normal': '#00f5d4',
      'info': '#5a6b8a'
    };
    return colors[status] || '#5a6b8a';
  };

  const getDominoColor = (status) => {
    const colors = {
      'CRITICAL': '#ff3b5c',
      'WARNING': '#ff8c42',
      'ELEVATED': '#fbbf24',
      'STABLE': '#00f5d4'
    };
    return colors[status] || '#2a3548';
  };

  // Loading state
  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#080b12',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          border: '3px solid #1a2030',
          borderTop: '3px solid #00f5d4',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <div style={{ color: '#5a6b8a', fontSize: '14px', letterSpacing: '2px' }}>
          LOADING FAULT.WATCH...
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Extract data from API responses
  const riskIndex = dashboardData?.risk_index || 0;
  const riskLabel = dashboardData?.risk_label || 'UNKNOWN';
  const riskColor = getRiskColor(riskIndex);
  const prices = dashboardData?.prices || {};
  const alerts = dashboardData?.alerts || [];
  const dominoes = dashboardData?.dominoes || [];
  const countdowns = dashboardData?.countdowns || {};

  // Get silver price from SLV or silver key
  const silverPrice = prices.silver?.price || prices.slv?.price || 0;
  const silverChange = prices.silver?.change_pct || prices.slv?.change_pct || 0;

  // Build bank data from naked shorts API
  const bankPositions = nakedShorts?.bank_positions || [];

  // Critical alerts for ticker
  const criticalAlerts = alerts.filter(a => a.level === 'critical');
  const hasCritical = criticalAlerts.length > 0;

  // Countdown dates
  const lloydsCountdown = getCountdown(countdowns.lloyds?.deadline || '2026-01-31T23:59:59');
  const secCountdown = getCountdown(countdowns.sec?.deadline || '2026-02-15T16:00:00');

  return (
    <div style={{
      minHeight: '100vh',
      background: '#080b12',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      color: '#e8eef5',
      overflow: 'hidden'
    }}>
      {/* Animated Background */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(ellipse at 20% 20%, rgba(255, 59, 92, 0.08) 0%, transparent 50%),
          radial-gradient(ellipse at 80% 80%, rgba(0, 245, 212, 0.05) 0%, transparent 50%),
          radial-gradient(ellipse at 50% 50%, rgba(255, 140, 66, 0.03) 0%, transparent 50%)
        `,
        pointerEvents: 'none'
      }} />

      {/* Grid overlay */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
          linear-gradient(rgba(0, 245, 212, 0.02) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 245, 212, 0.02) 1px, transparent 1px)
        `,
        backgroundSize: '60px 60px',
        pointerEvents: 'none'
      }} />

      {/* Breaking News Ticker */}
      {hasCritical && (
        <div style={{
          position: 'relative',
          zIndex: 100,
          background: 'linear-gradient(90deg, #ff3b5c 0%, #ff1744 50%, #ff3b5c 100%)',
          padding: '10px 0',
          overflow: 'hidden',
          borderBottom: '2px solid #ff3b5c'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            whiteSpace: 'nowrap',
            transform: `translateX(${tickerOffset}px)`
          }}>
            {[...Array(3)].map((_, i) => (
              <React.Fragment key={i}>
                {criticalAlerts.map((alert, idx) => (
                  <span key={`${i}-${idx}`} style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    marginRight: '80px',
                    fontSize: '13px',
                    fontWeight: 700,
                    letterSpacing: '0.5px'
                  }}>
                    <span style={{
                      background: 'rgba(0,0,0,0.3)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      marginRight: '12px',
                      fontSize: '11px'
                    }}>
                      {alert.title?.split(' ')[0] || 'ALERT'}
                    </span>
                    {alert.detail?.toUpperCase() || alert.title?.toUpperCase()}
                    <span style={{ margin: '0 40px', opacity: 0.5 }}>●</span>
                  </span>
                ))}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Header with Risk Gauge */}
      <header style={{
        position: 'relative',
        zIndex: 10,
        padding: '20px 40px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        background: 'rgba(8, 11, 18, 0.9)',
        backdropFilter: 'blur(20px)'
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{
            position: 'relative',
            width: '56px',
            height: '56px'
          }}>
            <div style={{
              position: 'absolute',
              inset: 0,
              borderRadius: '14px',
              background: `linear-gradient(135deg, ${riskColor} 0%, ${riskColor}88 100%)`,
              opacity: showPulse && hasCritical ? 0.8 : 0.4,
              filter: 'blur(12px)',
              transition: 'opacity 0.5s ease'
            }} />
            <div style={{
              position: 'relative',
              width: '100%',
              height: '100%',
              borderRadius: '14px',
              background: `linear-gradient(135deg, ${riskColor}22 0%, ${riskColor}11 100%)`,
              border: `2px solid ${riskColor}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '28px'
            }}>
              ⚡
            </div>
          </div>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '32px',
              fontWeight: 800,
              letterSpacing: '-1px',
              background: `linear-gradient(135deg, #fff 0%, ${riskColor} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              FAULT.WATCH
            </h1>
            <p style={{
              margin: 0,
              fontSize: '11px',
              color: '#5a6b8a',
              letterSpacing: '3px',
              textTransform: 'uppercase',
              fontWeight: 500
            }}>
              Systemic Risk Monitor • LIVE
            </p>
          </div>
        </div>

        {/* Central Risk Gauge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
          padding: '12px 32px',
          background: 'rgba(255,255,255,0.02)',
          borderRadius: '16px',
          border: `1px solid ${riskColor}33`
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: '#5a6b8a', letterSpacing: '2px', marginBottom: '4px' }}>
              THREAT LEVEL
            </div>
            <div style={{
              fontSize: '42px',
              fontWeight: 800,
              color: riskColor,
              lineHeight: 1,
              textShadow: `0 0 40px ${riskColor}66`
            }}>
              {riskIndex.toFixed(1)}
            </div>
          </div>
          <div style={{
            width: '1px',
            height: '50px',
            background: 'rgba(255,255,255,0.1)'
          }} />
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{
              padding: '6px 16px',
              background: `${riskColor}22`,
              border: `1px solid ${riskColor}`,
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 700,
              color: riskColor,
              letterSpacing: '2px'
            }}>
              {riskLabel}
            </div>
            <div style={{
              display: 'flex',
              gap: '3px'
            }}>
              {[...Array(10)].map((_, i) => (
                <div key={i} style={{
                  width: '16px',
                  height: '6px',
                  borderRadius: '2px',
                  background: i < riskIndex
                    ? i < 4 ? '#00f5d4' : i < 6 ? '#fbbf24' : i < 8 ? '#ff8c42' : '#ff3b5c'
                    : 'rgba(255,255,255,0.1)',
                  transition: 'background 0.3s ease'
                }} />
              ))}
            </div>
          </div>
        </div>

        {/* Time and Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{
              fontSize: '28px',
              fontWeight: 600,
              color: '#fff',
              fontFamily: "'JetBrains Mono', monospace"
            }}>
              {time.toLocaleTimeString('en-US', { hour12: false })}
            </div>
            <div style={{ fontSize: '11px', color: '#5a6b8a' }}>
              {lastUpdate ? `Updated ${Math.floor((new Date() - lastUpdate) / 1000)}s ago` : 'Connecting...'}
            </div>
          </div>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: error ? '#ff3b5c' : '#00f5d4',
            boxShadow: `0 0 20px ${error ? '#ff3b5c' : '#00f5d4'}`,
            animation: 'pulse 2s infinite'
          }} />
        </div>
      </header>

      {/* Crisis Countdowns */}
      <div style={{
        position: 'relative',
        zIndex: 10,
        display: 'flex',
        justifyContent: 'center',
        gap: '40px',
        padding: '20px 40px',
        background: 'rgba(255, 59, 92, 0.03)',
        borderBottom: '1px solid rgba(255,255,255,0.05)'
      }}>
        {[
          { label: "LLOYD'S DEADLINE", countdown: lloydsCountdown, critical: true },
          { label: "SEC ENFORCEMENT", countdown: secCountdown, critical: false }
        ].map((item, idx) => (
          <div key={idx} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            padding: '12px 24px',
            background: item.critical ? 'rgba(255, 59, 92, 0.1)' : 'rgba(255, 140, 66, 0.1)',
            border: `1px solid ${item.critical ? '#ff3b5c44' : '#ff8c4244'}`,
            borderRadius: '12px'
          }}>
            <div>
              <div style={{
                fontSize: '10px',
                color: item.critical ? '#ff3b5c' : '#ff8c42',
                letterSpacing: '2px',
                marginBottom: '4px',
                fontWeight: 600
              }}>
                {item.label}
              </div>
              <div style={{
                display: 'flex',
                gap: '8px',
                fontFamily: "'JetBrains Mono', monospace"
              }}>
                {[
                  { val: item.countdown.days, label: 'D' },
                  { val: item.countdown.hours, label: 'H' },
                  { val: item.countdown.mins, label: 'M' },
                  { val: item.countdown.secs, label: 'S' }
                ].map((unit, i) => (
                  <div key={i} style={{ textAlign: 'center' }}>
                    <div style={{
                      fontSize: '24px',
                      fontWeight: 700,
                      color: '#fff',
                      minWidth: '36px',
                      padding: '4px 8px',
                      background: 'rgba(0,0,0,0.3)',
                      borderRadius: '6px'
                    }}>
                      {String(unit.val).padStart(2, '0')}
                    </div>
                    <div style={{ fontSize: '9px', color: '#5a6b8a', marginTop: '2px' }}>
                      {unit.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <main style={{
        position: 'relative',
        zIndex: 10,
        padding: '24px 40px',
        display: 'grid',
        gap: '20px'
      }}>

        {/* Top Metrics Row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '16px'
        }}>
          {/* Silver Spot Card */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(192, 192, 192, 0.08) 0%, rgba(20, 25, 35, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: '1px solid rgba(192, 192, 192, 0.2)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: '-30px',
              right: '-30px',
              fontSize: '100px',
              opacity: 0.05
            }}>🥈</div>
            <div style={{ fontSize: '11px', color: '#8b9dc3', letterSpacing: '2px', marginBottom: '8px' }}>
              SILVER SPOT
            </div>
            <div style={{
              fontSize: '40px',
              fontWeight: 800,
              background: 'linear-gradient(180deg, #e8e8e8 0%, #a0a0a0 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              ${formatNumber(silverPrice)}
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '8px'
            }}>
              <span style={{
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                background: silverChange >= 0 ? 'rgba(0, 245, 212, 0.15)' : 'rgba(255, 59, 92, 0.15)',
                color: silverChange >= 0 ? '#00f5d4' : '#ff3b5c'
              }}>
                {silverChange >= 0 ? '↑' : '↓'} {formatNumber(Math.abs(silverChange))}%
              </span>
              <span style={{ fontSize: '12px', color: '#5a6b8a' }}>24h</span>
            </div>
          </div>

          {/* Shanghai Premium */}
          <div style={{
            background: shanghaiPremium?.premium_pct >= 10
              ? 'linear-gradient(135deg, #ff3b5c 0%, #ff1744 100%)'
              : shanghaiPremium?.premium_pct >= 7
              ? 'linear-gradient(135deg, #ff8c42 0%, #ff6b00 100%)'
              : 'linear-gradient(135deg, #00f5d4 0%, #00bfa5 100%)',
            borderRadius: '20px',
            padding: '24px',
            position: 'relative',
            overflow: 'hidden',
            boxShadow: shanghaiPremium?.premium_pct >= 10 ? '0 0 60px rgba(255, 59, 92, 0.4)' : 'none'
          }}>
            <div style={{
              position: 'absolute',
              bottom: '-20px',
              right: '-10px',
              fontSize: '120px',
              fontWeight: 900,
              opacity: 0.15
            }}>%</div>
            <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.8)', letterSpacing: '2px', marginBottom: '8px' }}>
              SHANGHAI PREMIUM
            </div>
            <div style={{ fontSize: '40px', fontWeight: 800, color: '#fff' }}>
              +{formatNumber(shanghaiPremium?.premium_pct || 0)}%
            </div>
            <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)', marginTop: '8px' }}>
              {shanghaiPremium?.status?.toUpperCase() || 'LOADING'}
            </div>
            {shanghaiPremium?.premium_pct >= 10 && (
              <div style={{
                position: 'absolute',
                top: '12px',
                right: '12px',
                padding: '4px 10px',
                background: 'rgba(0,0,0,0.4)',
                borderRadius: '20px',
                fontSize: '10px',
                fontWeight: 700,
                letterSpacing: '1px'
              }}>
                ⚠️ CRITICAL
              </div>
            )}
          </div>

          {/* COMEX Inventory */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(255, 140, 66, 0.08) 0%, rgba(20, 25, 35, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: `1px solid ${contagion?.comex?.registered_oz < 100000000 ? '#ff3b5c44' : '#ff8c4244'}`,
            position: 'relative'
          }}>
            <div style={{ fontSize: '11px', color: '#8b9dc3', letterSpacing: '2px', marginBottom: '8px' }}>
              COMEX REGISTERED
            </div>
            <div style={{
              fontSize: '40px',
              fontWeight: 800,
              color: contagion?.comex?.registered_oz < 100000000 ? '#ff3b5c' : '#ff8c42'
            }}>
              {contagion?.comex?.registered_oz
                ? `${(contagion.comex.registered_oz / 1000000).toFixed(1)}M`
                : '—'}
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '8px'
            }}>
              <span style={{
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                background: 'rgba(255, 140, 66, 0.15)',
                color: '#ff8c42'
              }}>
                {contagion?.comex?.status?.toUpperCase() || 'LOADING'}
              </span>
            </div>
            {/* Progress bar */}
            <div style={{
              marginTop: '16px',
              height: '8px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                width: `${Math.min(((contagion?.comex?.registered_oz || 0) / 150000000) * 100, 100)}%`,
                background: contagion?.comex?.registered_oz < 100000000
                  ? 'linear-gradient(90deg, #ff3b5c, #ff8c42)'
                  : 'linear-gradient(90deg, #ff8c42, #fbbf24)',
                borderRadius: '4px'
              }} />
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '10px',
              color: '#5a6b8a',
              marginTop: '4px'
            }}>
              <span>0</span>
              <span style={{ color: '#ff3b5c' }}>Critical: 100M</span>
              <span>150M</span>
            </div>
          </div>

          {/* Contagion Score */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 20, 30, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: `1px solid ${contagion?.contagion_color || '#00f5d4'}33`,
            position: 'relative'
          }}>
            <div style={{ fontSize: '11px', color: '#8b9dc3', letterSpacing: '2px', marginBottom: '8px' }}>
              CONTAGION SCORE
            </div>
            <div style={{
              fontSize: '40px',
              fontWeight: 800,
              color: contagion?.contagion_color || '#00f5d4'
            }}>
              {formatNumber(contagion?.contagion_score || 0, 1)}
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '8px'
            }}>
              <span style={{
                padding: '4px 12px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 700,
                background: `${contagion?.contagion_color || '#00f5d4'}22`,
                color: contagion?.contagion_color || '#00f5d4',
                textTransform: 'uppercase'
              }}>
                {contagion?.contagion_level || 'LOADING'}
              </span>
            </div>
            <div style={{
              marginTop: '12px',
              fontSize: '11px',
              color: '#5a6b8a'
            }}>
              Stage {contagion?.cascade_stage || 1}/5
            </div>
          </div>
        </div>

        {/* Domino Cascade Visualization */}
        <div style={{
          background: 'linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 20, 30, 0.95) 100%)',
          borderRadius: '20px',
          padding: '24px',
          border: '1px solid rgba(255,255,255,0.05)'
        }}>
          <div style={{
            fontSize: '11px',
            color: '#8b9dc3',
            letterSpacing: '2px',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            DOMINO CASCADE TRACKER
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '8px'
          }}>
            {dominoes.map((domino, idx) => (
              <React.Fragment key={domino.id}>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <div style={{
                    width: '80px',
                    height: '100px',
                    borderRadius: '12px',
                    background: getDominoColor(domino.status),
                    border: `2px solid ${domino.color || '#3a4558'}`,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    boxShadow: domino.status === 'CRITICAL'
                      ? '0 0 30px rgba(255, 59, 92, 0.5)'
                      : domino.status === 'WARNING'
                      ? '0 0 20px rgba(255, 140, 66, 0.3)'
                      : 'none',
                    transform: domino.status === 'CRITICAL' ? 'rotate(-15deg)' : 'rotate(0deg)',
                    transition: 'all 0.5s ease'
                  }}>
                    <span style={{ fontSize: '24px', fontWeight: 700, color: domino.color || '#5a6b8a' }}>
                      {idx + 1}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '10px',
                    color: domino.status === 'STABLE' ? '#5a6b8a' : '#fff',
                    fontWeight: 600,
                    textAlign: 'center',
                    maxWidth: '80px'
                  }}>
                    {domino.label}
                  </div>
                  <div style={{
                    fontSize: '9px',
                    color: domino.color || '#5a6b8a',
                    fontWeight: 600
                  }}>
                    {domino.detail}
                  </div>
                </div>
                {idx < dominoes.length - 1 && (
                  <div style={{
                    width: '40px',
                    height: '2px',
                    background: domino.status !== 'STABLE'
                      ? 'linear-gradient(90deg, #ff3b5c, #ff8c42)'
                      : 'rgba(255,255,255,0.1)',
                    marginBottom: '60px'
                  }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Middle Section - Banks and Alerts */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr',
          gap: '20px'
        }}>
          {/* Bank Monitor Table */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 20, 30, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h2 style={{
                margin: 0,
                fontSize: '13px',
                letterSpacing: '2px',
                color: '#8b9dc3',
                textTransform: 'uppercase'
              }}>
                Bank Short Position Monitor
              </h2>
              <div style={{
                padding: '6px 14px',
                background: 'rgba(255, 140, 66, 0.15)',
                borderRadius: '20px',
                fontSize: '11px',
                color: '#ff8c42',
                fontWeight: 600
              }}>
                {nakedShorts?.banks_insolvent_at_80?.length || 0} AT RISK @ $80
              </div>
            </div>

            <div style={{ display: 'grid', gap: '8px' }}>
              {/* Header */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '70px 130px 100px 80px 90px 80px',
                gap: '12px',
                padding: '10px 16px',
                fontSize: '10px',
                color: '#5a6b8a',
                letterSpacing: '1px',
                textTransform: 'uppercase',
                borderBottom: '1px solid rgba(255,255,255,0.05)'
              }}>
                <div>Ticker</div>
                <div>Name</div>
                <div style={{ textAlign: 'right' }}>Short Position</div>
                <div style={{ textAlign: 'right' }}>Equity</div>
                <div style={{ textAlign: 'right' }}>Insolvent @</div>
                <div style={{ textAlign: 'center' }}>Position</div>
              </div>

              {/* Rows */}
              {bankPositions.map((bank) => (
                <div
                  key={bank.ticker}
                  onMouseEnter={() => setHoveredBank(bank.ticker)}
                  onMouseLeave={() => setHoveredBank(null)}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '70px 130px 100px 80px 90px 80px',
                    gap: '12px',
                    padding: '14px 16px',
                    background: hoveredBank === bank.ticker
                      ? 'rgba(255,255,255,0.05)'
                      : bank.position === 'SHORT'
                      ? 'rgba(255, 140, 66, 0.03)'
                      : 'rgba(74, 222, 128, 0.03)',
                    borderRadius: '10px',
                    alignItems: 'center',
                    border: `1px solid ${bank.position === 'SHORT' ? '#ff8c4222' : '#4ade8022'}`,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{
                    fontWeight: 700,
                    color: getStatusColor(bank.position),
                    fontSize: '15px'
                  }}>
                    {bank.ticker}
                  </div>
                  <div style={{ color: '#8b9dc3', fontSize: '12px' }}>{bank.name}</div>
                  <div style={{
                    textAlign: 'right',
                    fontWeight: 600,
                    color: bank.position === 'LONG' ? '#4ade80' : '#ff8c42',
                    fontSize: '12px'
                  }}>
                    {(bank.ounces / 1e9).toFixed(2)}B oz
                  </div>
                  <div style={{ textAlign: 'right', fontWeight: 600, fontSize: '12px', color: '#8b9dc3' }}>
                    {formatBillions(bank.equity)}
                  </div>
                  <div style={{
                    textAlign: 'right',
                    color: bank.insolvency_price ? '#ff3b5c' : '#4ade80',
                    fontWeight: 600,
                    fontSize: '13px'
                  }}>
                    {bank.insolvency_price ? `$${bank.insolvency_price}` : 'N/A'}
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      display: 'inline-block',
                      padding: '4px 10px',
                      borderRadius: '20px',
                      fontSize: '10px',
                      fontWeight: 700,
                      background: `${getStatusColor(bank.position)}22`,
                      color: getStatusColor(bank.position),
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      {bank.position}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Total Summary */}
            <div style={{
              marginTop: '16px',
              padding: '16px',
              background: 'rgba(255, 59, 92, 0.1)',
              borderRadius: '12px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontSize: '10px', color: '#ff3b5c', letterSpacing: '1px' }}>TOTAL NAKED SHORT</div>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#ff3b5c' }}>
                  {nakedShorts?.total_short_oz ? `${(nakedShorts.total_short_oz / 1e9).toFixed(1)}B oz` : '—'}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '10px', color: '#5a6b8a', letterSpacing: '1px' }}>PAPER:PHYSICAL RATIO</div>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#ff8c42' }}>
                  {nakedShorts?.paper_to_physical_ratio || '—'}:1
                </div>
              </div>
            </div>
          </div>

          {/* Live Alerts */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 20, 30, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: '1px solid rgba(255,255,255,0.05)',
            maxHeight: '500px',
            overflow: 'auto'
          }}>
            <h2 style={{
              margin: '0 0 20px 0',
              fontSize: '13px',
              letterSpacing: '2px',
              color: '#8b9dc3',
              textTransform: 'uppercase'
            }}>
              Live Alerts ({alerts.length})
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {alerts.length === 0 ? (
                <div style={{
                  padding: '20px',
                  textAlign: 'center',
                  color: '#5a6b8a',
                  fontSize: '13px'
                }}>
                  No active alerts
                </div>
              ) : (
                alerts.map((alert, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    padding: '14px',
                    background: alert.level === 'critical'
                      ? 'rgba(255, 59, 92, 0.1)'
                      : alert.level === 'warning'
                      ? 'rgba(255, 140, 66, 0.05)'
                      : 'rgba(255,255,255,0.02)',
                    borderRadius: '12px',
                    borderLeft: `4px solid ${getStatusColor(alert.level)}`
                  }}>
                    <div style={{
                      minWidth: '60px',
                      padding: '4px 8px',
                      background: 'rgba(0,0,0,0.3)',
                      borderRadius: '6px',
                      fontSize: '9px',
                      fontWeight: 700,
                      textAlign: 'center',
                      color: getStatusColor(alert.level),
                      textTransform: 'uppercase'
                    }}>
                      {alert.level}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{
                        fontSize: '13px',
                        color: '#e8eef5',
                        lineHeight: 1.4,
                        fontWeight: alert.level === 'critical' ? 600 : 400
                      }}>
                        {alert.title}
                      </div>
                      <div style={{ fontSize: '11px', color: '#8b9dc3', marginTop: '4px' }}>
                        {alert.detail}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Bottom Row - Credit Stress and COT */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '20px'
        }}>
          {/* Credit Stress */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 20, 30, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <h2 style={{
              margin: '0 0 20px 0',
              fontSize: '13px',
              letterSpacing: '2px',
              color: '#8b9dc3',
              textTransform: 'uppercase'
            }}>
              Credit Stress Indicators
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
              {[
                { label: 'TED Spread', value: contagion?.credit_stress?.ted_spread, suffix: '%' },
                { label: 'Credit Spread', value: contagion?.credit_stress?.credit_spread, suffix: 'bps' },
                { label: 'HY Spread', value: contagion?.credit_stress?.high_yield_spread, suffix: 'bps' },
                { label: 'SOFR Rate', value: contagion?.credit_stress?.sofr_rate, suffix: '%' }
              ].map((item, idx) => (
                <div key={idx} style={{
                  padding: '16px',
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '12px'
                }}>
                  <div style={{ fontSize: '10px', color: '#5a6b8a', letterSpacing: '1px', marginBottom: '8px' }}>
                    {item.label.toUpperCase()}
                  </div>
                  <div style={{
                    fontSize: '24px',
                    fontWeight: 700,
                    color: '#fff'
                  }}>
                    {item.value ? `${formatNumber(item.value)}${item.suffix}` : '—'}
                  </div>
                </div>
              ))}
            </div>

            <div style={{
              marginTop: '16px',
              padding: '12px 16px',
              background: `${contagion?.credit_stress?.stress_level === 'extreme' ? '#ff3b5c' : contagion?.credit_stress?.stress_level === 'high' ? '#ff8c42' : '#00f5d4'}22`,
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{ fontSize: '11px', color: '#8b9dc3' }}>STRESS LEVEL</span>
              <span style={{
                fontSize: '13px',
                fontWeight: 700,
                color: contagion?.credit_stress?.stress_level === 'extreme' ? '#ff3b5c' : contagion?.credit_stress?.stress_level === 'high' ? '#ff8c42' : '#00f5d4',
                textTransform: 'uppercase'
              }}>
                {contagion?.credit_stress?.stress_level || 'LOADING'}
              </span>
            </div>
          </div>

          {/* COT Data */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(20, 25, 35, 0.95) 0%, rgba(15, 20, 30, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <h2 style={{
              margin: '0 0 20px 0',
              fontSize: '13px',
              letterSpacing: '2px',
              color: '#8b9dc3',
              textTransform: 'uppercase'
            }}>
              CFTC COT Positioning
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
              <div style={{
                padding: '16px',
                background: 'rgba(255, 59, 92, 0.1)',
                borderRadius: '12px',
                borderLeft: '3px solid #ff3b5c'
              }}>
                <div style={{ fontSize: '10px', color: '#ff3b5c', letterSpacing: '1px', marginBottom: '8px' }}>
                  COMMERCIALS NET
                </div>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#ff3b5c' }}>
                  {cotData?.commercial_net ? formatNumber(cotData.commercial_net, 0) : '—'}
                </div>
                <div style={{ fontSize: '10px', color: '#5a6b8a', marginTop: '4px' }}>
                  contracts
                </div>
              </div>

              <div style={{
                padding: '16px',
                background: 'rgba(0, 245, 212, 0.1)',
                borderRadius: '12px',
                borderLeft: '3px solid #00f5d4'
              }}>
                <div style={{ fontSize: '10px', color: '#00f5d4', letterSpacing: '1px', marginBottom: '8px' }}>
                  MANAGED MONEY NET
                </div>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#00f5d4' }}>
                  {cotData?.managed_money_net ? formatNumber(cotData.managed_money_net, 0) : '—'}
                </div>
                <div style={{ fontSize: '10px', color: '#5a6b8a', marginTop: '4px' }}>
                  contracts
                </div>
              </div>
            </div>

            <div style={{
              marginTop: '16px',
              padding: '12px 16px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '8px'
            }}>
              <div style={{ fontSize: '10px', color: '#5a6b8a', marginBottom: '8px' }}>OPEN INTEREST</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#fff' }}>
                {cotData?.open_interest ? formatNumber(cotData.open_interest, 0) : '—'} contracts
              </div>
            </div>

            {cotData?.signal && (
              <div style={{
                marginTop: '12px',
                padding: '10px 14px',
                background: 'rgba(255, 179, 71, 0.1)',
                borderRadius: '8px',
                fontSize: '11px',
                color: '#ffb347',
                lineHeight: 1.4
              }}>
                💡 {cotData.signal}
              </div>
            )}
          </div>
        </div>

        {/* Working Theories */}
        {theories.length > 0 && (
          <div style={{
            background: 'linear-gradient(180deg, rgba(255, 140, 66, 0.05) 0%, rgba(20, 25, 35, 0.95) 100%)',
            borderRadius: '20px',
            padding: '24px',
            border: '1px solid rgba(255, 140, 66, 0.2)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '20px'
            }}>
              <span style={{ fontSize: '20px' }}>🔮</span>
              <h2 style={{
                margin: 0,
                fontSize: '13px',
                letterSpacing: '2px',
                color: '#ff8c42',
                textTransform: 'uppercase'
              }}>
                Working Theories (Not Verified)
              </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              {theories.slice(0, 3).map((theory, idx) => (
                <div key={idx} style={{
                  padding: '16px',
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 140, 66, 0.1)'
                }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '8px'
                  }}>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>
                      {theory.title}
                    </div>
                    <div style={{
                      padding: '2px 8px',
                      background: 'rgba(255, 140, 66, 0.2)',
                      borderRadius: '10px',
                      fontSize: '10px',
                      color: '#ff8c42',
                      fontWeight: 600
                    }}>
                      {theory.confidence}%
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#8b9dc3', lineHeight: 1.4 }}>
                    {theory.hypothesis}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* CSS Animations */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(0.95); }
        }

        * {
          box-sizing: border-box;
        }

        ::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }

        ::-webkit-scrollbar-track {
          background: rgba(255,255,255,0.02);
        }

        ::-webkit-scrollbar-thumb {
          background: rgba(255,255,255,0.1);
          border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: rgba(255,255,255,0.2);
        }
      `}</style>
    </div>
  );
};

export default FaultWatchDashboard;
