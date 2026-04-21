import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const statusStyle: any = {
  applied:   { bg: 'rgba(37,99,235,0.15)',   color: '#60A5FA'  },
  skipped:   { bg: 'rgba(107,114,128,0.15)', color: '#9CA3AF'  },
  interview: { bg: 'rgba(245,158,11,0.15)',  color: '#FCD34D'  },
  offer:     { bg: 'rgba(16,185,129,0.15)',  color: '#6EE7B7'  },
  rejected:  { bg: 'rgba(244,63,94,0.15)',   color: '#FB7185'  },
};

const emailBadge: Record<string, { bg: string; color: string }> = {
  interview:  { bg: 'rgba(245,158,11,0.15)',  color: '#FCD34D' },
  offer:      { bg: 'rgba(16,185,129,0.15)',  color: '#6EE7B7' },
  rejection:  { bg: 'rgba(244,63,94,0.15)',   color: '#FB7185' },
  assessment: { bg: 'rgba(139,92,246,0.15)',  color: '#C4B5FD' },
  followup:   { bg: 'rgba(37,99,235,0.15)',   color: '#60A5FA' },
  other:      { bg: 'rgba(107,114,128,0.15)', color: '#9CA3AF' },
};

export default function Applications() {
  const [apps, setApps]           = useState<any[]>([]);
  const [emails, setEmails]       = useState<any[]>([]);
  const [filter, setFilter]       = useState('all');
  const [loading, setLoading]     = useState(true);
  const [showEmails, setShowEmails] = useState(false);
  const [stats, setStats]         = useState({ total: 0, applied: 0, interview: 0, offer: 0, rejected: 0 });

  useEffect(() => { fetchApps(); fetchEmails(); }, []);

  const fetchEmails = async () => {
    try {
      const r = await axios.get(`${API}/api/email/results`);
      setEmails(r.data.data || []);
    } catch { setEmails([]); }
  };

  const fetchApps = async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/applications`);
      const data = r.data.applications || [];
      setApps(data);
      setStats({
        total:     data.length,
        applied:   data.filter((a: any) => a.status === 'applied').length,
        interview: data.filter((a: any) => a.status === 'interview').length,
        offer:     data.filter((a: any) => a.status === 'offer').length,
        rejected:  data.filter((a: any) => a.status === 'rejected').length,
      });
    } catch (e) { setApps([]); }
    setLoading(false);
  };

  const filtered = filter === 'all' ? apps : apps.filter(a => a.status === filter);

  const updateStatus = async (id: number, status: string) => {
    await axios.patch(`${API}/api/applications/${id}`, { status }).catch(() => {});
    setApps(apps.map(a => a.id === id ? { ...a, status } : a));
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleOutcome = async (app: any, outcome: string) => {
    try {
      await axios.post(`${API}/api/applications/${outcome}`, { app_id: app.id, job: app });
      fetchApps();
    } catch (e) {}
  };

  const getDaysAgo = (dateStr: string) => {
    if (!dateStr) return 0;
    const diff = new Date().getTime() - new Date(dateStr).getTime();
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  };

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 600 }}>Applications 📋</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginTop: 4 }}>Track every application in real time</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={fetchApps} style={{ padding: '8px 16px', background: 'rgba(37,99,235,0.2)', border: '1px solid rgba(37,99,235,0.3)', borderRadius: 10, color: '#60A5FA', fontSize: 12, cursor: 'pointer' }}>
            🔄 Refresh
          </button>
          <button onClick={() => window.open(`${API}/api/report/excel`, '_blank')}
            style={{ padding: '8px 16px', background: 'rgba(16,185,129,0.2)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 10, color: '#6EE7B7', fontSize: 12, cursor: 'pointer' }}>
            Download Excel
          </button>
          <button onClick={() => setShowEmails(v => !v)}
            style={{ padding: '8px 16px', background: showEmails ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.05)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: 10, color: '#FCD34D', fontSize: 12, cursor: 'pointer' }}>
            Email Intel {emails.length > 0 ? `(${emails.length})` : ''}
          </button>
        </div>
      </div>

      {/* Email Intel Panel */}
      {showEmails && (
        <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 16, padding: 20, marginBottom: 20 }}>
          <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 14, color: '#FCD34D' }}>Email Intelligence</div>
          {emails.length === 0 ? (
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', textAlign: 'center', padding: 20 }}>
              No email activity detected yet. Scan emails from Settings.
            </div>
          ) : (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.5fr 1fr 0.8fr 1.2fr', gap: 8, padding: '8px 12px', fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <div>Subject</div><div>Company / Job</div><div>Classification</div><div>Confidence</div><div>Processed</div>
              </div>
              {emails.map((e: any, i: number) => {
                const badge = emailBadge[e.classification] || emailBadge.other;
                return (
                  <div key={i} style={{ display: 'grid', gridTemplateColumns: '2fr 1.5fr 1fr 0.8fr 1.2fr', gap: 8, padding: '10px 12px', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12, alignItems: 'center' }}>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'rgba(255,255,255,0.75)' }}>{e.subject || '(no subject)'}</div>
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11 }}>{e.company || e.sender || '—'}{e.job_title ? ` · ${e.job_title}` : ''}</div>
                    <span style={{ padding: '3px 8px', borderRadius: 8, fontSize: 10, fontWeight: 600, background: badge.bg, color: badge.color, textTransform: 'capitalize', width: 'fit-content' }}>{e.classification || 'other'}</span>
                    <div style={{ color: 'rgba(255,255,255,0.45)' }}>{e.confidence ? `${Math.round(e.confidence * 100)}%` : '—'}</div>
                    <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11 }}>{e.processed_at ? String(e.processed_at).slice(0, 16) : '—'}</div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 12, marginBottom: 24 }}>
        {[['Total', stats.total, '#fff'], ['Applied', stats.applied, '#60A5FA'], ['Interview', stats.interview, '#FCD34D'], ['Offers', stats.offer, '#6EE7B7'], ['Rejected', stats.rejected, '#FB7185']].map(([label, val, color]) => (
          <div key={label as string} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 12, padding: '14px 16px' }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6 }}>{label as string}</div>
            <div style={{ fontSize: 24, fontWeight: 600, color: color as string }}>{val as number}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {['all', 'applied', 'interview', 'offer', 'rejected', 'skipped'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            style={{ padding: '6px 14px', borderRadius: 20, fontSize: 12, cursor: 'pointer', border: 'none', background: filter === f ? 'rgba(37,99,235,0.3)' : 'rgba(255,255,255,0.05)', color: filter === f ? '#60A5FA' : 'rgba(255,255,255,0.45)', textTransform: 'capitalize' }}>
            {f} {f !== 'all' ? `(${apps.filter(a => a.status === f).length})` : `(${apps.length})`}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: 40, color: 'rgba(255,255,255,0.4)' }}>
          ⏳ Loading applications...
        </div>
      )}

      {/* Empty */}
      {!loading && filtered.length === 0 && (
        <div style={{ textAlign: 'center', padding: 40, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16 }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📭</div>
          <div style={{ fontSize: 15, color: 'rgba(255,255,255,0.5)' }}>No applications yet</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.3)', marginTop: 4 }}>Go to Job Hunt and apply to some jobs!</div>
        </div>
      )}

      {/* Table */}
      {!loading && filtered.length > 0 && (
        <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, overflow: 'hidden' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.2fr 0.7fr 0.7fr 0.8fr 0.8fr 1.2fr', padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.06)', fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            <div>Job</div><div>Company</div><div>Fit</div><div>Days</div><div>Follow-up</div><div>Source</div><div>Status</div>
          </div>
          {filtered.map((app, i) => {
            const st      = statusStyle[app.status] || statusStyle.applied;
            const daysAgo = getDaysAgo(app.applied_at);
            return (
              <div key={app.id} style={{ display: 'grid', gridTemplateColumns: '2fr 1.2fr 0.7fr 0.7fr 0.8fr 0.8fr 1.2fr', padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)', alignItems: 'center', fontSize: 13 }}>
                <div style={{ fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{app.title}</div>
                <div style={{ color: 'rgba(255,255,255,0.55)', fontSize: 12 }}>{app.org}</div>
                <div style={{ color: Number(app.fit_score) >= 70 ? '#10B981' : '#F59E0B', fontWeight: 600 }}>{Number(app.fit_score || 0).toFixed(1)}%</div>
                <div style={{ fontSize: 12, color: daysAgo > 7 ? '#FCD34D' : 'rgba(255,255,255,0.4)' }}>{daysAgo}d</div>
                <div style={{ fontSize: 11, color: app.followup_date ? '#FCD34D' : 'rgba(255,255,255,0.3)' }}>
                  {app.followup_date ? String(app.followup_date).slice(0, 10) : '—'}
                </div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{app.source}</div>
                <select value={app.status} onChange={e => updateStatus(app.id, e.target.value)}
                  style={{ padding: '4px 8px', borderRadius: 8, fontSize: 11, fontWeight: 600, background: st.bg, color: st.color, border: 'none', cursor: 'pointer', outline: 'none' }}>
                  {['applied', 'interview', 'offer', 'rejected', 'skipped'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}