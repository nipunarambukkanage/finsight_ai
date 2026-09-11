import React, { useRef, useEffect, useState } from 'react';
import { PriceBar } from '../types';

interface PriceChartProps {
  prices: PriceBar[];
  height?: number;
  showSMA?: boolean;
  showBollinger?: boolean;
}

export const PriceChart: React.FC<PriceChartProps> = ({
  prices,
  height = 420,
  showSMA = true,
  showBollinger = false
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick');
  const [hoverBar, setHoverBar] = useState<PriceBar | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || prices.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;


    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const priceH = h * 0.75;
    const volH = h * 0.2;
    const volTop = h * 0.8;

    ctx.clearRect(0, 0, w, h);


    let minP = Math.min(...prices.map(p => p.low));
    let maxP = Math.max(...prices.map(p => p.high));
    const padding = (maxP - minP) * 0.05;
    minP -= padding;
    maxP += padding;

    const maxVol = Math.max(...prices.map(p => p.volume), 1);

    const n = prices.length;
    const step = w / n;
    const barW = Math.max(1, step * 0.7);


    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    const gridLines = 5;
    for (let i = 0; i <= gridLines; i++) {
      const y = (priceH / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      const priceVal = maxP - ((maxP - minP) / gridLines) * i;
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`$${priceVal.toFixed(2)}`, w - 8, y - 4);
    }


    prices.forEach((bar, i) => {
      const x = i * step + step / 2;
      const vHeight = (bar.volume / maxVol) * volH;
      const isUp = bar.close >= bar.open;

      ctx.fillStyle = isUp ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)';
      ctx.fillRect(x - barW / 2, h - vHeight, barW, vHeight);
    });


    if (chartType === 'line') {
      ctx.beginPath();
      prices.forEach((bar, i) => {
        const x = i * step + step / 2;
        const y = priceH - ((bar.close - minP) / (maxP - minP)) * priceH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 2;
      ctx.stroke();


      ctx.lineTo((n - 1) * step + step / 2, priceH);
      ctx.lineTo(step / 2, priceH);
      ctx.closePath();
      const grad = ctx.createLinearGradient(0, 0, 0, priceH);
      grad.addColorStop(0, 'rgba(6, 182, 212, 0.2)');
      grad.addColorStop(1, 'rgba(6, 182, 212, 0.0)');
      ctx.fillStyle = grad;
      ctx.fill();
    } else {

      prices.forEach((bar, i) => {
        const x = i * step + step / 2;
        const yO = priceH - ((bar.open - minP) / (maxP - minP)) * priceH;
        const yC = priceH - ((bar.close - minP) / (maxP - minP)) * priceH;
        const yH = priceH - ((bar.high - minP) / (maxP - minP)) * priceH;
        const yL = priceH - ((bar.low - minP) / (maxP - minP)) * priceH;
        const isUp = bar.close >= bar.open;

        ctx.strokeStyle = isUp ? '#10b981' : '#f43f5e';
        ctx.fillStyle = isUp ? '#10b981' : '#f43f5e';
        ctx.lineWidth = 1;


        ctx.beginPath();
        ctx.moveTo(x, yH);
        ctx.lineTo(x, yL);
        ctx.stroke();


        const topY = Math.min(yO, yC);
        const candleH = Math.max(2, Math.abs(yC - yO));
        ctx.fillRect(x - barW / 2, topY, barW, candleH);
      });
    }


    if (showSMA && prices.length >= 20) {
      ctx.beginPath();
      for (let i = 19; i < prices.length; i++) {
        const slice = prices.slice(i - 19, i + 1);
        const avg = slice.reduce((acc, p) => acc + p.close, 0) / 20;
        const x = i * step + step / 2;
        const y = priceH - ((avg - minP) / (maxP - minP)) * priceH;
        if (i === 19) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }, [prices, chartType, showSMA, showBollinger]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || prices.length === 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const idx = Math.floor((x / rect.width) * prices.length);
    if (idx >= 0 && idx < prices.length) {
      setHoverBar(prices[idx]);
    }
  };

  const handleMouseLeave = () => {
    setHoverBar(null);
  };

  return (
    <div style={{ position: 'relative', width: '100%' }}>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '12px'
        }}
      >
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            id="chart-mode-candle-btn"
            className={`btn btn-sm ${chartType === 'candlestick' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setChartType('candlestick')}
          >
            Candlestick
          </button>
          <button
            id="chart-mode-line-btn"
            className={`btn btn-sm ${chartType === 'line' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setChartType('line')}
          >
            Line
          </button>
        </div>

        {hoverBar ? (
          <div
            style={{
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              gap: '12px',
              color: 'var(--text-secondary)'
            }}
          >
            <span>Date: <strong style={{ color: 'var(--text-primary)' }}>{hoverBar.date}</strong></span>
            <span>O: <strong>${hoverBar.open.toFixed(2)}</strong></span>
            <span>H: <strong>${hoverBar.high.toFixed(2)}</strong></span>
            <span>L: <strong>${hoverBar.low.toFixed(2)}</strong></span>
            <span>C: <strong style={{ color: hoverBar.close >= hoverBar.open ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>${hoverBar.close.toFixed(2)}</strong></span>
            <span>Vol: <strong>{(hoverBar.volume / 1e6).toFixed(1)}M</strong></span>
          </div>
        ) : (
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Hover over chart for OHLCV details | SMA(20): Amber
          </div>
        )}
      </div>

      <canvas
        ref={canvasRef}
        id="financial-price-canvas"
        style={{
          width: '100%',
          height: `${height}px`,
          display: 'block',
          cursor: 'crosshair',
          borderRadius: 'var(--radius-md)'
        }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />
    </div>
  );
};
