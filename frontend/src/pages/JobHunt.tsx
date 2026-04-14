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
    setLoading(true); setError(''); setJobs([]);
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

  const toggle = (id: number) =>
    setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  const fitColor = (s: number) => s >= 70 ? '#10B981' : s >= 40 ? '#F59E0B' : '#F43F5E';
  const fitBg    = (s: number) => s >= 70 ? 'rgba(16,185,129,0.15)' : s >= 40 ? 'rgba(245,158,11,0.15)' : 'rgba(244,63,94,0.15)';

  const recColor: any = {
    APPLY:     { color: '#6EE7B7', bg: 'rgba(16,185,129,0.15)'  },
    CONSIDER:  { color: '#FCD34D', bg: 'rgba(245,158,11,0.15)'  },
    SKIP:      { color: '#FB7185', bg: 'rgba(244,63,94,0.15)'   },
  };

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Job Hunt 🔍</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>
        Search across all platforms — AI scores every job against your resume
      </div>

      {/* Search Bar */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }}>🔍</span>
            <input value={role} onChange={e => setRole(e.target.value)}
              placeholder="Job title e.g. Data Scientist"
              style={{ width: '100%', padding: '12px 12px 12px 36px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none', boxSizing: 'border-box' }} />
          </div>
          <div style={{ flex: 1, position: 'relative' }}>
            <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }}>📍</span>
            <input value={location} onChange={e => setLoc(e.target.value)}
              placeholder="Location e.g. Remote"
              style={{ width: '100%', padding: '12px 12px 12px 36px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 10, color: '#fff', fontSize: 13, outline: 'none', boxSizing: 'border-box' }} />
          </div>
          <button onClick={search} disabled={loading}
            style={{ padding: '12px 28px', background: loading ? 'rgba(37,99,235,0.4)' : 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', whiteSpace: 'nowrap' }}>
            {loading ? '⏳ Searching...' : '🚀 Search'}
          </button>
        </div>

        {/* LLM Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div onClick={() => setUseLLM(!useLLM)}
            style={{ width: 36, height: 20, borderRadius: 10, background: useLLM ? '#2563EB' : 'rgba(255,255,255,0.1)', cursor: 'pointer', position: 'relative', transition: 'background 0.2s', flexShrink: 0 }}>
            <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#fff', position: 'absolute', top: 3, left: useLLM ? 19 : 3, transition: 'left 0.2s' }} />
          </div>
          <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>
            Use LLM matching (slower but smarter — requires Ollama)
          </span>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '12px 16px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 10, color: '#FB7185', fontSize: 13, marginBottom: 16 }}>
          ❌ {error}
        </div>
      )}

      {/* Results header */}
      {jobs.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)' }}>
            Found <span style={{ color: '#fff', fontWeight: 600 }}>{jobs.length}</span> jobs ·{' '}
            <span style={{ color: '#60A5FA' }}>{selected.length} selected</span>
          </div>
          {selected.length > 0 && (
            <button style={{ padding: '8px 20px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
              ▶️ Process {selected.length} Jobs
            </button>
          )}
        </div>
      )}

      {/* Job Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {jobs.map((job, idx) => {
          const rec      = String(job.recommendation || 'CONSIDER');
          const recStyle = recColor[rec] || recColor['CONSIDER'];
          const fitScore = Number(job.fit_score || 0);
          const jobId    = job.id || idx;

          return (
            <div key={jobId}
              style={{ ...card(), transition: 'all 0.2s', cursor: 'pointer', borderColor: selected.includes(jobId) ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.07)' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(37,99,235,0.4)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = selected.includes(jobId) ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.07)'}>

              {/* Job Header */}
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

              {/* Score Explanation */}
              {job.explanation && (
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 10, padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 8, borderLeft: `3px solid ${recStyle.color}` }}>
                  {String(job.explanation)}
                </div>
              )}

              {/* Salary */}
              {job.salary && typeof job.salary === 'object' && (
                <div style={{ fontSize: 12, color: '#6EE7B7', marginBottom: 10 }}>
                  💰 ${Number(job.salary.min || 0).toLocaleString()} — ${Number(job.salary.max || 0).toLocaleString()}
                </div>
              )}

              {/* Keywords */}
              {Array.isArray(job.keywords) && job.keywords.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                  {job.keywords.slice(0, 6).map((kw: any, i: number) => (
                    <span key={i} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 6, background: 'rgba(37,99,235,0.15)', color: '#93C5FD', border: '1px solid rgba(37,99,235,0.2)' }}>
                      {String(kw)}
                    </span>
                  ))}
                </div>
              )}

              {/* Missing Skills */}
              {Array.isArray(job.missing_skills) && job.missing_skills.length > 0 && (
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 10 }}>
                  ⚠️ Missing: {job.missing_skills.slice(0, 3).map(String).join(', ')}
                </div>
              )}

              {/* Actions */}
              <div style={{ display: 'flex', gap: 8 }}>
                <a href={String(job.url || '#')} target="_blank" rel="noreferrer"
                  style={{ padding: '7px 14px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'rgba(255,255,255,0.7)', fontSize: 12, textDecoration: 'none' }}>
                  🔗 View Job
                </a>
                <button onClick={() => toggle(jobId)}
                  style={{ padding: '7px 14px', background: selected.includes(jobId) ? 'rgba(37,99,235,0.3)' : 'rgba(255,255,255,0.04)', border: `1px solid ${selected.includes(jobId) ? 'rgba(37,99,235,0.5)' : 'rgba(255,255,255,0.1)'}`, borderRadius: 8, color: selected.includes(jobId) ? '#60A5FA' : 'rgba(255,255,255,0.5)', fontSize: 12, cursor: 'pointer' }}>
                  {selected.includes(jobId) ? '✅ Selected' : '+ Select'}
                </button>
                {job.should_apply === false && (
                  <span style={{ padding: '7px 14px', background: 'rgba(244,63,94,0.1)', borderRadius: 8, color: '#FB7185', fontSize: 12 }}>
                    AI suggests skip
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}