import React from 'react';

const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

const skills = [
  { name:'MLflow',      freq:82, status:'missing',  resource:'MLflow Docs (Free, 2 days)',      progress:0  },
  { name:'Docker',      freq:78, status:'missing',  resource:'Docker for DS (Udemy, $15)',       progress:0  },
  { name:'PySpark',     freq:71, status:'learning', resource:'Databricks Academy (Free)',        progress:40 },
  { name:'dbt',         freq:45, status:'learning', resource:'dbt Learn (Free, 1 week)',         progress:20 },
  { name:'Airflow',     freq:42, status:'missing',  resource:'Astronomer Academy (Free)',        progress:0  },
  { name:'FastAPI',     freq:38, status:'have',     resource:'Already have it',                 progress:100},
  { name:'Kubernetes',  freq:30, status:'missing',  resource:'K8s for DS (YouTube, Free)',       progress:0  },
  { name:'LangChain',   freq:28, status:'have',     resource:'Already have it',                 progress:100},
];

const statusMap: any = {
  missing:  { color:'#FB7185', bg:'rgba(244,63,94,0.12)',  label:'Missing'  },
  learning: { color:'#FCD34D', bg:'rgba(245,158,11,0.12)', label:'Learning' },
  have:     { color:'#6EE7B7', bg:'rgba(16,185,129,0.12)', label:'Have it'  },
};

export default function SkillRoadmap() {
  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Skill Roadmap 📚</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>Weekly analysis of skills appearing in your target jobs</div>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 24 }}>
        {[['Critical Gaps',skills.filter(s=>s.status==='missing').length,'#FB7185'],['Learning',skills.filter(s=>s.status==='learning').length,'#FCD34D'],['Have It',skills.filter(s=>s.status==='have').length,'#6EE7B7']].map(([label,val,color]) => (
          <div key={label as string} style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.07)', borderRadius:12, padding:'14px 16px' }}>
            <div style={{ fontSize:11, color:'rgba(255,255,255,0.4)', marginBottom:6 }}>{label as string}</div>
            <div style={{ fontSize:24, fontWeight:600, color: color as string }}>{val as number}</div>
          </div>
        ))}
      </div>

      {/* Skill list */}
      <div style={card()}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>All Skills in Your Target Jobs</div>
        {skills.map(skill => {
          const s = statusMap[skill.status];
          return (
            <div key={skill.name} style={{ padding: '14px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ fontSize: 15, fontWeight: 600 }}>{skill.name}</div>
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 8, background: s.bg, color: s.color, fontWeight: 600 }}>{s.label}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>In {skill.freq}% of jobs</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', maxWidth: 220, textAlign: 'right' }}>📖 {skill.resource}</div>
                </div>
              </div>
              {skill.status !== 'have' && (
                <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${skill.progress}%`, background: skill.status === 'learning' ? '#FCD34D' : 'rgba(255,255,255,0.1)', borderRadius: 2, transition: 'width 1s ease' }} />
                </div>
              )}
              {skill.status === 'have' && (
                <div style={{ height: 4, background: 'rgba(16,185,129,0.3)', borderRadius: 2 }}>
                  <div style={{ height: '100%', width: '100%', background: '#10B981', borderRadius: 2 }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}