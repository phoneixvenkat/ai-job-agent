import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';

const statusStyle: any = {
  applied:   { bg: 'rgba(37,99,235,0.15)',   color: '#60A5FA'  },
  skipped:   { bg: 'rgba(107,114,128,0.15)', color: '#9CA3AF'  },
  interview: { bg: 'rgba(245,158,11,0.15)',  color: '#FCD34D'  },
  offer:     { bg: 'rgba(16,185,129,0.15)',  color: '#6EE7B7'  },
  rejected:  { bg: 'rgba(244,63,94,0.15)',   color: '#FB7185'  },
};

export default function Applications() {
  const [apps, setApps]   = useState<any[]>([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    axios.get(`${API}/api/applications`).then(r => setApps(r.data.applications || [])).catch(() => {
      setApps([
        { id:1, title:'Data Scientist', org:'Natera', source:'Greenhouse', fit_score:87, status:'applied', applied_at:'2026-04-05 10:32', followup_date:'2026-04-12' },
        { id:2, title:'ML Engineer', org:'Truveta', source:'Greenhouse', fit_score:79, status:'interview', applied_at:'2026-04-03 09:15', followup_date:'2026-04-10' },
        { id:3, title:'AI Engineer', org:'Oscar', source:'LinkedIn', fit_score:65, status:'skipped', applied_at:'2026-04-02 14:20', followup_date:'' },
      ]);
    });
  }, []);

  const filtered = filter === 'all' ? apps : apps.filter(a => a.status === filter);
  const counts   = { all: apps.length, applied: apps.filter(a=>a.status==='applied').length, interview: apps.filter(a=>a.status==='interview').length, offer: apps.filter(a=>a.status==='offer').length };

  const updateStatus = async (id: number, status: string) => {
    await axios.patch(`${API}/api/applications/${id}`, { status }).catch(() => {});
    setApps(apps.map(a => a.id === id ? { ...a, status } : a));
  };

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Applications 📋</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>Track every application — update status, follow-ups, and more</div>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 24 }}>
        {[['Total',counts.all,'#2563EB'],['Applied',counts.applied,'#10B981'],['Interview',counts.interview,'#F59E0B'],['Offers',counts.offer,'#06B6D4']].map(([label,val,color]) => (
          <div key={label as string} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 12, padding: '14px 16px' }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6 }}>{label as string}</div>
            <div style={{ fontSize: 24, fontWeight: 600, color: color as string }}>{val as number}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {['all','applied','interview','offer','rejected','skipped'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            style={{ padding: '6px 14px', borderRadius: 20, fontSize: 12, cursor: 'pointer', border: 'none', background: filter === f ? 'rgba(37,99,235,0.3)' : 'rgba(255,255,255,0.05)', color: filter === f ? '#60A5FA' : 'rgba(255,255,255,0.45)', textTransform: 'capitalize' }}>
            {f}
          </button>
        ))}
      </div>

      {/* Table */}
      <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 0.8fr 0.6fr 0.8fr 1fr 1.2fr', padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.06)', fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          <div>Job</div><div>Company</div><div>Fit</div><div>Source</div><div>Applied</div><div>Follow-up</div><div>Status</div>
        </div>
        {filtered.map((app, i) => {
          const st = statusStyle[app.status] || statusStyle.applied;
          return (
            <div key={app.id} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 0.8fr 0.6fr 0.8fr 1fr 1.2fr', padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)', alignItems: 'center', fontSize: 13 }}>
              <div style={{ fontWeight: 500 }}>{app.title}</div>
              <div style={{ color: 'rgba(255,255,255,0.55)' }}>{app.org}</div>
              <div style={{ color: app.fit_score >= 70 ? '#10B981' : '#F59E0B', fontWeight: 600 }}>{app.fit_score}%</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{app.source}</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{String(app.applied_at || '').slice(0,10)}</div>
              <div style={{ fontSize: 11, color: app.followup_date ? '#FCD34D' : 'rgba(255,255,255,0.3)' }}>{app.followup_date || '—'}</div>
              <select value={app.status} onChange={e => updateStatus(app.id, e.target.value)}
                style={{ padding: '4px 8px', borderRadius: 8, fontSize: 11, fontWeight: 600, background: st.bg, color: st.color, border: 'none', cursor: 'pointer', outline: 'none' }}>
                {['applied','interview','offer','rejected','skipped'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}