import React, { useState } from 'react';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';
const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

export default function JobHunt() {
  const [role, setRole]         = useState('Data Scientist');
  const [location, setLoc]      = useState('Remote');
  const [jobs, setJobs]         = useState<any[]>([]);
  const [loading, setLoading]   = useState(false);
  const [selected, setSelected] = useState<number[]>([]);
  const [error, setError]       = useState('');
  const [useLLM, setUseLLM]     = useState(false);

  const search = async () => {
    setLoading(true);
    setError('');
    setJobs([]);
    setSelected([]);
    try {
      const r = await axios.post(`${API}/api/jobs/search`, {
        roles: [role], location, limit: 20, use_llm: useLLM
      });
      setJobs(r.data.jobs || []);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Upload your resume first!');
    }
    setLoading(false);
  };

  const toggle = (idx: number) => {
    setSelected(s => s.includes(idx) ? s.filter(x => x !== idx) : [...s, idx]);
  };

  const processJobs = () => {
    const selectedJobs = jobs.filter((_, idx) => selected.includes(idx));
    localStorage.setItem('selected_jobs', JSON.stringify(selectedJobs));
    window.location.href = '/review';
  };

  const fitColor = (s: number) => s >= 70 ? '#10B981' : s >= 40 ? '#F59E0B' : '#F43F5E';
  const fitBg    = (s: number) => s >= 70 ? 'rgba(16,185,129,0.15)' : s >= 40 ? 'rgba(245,158,11,0.15)' : 'rgba(244,63,94,0.15)';

  const recColor: any = {
    APPLY:    { color: '#6EE7B7', bg: 'rgba(16,185,129,0.15)' },
    CONSIDER: { color: '#FCD34D', bg: 'rgba(245,158,11,0.15)' },
    SKIP:     { color: '#FB7185', bg: 'rgba(244,63,94,0.15)'  },
  };

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Job Hunt 🔍</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>
        Search across all platforms — AI scores every job against your resume
      </div>

      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }}>🔍</span>
            <input
              value={role}
              onChange={e => setRole(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') search(); }}
              placeholder="Job title e.g. Data Scientist"
              style={{ width: '100%', padding: '12px 12px 12px 36px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none', boxSizing: 'border-box' }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative' }}>
            <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }}>📍</span>
            <input
              value={location}
              onChange={e => setLoc(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') search(); }}
              placeholder="Location e.g. Remote"
              style={{ width: '100%', padding: '12px 12px 12px 36px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none', boxSizing: 'border-box' }}
            />
          </div>
          <button
            onClick={search}
            disabled={loading}
            style={{ padding: '12px 28px', background: loading ? 'rgba(37,99,235,0.4)' : 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', whiteSpace: 'nowrap' }}
          >
            {loading ? '⏳ Searching...' : '🚀 Search'}
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            onClick={() => setUseLLM(!useLLM)}
            style={{ width: 36, height: 20, borderRadius: 10, background: useLLM ? '#2563EB' : 'rgba(255,255,255,0.1)', cursor: 'pointer', position: 'relative', transition: 'background 0.2s', flexShrink: 0 }}
          >
            <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#fff', position: 'absolute', top: 3, left: useLLM ? 19 : 3, transition: 'left 0.2s' }} />
          </div>
          <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>
            Use LLM matching — smarter scoring with Groq AI
          </span>
        </div>
      </div>

      {error && (
        <div style={{ padding: '12px 16px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 10, color: '#FB7185', fontSize: 13, marginBottom: 16 }}>
          ❌ {error}
        </div>
      )}

      {jobs.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>
            Found <span style={{ color: '#fff', fontWeight: 600 }}>{jobs.length}</span> jobs
            {' · '}
            <span style={{ color: '#60A5FA' }}>{selected.length} selected</span>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {selected.length > 0 && (
              <button
                onClick={() => setSelected([])}
                style={{ padding: '8px 14px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: 'rgba(255,255,255,0.5)', fontSize: 12, cursor: 'pointer' }}
              >
                Clear
              </button>
            )}
            {selected.length > 0 && (
              <button
                onClick={processJobs}
                style={{ padding: '8px 20px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
              >
                ▶️ Process {selected.length} Jobs
              </button>
            )}
          </div>
        </div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: 40, color: 'rgba(255,255,255,0.4)' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>⏳</div>
          <div style={{ fontSize: 13 }}>Searching across all platforms...</div>
        </div>
      )}

      {!loading && jobs.length === 0 && !error && (
        <div style={{ textAlign: 'center', padding: 60, color: 'rgba(255,255,255,0.3)' }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
          <div style={{ fontSize: 15 }}>Search for jobs to get started</div>
          <div style={{ fontSize: 12, marginTop: 4 }}>Upload your resume first for best results</div>
        </div>
      )}

      {!loading && jobs.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {jobs.map((job, idx) => {
            const rec        = String(job.recommendation || 'CONSIDER');
            const recStyle   = recColor[rec] || recColor['CONSIDER'];
            const fitScore   = Number(job.fit_score || 0);
            const isSelected = selected.includes(idx);

            return (
              <div
                key={idx}
                style={{ ...card(), transition: 'all 0.2s', borderColor: isSelected ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.07)', background: isSelected ? 'rgba(37,99,235,0.05)' : 'rgba(255,255,255,0.04)' }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 15, fontWeight: 600 }}>{String(job.title || '')}</div>
                    <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 3 }}>
                      {String(job.org || '')} · {String(job.location || '')} · via {String(job.source || '')}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0, marginLeft: 12 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, padding: '3px 10px', borderRadius: 20, color: fitColor(fitScore), background: fitBg(fitScore) }}>
                      {fitScore}% fit
                    </span>
                    <span style={{ fontSize: 11, fontWeight: 600, padding: '3px 8px', borderRadius: 8, color: recStyle.color, background: recStyle.bg }}>
                      {rec}
                    </span>
                  </div>
                </div>

                {job.explanation && (
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 10, padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 8, borderLeft: `3px solid ${recStyle.color}` }}>
                    {String(job.explanation)}
                  </div>
                )}

                {job.salary && typeof job.salary === 'object' && (
                  <div style={{ fontSize: 12, color: '#6EE7B7', marginBottom: 10 }}>
                    💰 ${Number(job.salary.min || 0).toLocaleString()} — ${Number(job.salary.max || 0).toLocaleString()}
                  </div>
                )}

                {Array.isArray(job.missing_skills) && job.missing_skills.length > 0 && (
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 10 }}>
                    ⚠️ Missing: {job.missing_skills.slice(0, 3).map(String).join(', ')}
                  </div>
                )}

                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  <button
                    onClick={() => { window.open(String(job.url || '#'), '_blank'); }}
                    style={{ padding: '7px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'rgba(255,255,255,0.7)', fontSize: 12, cursor: 'pointer' }}
                  >
                    🔗 View Job
                  </button>
                  <button
                    onClick={() => toggle(idx)}
                    style={{ padding: '7px 14px', background: isSelected ? 'rgba(37,99,235,0.3)' : 'rgba(255,255,255,0.04)', border: `1px solid ${isSelected ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.1)'}`, borderRadius: 8, color: isSelected ? '#60A5FA' : 'rgba(255,255,255,0.5)', fontSize: 12, cursor: 'pointer', transition: 'all 0.2s' }}
                  >
                    {isSelected ? '✅ Selected' : '+ Select'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}