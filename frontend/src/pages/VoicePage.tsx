import React, { useState } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  Activity,
  CheckCircle2,
  ShieldAlert,
  Play
} from 'lucide-react';
import { api } from '../api/client';
import { VoiceBriefingResponse } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const VoicePage: React.FC = () => {
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [briefing, setBriefing] = useState<VoiceBriefingResponse | null>(null);

  const handleGenerateBriefing = async () => {
    setGenerating(true);
    try {
      const res = await api.getVoiceBriefing(['AAPL', 'MSFT', 'NVDA']);
      setBriefing(res);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleSpeak = () => {
    if (!briefing) return;

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(briefing.audio_briefing_script);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);
      window.speechSynthesis.speak(utterance);
      setSpeaking(true);
    }
  };

  const handleSimulateVoiceInput = () => {
    setListening(true);
    setTimeout(() => {
      setListening(false);
      handleGenerateBriefing();
    }, 1800);
  };

  return (
    <div id="voice-page" className="page-wrapper">
      <DisclaimerBanner />

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Mic size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Voice AI Financial Assistant & Audio Briefings
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Conversational voice commands and synthesized executive audio briefings using the Web Speech API and streaming speech synthesis.
        </p>
      </div>

      {/* Microphone Interaction Center */}
      <div
        className="glass-card"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          marginBottom: '24px',
          textAlign: 'center'
        }}
      >
        <button
          id="voice-mic-button"
          onClick={handleSimulateVoiceInput}
          style={{
            width: '84px',
            height: '84px',
            borderRadius: '50%',
            backgroundColor: listening ? 'var(--accent-rose)' : 'var(--accent-cyan)',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: listening ? '0 0 30px rgba(244, 63, 94, 0.6)' : '0 0 25px rgba(6, 182, 212, 0.5)',
            transition: 'all 0.3s ease',
            color: '#ffffff'
          }}
          className={listening ? 'animate-pulse-glow' : ''}
        >
          {listening ? <MicOff size={36} /> : <Mic size={36} />}
        </button>

        <div style={{ marginTop: '20px', fontWeight: 700, fontSize: '16px' }}>
          {listening ? 'Listening to voice command...' : 'Tap to Speak Command'}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
          Example: <em>"Give me a short briefing on my technology watchlist."</em>
        </div>

        <div style={{ marginTop: '16px' }}>
          <button
            id="generate-briefing-btn"
            className="btn btn-secondary btn-sm"
            onClick={handleGenerateBriefing}
            disabled={generating}
          >
            <Sparkles size={14} />
            <span>{generating ? 'Synthesizing Audio Briefing...' : 'Generate Watchlist Briefing Script'}</span>
          </button>
        </div>
      </div>

      {/* Generated Audio Briefing Output */}
      {briefing && (
        <div className="glass-card" id="voice-briefing-output-container">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <span className="badge badge-emerald" style={{ marginBottom: '6px' }}>{briefing.sentiment_headline}</span>
              <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Synthesized Audio Market Briefing</h2>
            </div>

            <button
              id="voice-tts-toggle-btn"
              className={`btn ${speaking ? 'btn-secondary' : 'btn-primary'}`}
              onClick={handleToggleSpeak}
            >
              {speaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
              <span>{speaking ? 'Stop Speech Audio' : 'Play Audio Briefing'}</span>
            </button>
          </div>

          <div
            style={{
              padding: '18px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              fontSize: '13px',
              lineHeight: 1.7,
              color: 'var(--text-primary)',
              marginBottom: '16px',
              border: '1px solid var(--border-subtle)'
            }}
          >
            "{briefing.audio_briefing_script}"
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>
              EXECUTIVE BRIEFING TAKEAWAYS:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {briefing.key_takeaways.map((takeaway, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <CheckCircle2 size={14} color="var(--accent-emerald)" />
                  <span>{takeaway}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
