import React, { useState, useRef } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 20, marginBottom: 16, ...style });
const inputStyle = { width: '100%', padding: '10px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none', marginTop: 6 };
const labelStyle = { fontSize: 12, color: 'rgba(255,255,255,0.5)' };

const FIELDS: [string, string, string][] = [
  ['full_name',  'Full Name',  'Venkatasaikumar Erla'],
  ['email',      'Email',      'venkatasaikumarerla@email.com'],
  ['phone',      'Phone',      '+1-203-627-5831'],
  ['location',   'Location',   'West Haven, CT'],
];

export default function Settings() {
  const [budget, setBudget]   = useState(5);
  const [autoApply, setAuto]  = useState(false);
  const [saved, setSaved]     = useState(false);
  const fieldRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const handleSave = async () => {
    const payload: Record<string, any> = { max_applications_per_day: budget, auto_apply: autoApply };
    FIELDS.forEach(([key]) => {
      const el = fieldRefs.current[key];
      if (el) payload[key] = el.value;
    });
    try {
      await axios.post(`${API}/api/settings`, payload);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {
      // silently ignore - backend may be offline
    }
  };

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Settings</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>Configure your job agent preferences</div>

      {/* Profile */}
      <div style={card()}>
        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>Profile</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          {FIELDS.map(([key, label, defaultVal]) => (
            <div key={key}>
              <div style={labelStyle}>{label}</div>
              <input
                ref={el => { fieldRefs.current[key] = el; }}
                defaultValue={defaultVal}
                style={inputStyle}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Agent Settings */}
      <div style={card()}>
        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>Agent Settings</div>
        <div style={{ marginBottom: 16 }}>
          <div style={{ ...labelStyle, marginBottom: 8 }}>Max applications per day: <span style={{ color: '#60A5FA', fontWeight: 600 }}>{budget}</span></div>
          <input type="range" min={1} max={20} value={budget} onChange={e => setBudget(+e.target.value)}
            style={{ width: '100%', accentColor: '#2563EB' }} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Auto-apply without review</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginTop: 2 }}>Not recommended — always review first</div>
          </div>
          <div onClick={() => setAuto(!autoApply)}
            style={{ width: 44, height: 24, borderRadius: 12, background: autoApply ? '#2563EB' : 'rgba(255,255,255,0.1)', cursor: 'pointer', position: 'relative', transition: 'background 0.2s' }}>
            <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#fff', position: 'absolute', top: 3, left: autoApply ? 23 : 3, transition: 'left 0.2s' }} />
          </div>
        </div>
      </div>

      {/* Save */}
      {saved && (
        <div style={{ padding: '10px 16px', borderRadius: 10, background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.3)', color: '#6EE7B7', fontSize: 13, marginBottom: 12 }}>
          Settings saved successfully.
        </div>
      )}
      <button
        onClick={handleSave}
        style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 12, color: '#fff', fontSize: 15, fontWeight: 600, cursor: 'pointer', boxShadow: '0 0 20px rgba(37,99,235,0.3)' }}>
        Save Settings
      </button>
    </div>
  );
}
