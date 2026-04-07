import React, { useState } from 'react';

const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

export default function Review() {
  const [step, setStep] = useState(0);
  const jobs = [
    { title: 'Data Scientist', org: 'Natera', fit: 87, salary: '$95-120k', resume: 'resume_natera.docx', cover: 'cover_natera.docx' },
    { title: 'ML Engineer', org: 'Truveta', fit: 79, salary: '$85-110k', resume: 'resume_truveta.docx', cover: 'cover_truveta.docx' },
  ];
  const job = jobs[step] || jobs[0];

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Review & Apply 📄</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>Preview your tailored resume and cover letter before submitting</div>

      {/* Progress */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {jobs.map((j, i) => (
          <div key={i} onClick={() => setStep(i)}
            style={{ padding: '8px 16px', borderRadius: 10, cursor: 'pointer', fontSize: 13, background: i === step ? 'rgba(37,99,235,0.25)' : 'rgba(255,255,255,0.04)', border: `1px solid ${i === step ? 'rgba(37,99,235,0.4)' : 'rgba(255,255,255,0.07)'}`, color: i === step ? '#60A5FA' : 'rgba(255,255,255,0.45)' }}>
            {j.org}
          </div>
        ))}
      </div>

      {/* Job header */}
      <div style={{ ...card(), marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>{job.title}</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginTop: 4 }}>{job.org} · {job.salary}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#10B981' }}>{job.fit}%</div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>Fit Score</div>
        </div>
      </div>

      {/* Quality Score */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Application Quality Score</div>
        {[['Resume Match', job.fit, '#10B981'], ['Cover Letter', 92, '#2563EB'], ['ATS Score', 78, '#F59E0B']].map(([label, pct, color]) => (
          <div key={label as string} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', width: 120 }}>{label as string}</div>
            <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${pct}%`, background: color as string, borderRadius: 3, transition: 'width 1s ease' }} />
            </div>
            <div style={{ fontSize: 13, fontWeight: 500, width: 36, textAlign: 'right' }}>{pct}%</div>
          </div>
        ))}
      </div>

      {/* Preview panels */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div style={card()}>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 12 }}>📄 RESUME PREVIEW</div>
          <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: 16, fontSize: 12, color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, minHeight: 200 }}>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8, color: '#fff' }}>VENKATASAIKUMAR ERLA</div>
            <div style={{ color: 'rgba(255,255,255,0.4)', marginBottom: 12, fontSize: 11 }}>West Haven, CT | venkatasaikumarerla@email.com</div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>SUMMARY</div>
            <div style={{ color: 'rgba(255,255,255,0.55)', marginBottom: 12 }}>Results-driven Data Scientist with expertise in ML pipelines, NLP, and clinical data analysis. Proven track record...</div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>SKILLS</div>
            <div style={{ color: 'rgba(255,255,255,0.55)' }}>Python · TensorFlow · NLP · AWS · SQL · Scikit-learn</div>
          </div>
          <button style={{ marginTop: 12, width: '100%', padding: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'rgba(255,255,255,0.6)', fontSize: 12, cursor: 'pointer' }}>⬇️ Download Resume</button>
        </div>

        <div style={card()}>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 12 }}>📝 COVER LETTER PREVIEW</div>
          <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: 16, fontSize: 12, color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, minHeight: 200 }}>
            <div style={{ marginBottom: 8 }}>Dear Hiring Team at <span style={{ color: '#60A5FA' }}>{job.org}</span>,</div>
            <div style={{ marginBottom: 8 }}>I am excited to apply for the <span style={{ color: '#60A5FA' }}>{job.title}</span> position. My experience in machine learning and data science directly aligns with your requirements...</div>
            <div style={{ marginBottom: 8 }}>My background in NLP and Python-based ML pipelines positions me well to contribute to your team from day one...</div>
            <div>Thank you for your consideration. I look forward to discussing how I can contribute.<br /><br />Best regards,<br />Venkatasaikumar Erla</div>
          </div>
          <button style={{ marginTop: 12, width: '100%', padding: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'rgba(255,255,255,0.6)', fontSize: 12, cursor: 'pointer' }}>⬇️ Download Cover Letter</button>
        </div>
      </div>

      {/* Decision */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <button style={{ padding: '16px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 12, color: '#FB7185', fontSize: 15, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(244,63,94,0.2)'}
          onMouseLeave={e => e.currentTarget.style.background = 'rgba(244,63,94,0.1)'}>
          ❌ Skip This Job
        </button>
        <button style={{ padding: '16px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 12, color: '#fff', fontSize: 15, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 0 20px rgba(37,99,235,0.3)' }}
          onMouseEnter={e => e.currentTarget.style.boxShadow = '0 0 30px rgba(37,99,235,0.5)'}
          onMouseLeave={e => e.currentTarget.style.boxShadow = '0 0 20px rgba(37,99,235,0.3)'}>
          ✅ Submit Application
        </button>
      </div>
    </div>
  );
}