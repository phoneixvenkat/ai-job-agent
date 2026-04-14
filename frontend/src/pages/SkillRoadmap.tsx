import React, { useState } from 'react';

const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

const skills = [
  { name:'MLflow',      freq:82, status:'missing',  resource:'MLflow Docs (Free, 2 days)',        progress:0,   priority:'Critical' },
  { name:'Docker',      freq:78, status:'missing',  resource:'Docker for DS — Udemy ($15)',        progress:0,   priority:'Critical' },
  { name:'PySpark',     freq:71, status:'learning', resource:'Databricks Academy (Free)',          progress:40,  priority:'Critical' },
  { name:'dbt',         freq:45, status:'learning', resource:'dbt Learn (Free, 1 week)',           progress:20,  priority:'Medium'   },
  { name:'Airflow',     freq:42, status:'missing',  resource:'Astronomer Academy (Free)',          progress:0,   priority:'Medium'   },
  { name:'Kubernetes',  freq:35, status:'missing',  resource:'K8s for DS — YouTube (Free)',        progress:0,   priority:'Medium'   },
  { name:'FastAPI',     freq:38, status:'have',     resource:'Already in your projects ✅',        progress:100, priority:'Done'     },
  { name:'LangChain',   freq:32, status:'have',     resource:'Already in your projects ✅',        progress:100, priority:'Done'     },
  { name:'PyTorch',     freq:65, status:'have',     resource:'Already in your coursework ✅',      progress:100, priority:'Done'     },
  { name:'AWS',         freq:55, status:'have',     resource:'Already in your projects ✅',        progress:100, priority:'Done'     },
  { name:'SQL',         freq:90, status:'have',     resource:'Already have it ✅',                 progress:100, priority:'Done'     },
  { name:'Scikit-learn',freq:85, status:'have',     resource:'Already have it ✅',                 progress:100, priority:'Done'     },
];

const statusMap: any = {
  missing:  { color:'#FB7185', bg:'rgba(244,63,94,0.12)',  label:'Missing'  },
  learning: { color:'#FCD34D', bg:'rgba(245,158,11,0.12)', label:'Learning' },
  have:     { color:'#6EE7B7', bg:'rgba(16,185,129,0.12)', label:'Have it'  },
};

const priorityMap: any = {
  Critical: { color:'#FB7185' },
  Medium:   { color:'#FCD34D' },
  Done:     { color:'#6EE7B7' },
};

export default function SkillRoadmap() {
  const [filter, setFilter] = useState('all');
  const [week] = useState('April 14, 2026');

  const filtered = filter === 'all' ? skills : skills.filter(s => s.status === filter);
  const critical = skills.filter(s => s.status === 'missing').length;
  const learning = skills.filter(s => s.status === 'learning').length;
  const have     = skills.filter(s => s.status === 'have').length;
  const total    = skills.length;
  const completion = Math.round((have / total) * 100);

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Skill Roadmap 📚</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>
        Week of {week} — Skills appearing in your target jobs
      </div>

      {/* Overall progress */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
          <span style={{ fontSize: 13, fontWeight: 500 }}>Overall Skill Readiness</span>
          <span style={{ fontSize: 13, color: '#6EE7B7', fontWeight: 600 }}>{completion}%</span>
        </div>
        <div style={{ height: 8, background: 'rgba(255,255,255,0.06)', borderRadius: 4, overflow: 'hidden', marginBottom: 12 }}>
          <div style={{ height: '100%', width: `${completion}%`, background: 'linear-gradient(90deg,#2563EB,#10B981)', borderRadius: 4, transition: 'width 1.5s ease' }} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
          {[['Critical Gaps', critical, '#FB7185'], ['Learning', learning, '#FCD34D'], ['Have It', have, '#6EE7B7']].map(([label, val, color]) => (
            <div key={label as string} style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 10, padding: '12px', textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: color as string }}>{val as number}</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>{label as string}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {['all', 'missing', 'learning', 'have'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            style={{ padding: '6px 14px', borderRadius: 20, fontSize: 12, cursor: 'pointer', border: 'none', background: filter === f ? 'rgba(37,99,235,0.3)' : 'rgba(255,255,255,0.05)', color: filter === f ? '#60A5FA' : 'rgba(255,255,255,0.45)', textTransform: 'capitalize' }}>
            {f} ({f === 'all' ? skills.length : skills.filter(s => s.status === f).length})
          </button>
        ))}
      </div>

      {/* Skills list */}
      <div style={card()}>
        {filtered.map((skill, i) => {
          const s = statusMap[skill.status];
          const p = priorityMap[skill.priority];
          return (
            <div key={skill.name} style={{ padding: '14px 0', borderBottom: i < filtered.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ fontSize: 15, fontWeight: 600 }}>{skill.name}</div>
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: s.bg, color: s.color, fontWeight: 600 }}>{s.label}</span>
                  <span style={{ fontSize: 10, color: p.color }}>● {skill.priority}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>In {skill.freq}% of jobs</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', maxWidth: 250, textAlign: 'right' }}>📖 {skill.resource}</div>
                </div>
              </div>
              <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${skill.progress}%`, background: skill.status === 'have' ? '#10B981' : skill.status === 'learning' ? '#FCD34D' : 'rgba(255,255,255,0.1)', borderRadius: 2, transition: 'width 1s ease' }} />
              </div>
              {skill.status !== 'have' && (
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginTop: 4 }}>{skill.progress}% complete</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Weekly tip */}
      <div style={{ ...card({ marginTop: 16 }), background: 'rgba(37,99,235,0.08)', border: '1px solid rgba(37,99,235,0.2)' }}>
        <div style={{ fontSize: 13, fontWeight: 500, color: '#60A5FA', marginBottom: 8 }}>💡 This Week's Focus</div>
        <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)' }}>
          Start with <strong style={{ color: '#fff' }}>MLflow</strong> — it appears in 82% of your target jobs and can be learned in 2 days using the free official documentation. This single skill could unlock 20+ more job matches immediately.
        </div>
      </div>
    </div>
  );
}