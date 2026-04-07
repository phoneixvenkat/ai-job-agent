import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';

const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

export default function Dashboard() {
  const [stats, setStats]   = useState<any>({ total: 0, applied: 0, interview: 0, offer: 0, avg_fit: 0 });
  const [jobs, setJobs]     = useState<any[]>([]);
  const [counts, setCounts] = useState({ applied: 0, response: 0, interview: 0, goal: 0 });

  useEffect(() => {
    axios.get(`${API}/api/stats`).then(r => setStats(r.data)).catch(() => {});
    axios.get(`${API}/api/jobs`).then(r => setJobs(r.data.jobs || [])).catch(() => {});
  }, []);

  useEffect(() => {
    const target = { applied: stats.applied || 136, response: 12, interview: stats.interview || 3, goal: 68 };
    let frame = 0;
    const timer = setInterval(() => {
      frame += 3;
      setCounts({ applied: Math.min(frame * target.applied / 50, target.applied), response: Math.min(frame * target.response / 50, target.response), interview: Math.min(frame * target.interview / 50, target.interview), goal: Math.min(frame * target.goal / 50, target.goal) });
      if (frame >= 50) clearInterval(timer);
    }, 20);
    return () => clearInterval(timer);
  }, [stats]);

  const urgentJobs = [
    { title: 'Data Scientist', org: 'Natera', salary: '$95-120k', tag: 'Today 🔥', tagColor: '#FB7185', tagBg: 'rgba(244,63,94,0.15)' },
    { title: 'ML Engineer', org: 'Truveta', salary: '$85-110k', tag: '3 days', tagColor: '#FCD34D', tagBg: 'rgba(245,158,11,0.15)' },
    { title: 'AI Engineer', org: 'Oscar Health', salary: '$90-115k', tag: '6 days', tagColor: '#6EE7B7', tagBg: 'rgba(16,185,129,0.15)' },
  ];

  const fitData = [
    { label: 'Data Scientist', pct: 87, color: '#10B981' },
    { label: 'ML Engineer',    pct: 79, color: '#2563EB' },
    { label: 'AI Engineer',    pct: 72, color: '#2563EB' },
    { label: 'Data Analyst',   pct: 61, color: '#F59E0B' },
  ];

  const metrics = [
    { label: 'Total Applied',  value: Math.round(counts.applied), accent: '#2563EB' },
    { label: 'Response Rate',  value: `${Math.round(counts.response)}%`, accent: '#06B6D4' },
    { label: 'Interviews',     value: Math.round(counts.interview), accent: '#10B981' },
    { label: 'Goal Progress',  value: `${Math.round(counts.goal)}%`, accent: '#F59E0B' },
  ];

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 22, fontWeight: 600 }}>Good morning, Sai 👋</div>
        <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginTop: 4 }}>Your agents found <span style={{ color: '#60A5FA', fontWeight: 500 }}>23 new jobs</span> overnight</div>
      </div>

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginBottom: 20 }}>
        {metrics.map(m => (
          <div key={m.label} style={{ ...card(), position: 'relative', overflow: 'hidden', transition: 'all 0.3s', cursor: 'default' }}
            onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-2px)')}
            onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: m.accent }} />
            <div style={{ position: 'absolute', top: -20, right: -20, width: 80, height: 80, borderRadius: '50%', background: m.accent, opacity: 0.06, filter: 'blur(20px)' }} />
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>{m.label}</div>
            <div style={{ fontSize: 28, fontWeight: 600 }}>{m.value}</div>
          </div>
        ))}
      </div>

      {/* Goal bar */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: 13 }}>
          <span style={{ color: 'rgba(255,255,255,0.7)', fontWeight: 500 }}>🎯 Goal: 200 applications by May 2026</span>
          <span style={{ color: 'rgba(255,255,255,0.4)' }}>136 / 200</span>
        </div>
        <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${counts.goal}%`, background: 'linear-gradient(90deg,#2563EB,#06B6D4)', borderRadius: 3, boxShadow: '0 0 10px rgba(6,182,212,0.4)', transition: 'width 1.5s cubic-bezier(0.4,0,0.2,1)' }} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        {/* Urgent */}
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>🔥 Closing Soon</div>
          {urgentJobs.map(j => (
            <div key={j.org} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.05)', marginBottom: 8, cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.transform = 'translateX(3px)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.transform = 'translateX(0)'; }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{j.title}</div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>{j.org} · {j.salary}</div>
              </div>
              <span style={{ fontSize: 10, fontWeight: 600, padding: '3px 8px', borderRadius: 8, color: j.tagColor, background: j.tagBg }}>{j.tag}</span>
            </div>
          ))}
        </div>

        {/* Fit scores */}
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>🎯 Top Fit Scores</div>
          {fitData.map(f => (
            <div key={f.label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', width: 95 }}>{f.label}</div>
              <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${f.pct}%`, background: `linear-gradient(90deg,${f.color},${f.color}aa)`, borderRadius: 3, transition: 'width 1.2s cubic-bezier(0.4,0,0.2,1)' }} />
              </div>
              <div style={{ fontSize: 12, fontWeight: 500, width: 32, textAlign: 'right' }}>{f.pct}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Activity + Skills + Insights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>⚡ Live Activity</div>
          {[['10:44','Excel report updated'],['10:41','Follow-up set Apr 13'],['10:35','Resume ready Natera'],['10:33','ML Engineer 87% fit'],['10:32','Scout found 5 jobs']].map(([t,txt]) => (
            <div key={t} style={{ display: 'flex', gap: 10, padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', boxShadow: '0 0 6px #2563EB', marginTop: 5, flexShrink: 0 }} />
              <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)', width: 40, paddingTop: 1 }}>{t}</div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>{txt}</div>
            </div>
          ))}
        </div>

        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>📚 Skill Gaps</div>
          {[['MLflow','82%','Missing','rgba(244,63,94,0.12)','#FB7185'],['Docker','78%','Missing','rgba(244,63,94,0.12)','#FB7185'],['PySpark','71%','Learning','rgba(245,158,11,0.12)','#FCD34D'],['dbt','45%','Learning','rgba(245,158,11,0.12)','#FCD34D'],['FastAPI','38%','Have it','rgba(16,185,129,0.12)','#6EE7B7']].map(([skill,freq,tag,bg,color]) => (
            <div key={skill} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
              <div>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.75)' }}>{skill}</div>
                <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>{freq} of jobs</div>
              </div>
              <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: bg, color, fontWeight: 500 }}>{tag}</span>
            </div>
          ))}
        </div>

        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>🏆 Your Insights</div>
          {[['Best day','Wednesday 10am'],['Best role','Data Analyst 18%'],['Platform','Greenhouse'],['Avg fit','74% all apps'],['Follow-ups','3 due this week']].map(([label,value]) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12 }}>
              <span style={{ color: 'rgba(255,255,255,0.35)' }}>{label}</span>
              <span style={{ color: 'rgba(255,255,255,0.75)', fontWeight: 500 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}