import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

export default function Review() {
  const [jobs, setJobs]             = useState<any[]>([]);
  const [step, setStep]             = useState(0);
  const [loading, setLoading]       = useState(false);
  const [status, setStatus]         = useState('');
  const [tailored, setTailored]     = useState<any>(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('selected_jobs');
    if (stored) {
      setJobs(JSON.parse(stored));
    } else {
      setJobs([
        { title: 'Data Scientist', org: 'Natera', fit_score: 87, salary: { min: 95000, max: 120000 }, source: 'Greenhouse', location: 'Remote', url: '#' },
        { title: 'ML Engineer', org: 'Truveta', fit_score: 79, salary: { min: 85000, max: 110000 }, source: 'Greenhouse', location: 'Remote', url: '#' },
      ]);
    }
  }, []);

  const job = jobs[step];

  useEffect(() => {
    if (job) generateDocs();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step]);

  const generateDocs = async () => {
    if (!job) return;
    setGenerating(true);
    setTailored(null);
    try {
      const r = await axios.post(`${API}/api/resume/tailor`, { job, use_llm: true });
      setTailored(r.data);
    } catch (e) {
      setTailored({
        cover_text: `Dear Hiring Team at ${job.org},\n\nI am excited to apply for the ${job.title} position. My background in data science and machine learning makes me a strong candidate for this role.\n\nThank you for your consideration.\n\nBest regards,\nVenkatasaikumar Erla`,
        resume_path: '',
        cover_path: ''
      });
    }
    setGenerating(false);
  };

  const handleYes = async () => {
    if (!job) return;
    setLoading(true);
    try {
      await axios.post(`${API}/api/jobs/apply`, {
        job,
        resume_path: tailored?.resume_path || '',
        cover_path:  tailored?.cover_path  || '',
        status:      'applied',
        explanation: `Applied with ${job.fit_score}% fit score`
      });
      setStatus(`✅ Applied to ${job.title} at ${job.org}!`);
      setTimeout(() => { setStatus(''); setStep(s => s + 1); }, 2000);
    } catch (e) {
      setStatus('❌ Failed to log application');
    }
    setLoading(false);
  };

  const handleNo = async () => {
    if (!job) return;
    setLoading(true);
    try {
      await axios.post(`${API}/api/jobs/skip`, {
        job, reason: 'User skipped during review'
      });
      setStatus(`⏭️ Skipped ${job.title} at ${job.org}`);
      setTimeout(() => { setStatus(''); setStep(s => s + 1); }, 1500);
    } catch (e) {
      setStep(s => s + 1);
    }
    setLoading(false);
  };

  if (!job) {
    return (
      <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
        <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Review & Apply ✅</div>
        <div style={{ ...card(), textAlign: 'center', padding: 48 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🎉</div>
          <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>All Done!</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)' }}>
            You have reviewed all selected jobs. Check Applications to track your progress.
          </div>
        </div>
      </div>
    );
  }

  const coverLines = (tailored?.cover_text || `Dear Hiring Team at ${job.org},\n\nI am excited to apply for the ${job.title} position.`).split('\n');

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Review & Apply ✅</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>
        Preview your tailored documents before submitting
      </div>

      {/* Progress */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {jobs.map((j, i) => (
          <div key={i} onClick={() => setStep(i)}
            style={{
              padding: '6px 14px', borderRadius: 10, cursor: 'pointer', fontSize: 12,
              background: i === step ? 'rgba(37,99,235,0.25)' : i < step ? 'rgba(16,185,129,0.15)' : 'rgba(255,255,255,0.04)',
              border: `1px solid ${i === step ? 'rgba(37,99,235,0.4)' : i < step ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.07)'}`,
              color: i === step ? '#60A5FA' : i < step ? '#6EE7B7' : 'rgba(255,255,255,0.45)'
            }}>
            {i < step ? '✅ ' : ''}{j.org}
          </div>
        ))}
      </div>

      {/* Status */}
      {status && (
        <div style={{
          padding: '12px 16px', borderRadius: 12, marginBottom: 16, fontSize: 13, fontWeight: 500,
          background: status.includes('✅') ? 'rgba(16,185,129,0.1)' : status.includes('❌') ? 'rgba(244,63,94,0.1)' : 'rgba(245,158,11,0.1)',
          border: `1px solid ${status.includes('✅') ? 'rgba(16,185,129,0.3)' : status.includes('❌') ? 'rgba(244,63,94,0.3)' : 'rgba(245,158,11,0.3)'}`,
          color: status.includes('✅') ? '#6EE7B7' : status.includes('❌') ? '#FB7185' : '#FCD34D'
        }}>
          {status}
        </div>
      )}

      {/* Job Header */}
      <div style={{ ...card(), marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>{job.title}</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginTop: 4 }}>
            {job.org} · {job.location} · {job.source}
          </div>
          {job.salary && (
            <div style={{ fontSize: 13, color: '#6EE7B7', marginTop: 4 }}>
              💰 ${Number(job.salary.min || 0).toLocaleString()} — ${Number(job.salary.max || 0).toLocaleString()}
            </div>
          )}
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: job.fit_score >= 70 ? '#10B981' : job.fit_score >= 40 ? '#F59E0B' : '#F43F5E' }}>
            {job.fit_score}%
          </div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>Fit Score</div>
        </div>
      </div>

      {/* Quality Scores */}
      <div style={{ ...card(), marginBottom: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Application Quality</div>
        {[
          ['Resume Match', job.fit_score, '#10B981'],
          ['Cover Letter', 88, '#2563EB'],
          ['ATS Score', job.ats_score || 72, '#F59E0B']
        ].map(([label, pct, color]) => (
          <div key={label as string} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', width: 120 }}>{label as string}</div>
            <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${pct}%`, background: color as string, borderRadius: 3, transition: 'width 1s ease' }} />
            </div>
            <div style={{ fontSize: 13, fontWeight: 500, width: 36, textAlign: 'right' }}>{pct}%</div>
          </div>
        ))}
      </div>

      {/* Document Previews */}
      {generating ? (
        <div style={{ ...card(), textAlign: 'center', padding: 32, marginBottom: 20 }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>⏳</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)' }}>
            Generating tailored resume and cover letter with AI...
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>

          {/* Resume Preview */}
          <div style={card()}>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 12 }}>📄 RESUME PREVIEW</div>
            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: 16, fontSize: 12, color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, minHeight: 200 }}>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8, color: '#fff' }}>VENKATASAIKUMAR ERLA</div>
              <div style={{ color: 'rgba(255,255,255,0.4)', marginBottom: 12, fontSize: 11 }}>
                West Haven, CT | venkatasaikumarerla@gmail.com | +1-203-868-6085
              </div>
              <div style={{ fontWeight: 600, marginBottom: 4, color: '#60A5FA' }}>SUMMARY</div>
              <div style={{ marginBottom: 12 }}>
                {tailored?.summary_used || `MS Data Science candidate with 3.5 years full stack experience. Skilled in Python, ML, NLP, and LLM-based systems. Tailored for ${job.title} at ${job.org}.`}
              </div>
              <div style={{ fontWeight: 600, marginBottom: 4, color: '#60A5FA' }}>KEY SKILLS</div>
              <div>Python · TensorFlow · NLP · LangChain · AWS · SQL · Scikit-learn · FastAPI</div>
            </div>
            {tailored?.resume_path && (
              <div style={{ marginTop: 8, fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
                📁 {tailored.resume_path.split('\\').pop()}
              </div>
            )}
          </div>

          {/* Cover Letter Preview */}
          <div style={card()}>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 12 }}>📝 COVER LETTER</div>
            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: 16, fontSize: 12, color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, minHeight: 200, overflowY: 'auto', maxHeight: 250 }}>
              {coverLines.map((line: string, i: number) => (
                <div key={i} style={{ marginBottom: line === '' ? 8 : 2 }}>
                  {line || '\u00A0'}
                </div>
              ))}
            </div>
            {tailored?.cover_path && (
              <div style={{ marginTop: 8, fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
                📁 {tailored.cover_path.split('\\').pop()}
              </div>
            )}
          </div>

        </div>
      )}

      {/* Decision Buttons */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <button onClick={handleNo} disabled={loading}
          style={{ padding: '16px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 12, color: '#FB7185', fontSize: 15, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.2s' }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(244,63,94,0.2)'}
          onMouseLeave={e => e.currentTarget.style.background = 'rgba(244,63,94,0.1)'}>
          ❌ Skip This Job
        </button>
        <button onClick={handleYes} disabled={loading || generating}
          style={{ padding: '16px', background: loading ? 'rgba(37,99,235,0.4)' : 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 12, color: '#fff', fontSize: 15, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.2s', boxShadow: '0 0 20px rgba(37,99,235,0.3)' }}>
          {loading ? '⏳ Submitting...' : '✅ Submit Application'}
        </button>
      </div>

      {/* Counter */}
      <div style={{ textAlign: 'center', marginTop: 12, fontSize: 12, color: 'rgba(255,255,255,0.3)' }}>
        Job {step + 1} of {jobs.length}
      </div>
    </div>
  );
}