import React, { useState } from 'react';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';
const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

export default function JobHunt() {
  const [role, setRole]       = useState('Data Scientist');
  const [location, setLoc]   = useState('Remote');
  const [jobs, setJobs]       = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<number[]>([]);
  const [error, setError]     = useState('');

  const search = async () => {
    setLoading(true); setError(''); setJobs([]);
    try {
      const r = await axios.post(`${API}/api/jobs/search`, { role, location, limit: 20 });
      setJobs(r.data.jobs || []);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Upload your resume first!');
    }
    setLoading(false);
  };

  const toggle = (id: number) => setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  const fitColor = (s: number) => s >= 70 ? '#10B981' : s >= 40 ? '#F59E0B' : '#F43F5E';
  const fitBg    = (s: number) => s >= 70 ? 'rgba(16,185,129,0.15)' : s >= 40 ? 'rgba(245,158,11,0.15)' : 'rgba(244,63,94,0.15)';

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Job Hunt 🔍</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>Search across all platforms — AI scores every job against your resume</div>

      {/* Search */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', fontSize: 14 }}>🔍</span>
            <input value={role} onChange={e => setRole(e.target.value)}
              placeholder="Job title..."
              style={{ width: '100%', padding: '12px 12px 12px 36px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none' }} />
          </div>
          <div style={{ flex: 1, position: 'relative' }}>
            <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', fontSize: 14 }}>📍</span>
            <input value={location} onChange={e => setLoc(e.target.value)}
              placeholder="Location..."
              style={{ width: '100%', padding: '12px 12px 12px 36px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none' }} />
          </div>
          <button onClick={search} disabled={loading}
            style={{ padding: '12px 28px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', opacity: loading ? 0.6 : 1 }}>
            {loading ? '⏳ Searching...' : '🚀 Search'}
          </button>
        </div>
      </div>

      {error && <div style={{ padding: '12px 16px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 10, color: '#FB7185', fontSize: 13, marginBottom: 16 }}>{error}</div>}

      {jobs.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>Found <span style={{ color: '#fff', fontWeight: 600 }}>{jobs.length}</span> jobs · <span style={{ color: '#60A5FA' }}>{selected.length} selected</span></div>
          {selected.length > 0 && (
            <button style={{ padding: '8px 20px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
              ▶️ Process {selected.length} Jobs
            </button>
          )}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {jobs.map(job => (
          <div key={job.id} style={{ ...card(), transition: 'all 0.2s', cursor: 'pointer', borderColor: selected.includes(job.id) ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.07)' }}
            onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(37,99,235,0.4)'}
            onMouseLeave={e => e.currentTarget.style.borderColor = selected.includes(job.id) ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.07)'}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 600 }}>{job.title}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 3 }}>{job.org} · {job.location} · via {job.source}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: 13, fontWeight: 700, padding: '4px 12px', borderRadius: 20, color: fitColor(job.fit_score), background: fitBg(job.fit_score) }}>{job.fit_score}% fit</span>
              </div>
            </div>

            {job.keywords?.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                {job.keywords.slice(0,6).map((kw: string) => (
                  <span key={kw} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 6, background: 'rgba(37,99,235,0.15)', color: '#93C5FD', border: '1px solid rgba(37,99,235,0.2)' }}>{kw}</span>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: 8 }}>
              <a href={job.url} target="_blank" rel="noreferrer"
                style={{ padding: '7px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'rgba(255,255,255,0.7)', fontSize: 12, textDecoration: 'none' }}>
                🔗 View Job
              </a>
              <button onClick={() => toggle(job.id)}
                style={{ padding: '7px 14px', background: selected.includes(job.id) ? 'rgba(37,99,235,0.3)' : 'rgba(255,255,255,0.04)', border: `1px solid ${selected.includes(job.id) ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.1)'}`, borderRadius: 8, color: selected.includes(job.id) ? '#60A5FA' : 'rgba(255,255,255,0.5)', fontSize: 12, cursor: 'pointer' }}>
                {selected.includes(job.id) ? '✅ Selected' : '+ Select'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}