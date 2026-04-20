import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';
const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

export default function Dashboard() {
  const [stats, setStats]     = useState<any>({ total: 0, applied: 0, interview: 0, offer: 0, avg_fit: 0 });
  const [counts, setCounts]   = useState({ applied: 0, response: 0, interview: 0, goal: 0 });
  const [loading, setLoading] = useState(true);
  const [recs, setRecs]       = useState<any>({ insights: [] });

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStats = async () => {
    try {
      const r    = await axios.get(`${API}/api/stats`);
      const data = r.data.data || {};
      setStats(data);
      setRecs(data.recommendations || { insights: [] });
      animateCounters(data);
    } catch (e) {
      animateCounters({ applied: 0, interview: 0, avg_fit: 0 });
    }
    setLoading(false);
  };

  const animateCounters = (data: any) => {
    const target = {
      applied:   data.applied   || 0,
      response:  data.applied > 0 ? Math.round((data.interview || 0) / data.applied * 100) : 0,
      interview: data.interview || 0,
      goal:      Math.min(Math.round(((data.applied || 0) / 200) * 100), 100)
    };
    let frame = 0;
    const timer = setInterval(() => {
      frame += 2;
      const progress = Math.min(frame / 50, 1);
      setCounts({
        applied:   Math.round(target.applied   * progress),
        response:  Math.round(target.response  * progress),
        interview: Math.round(target.interview * progress),
        goal:      Math.round(target.goal      * progress),
      });
      if (frame >= 50) clearInterval(timer);
    }, 20);
  };

  const urgentJobs = [
    { title: 'Data Scientist',  org: 'Natera',       salary: '$95-120k',  tag: 'Today 🔥', tagColor: '#FB7185', tagBg: 'rgba(244,63,94,0.15)'  },
    { title: 'ML Engineer',     org: 'Truveta',      salary: '$85-110k',  tag: '3 days',   tagColor: '#FCD34D', tagBg: 'rgba(245,158,11,0.15)' },
    { title: 'AI Engineer',     org: 'Mistral',      salary: '$110-150k', tag: '5 days',   tagColor: '#6EE7B7', tagBg: 'rgba(16,185,129,0.15)' },
    { title: 'Research Sci.',   org: 'Komodo Health', salary: '$90-120k', tag: '7 days',   tagColor: '#6EE7B7', tagBg: 'rgba(16,185,129,0.15)' },
  ];

  const fitData = [
    { label: 'Data Scientist', pct: 87, color: '#10B981' },
    { label: 'ML Engineer',    pct: 79, color: '#2563EB' },
    { label: 'AI Engineer',    pct: 72, color: '#2563EB' },
    { label: 'Data Analyst',   pct: 61, color: '#F59E0B' },
    { label: 'NLP Engineer',   pct: 58, color: '#F59E0B' },
  ];

  const metrics = [
    { label: 'Total Applied',  value: counts.applied,   suffix: '',  accent: '#2563EB' },
    { label: 'Response Rate',  value: counts.response,  suffix: '%', accent: '#06B6D4' },
    { label: 'Interviews',     value: counts.interview, suffix: '',  accent: '#10B981' },
    { label: 'Goal Progress',  value: counts.goal,      suffix: '%', accent: '#F59E0B' },
  ];

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 600 }}>Good morning, Sai 👋</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginTop: 4 }}>
            {loading ? 'Loading your stats...' : `${stats.total || 0} total applications tracked`}
          </div>
        </div>
        <button onClick={fetchStats} style={{ padding: '8px 16px', background: 'rgba(37,99,235,0.2)', border: '1px solid rgba(37,99,235,0.3)', borderRadius: 10, color: '#60A5FA', fontSize: 12, cursor: 'pointer' }}>
          🔄 Refresh
        </button>
      </div>

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginBottom: 20 }}>
        {metrics.map(m => (
          <div key={m.label} style={{ ...card(), position: 'relative', overflow: 'hidden', transition: 'all 0.3s' }}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: m.accent }} />
            <div style={{ position: 'absolute', top: -20, right: -20, width: 80, height: 80, borderRadius: '50%', background: m.accent, opacity: 0.06, filter: 'blur(20px)' }} />
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>{m.label}</div>
            <div style={{ fontSize: 28, fontWeight: 600 }}>{m.value}{m.suffix}</div>
          </div>
        ))}
      </div>

      {/* Goal bar */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: 13 }}>
          <span style={{ color: 'rgba(255,255,255,0.7)', fontWeight: 500 }}>🎯 Goal: 200 applications by May 2026</span>
          <span style={{ color: 'rgba(255,255,255,0.4)' }}>{stats.applied || 0} / 200</span>
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

        {/* Fit Scores */}
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>🎯 Top Fit Scores</div>
          {fitData.map(f => (
            <div key={f.label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', width: 110 }}>{f.label}</div>
              <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${f.pct}%`, background: `linear-gradient(90deg,${f.color},${f.color}aa)`, borderRadius: 3, transition: 'width 1.2s ease' }} />
              </div>
              <div style={{ fontSize: 12, fontWeight: 500, width: 32, textAlign: 'right' }}>{f.pct}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom 3 cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        {/* Activity */}
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>⚡ Live Activity</div>
          {[
            ['Scout found 258 jobs across 5 platforms', '#2563EB'],
            ['Analyst scored all jobs with TF-IDF', '#06B6D4'],
            ['Duplicate agents removed 66 dupes', '#10B981'],
            ['MySQL database initialized', '#F59E0B'],
            ['Architecture PDF generated', '#10B981'],
          ].map(([txt, color], i) => (
            <div key={i} style={{ display: 'flex', gap: 10, padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: color as string, boxShadow: `0 0 6px ${color}`, marginTop: 5, flexShrink: 0 }} />
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>{txt as string}</div>
            </div>
          ))}
        </div>

        {/* Skill Gaps */}
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>📚 Skill Gaps</div>
          {[
            ['MLflow',  '82%', 'Missing', 'rgba(244,63,94,0.12)',  '#FB7185'],
            ['Docker',  '78%', 'Missing', 'rgba(244,63,94,0.12)',  '#FB7185'],
            ['PySpark', '71%', 'Learning','rgba(245,158,11,0.12)', '#FCD34D'],
            ['dbt',     '45%', 'Learning','rgba(245,158,11,0.12)', '#FCD34D'],
            ['FastAPI', '38%', 'Have it', 'rgba(16,185,129,0.12)', '#6EE7B7'],
          ].map(([skill, freq, tag, bg, color]) => (
            <div key={skill as string} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
              <div>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.75)' }}>{skill as string}</div>
                <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>{freq as string} of jobs</div>
              </div>
              <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: bg as string, color: color as string, fontWeight: 500 }}>{tag as string}</span>
            </div>
          ))}
        </div>

        {/* Insights */}
        <div style={card()}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>🏆 Insights</div>
          {[
            ['Total jobs found', '258'],
            ['Platforms active', '4'],
            ['Avg fit score',    `${stats.avg_fit || 0}%`],
            ['Applications',    `${stats.applied || 0}`],
            ['Interviews',      `${stats.interview || 0}`],
          ].map(([label, value]) => (
            <div key={label as string} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12 }}>
              <span style={{ color: 'rgba(255,255,255,0.35)' }}>{label as string}</span>
              <span style={{ color: 'rgba(255,255,255,0.75)', fontWeight: 500 }}>{value as string}</span>
            </div>
          ))}
          {recs.insights?.length > 0 && (
            <div style={{ marginTop: 8, padding: '8px', background: 'rgba(37,99,235,0.1)', borderRadius: 8, fontSize: 11, color: '#93C5FD' }}>
              💡 {recs.insights[0]}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
