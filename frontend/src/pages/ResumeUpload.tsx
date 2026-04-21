import React, { useState, useRef } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

export default function ResumeUpload() {
  const [file, setFile]       = useState<File | null>(null);
  const [status, setStatus]   = useState<'idle'|'uploading'|'done'|'error'>('idle');
  const [message, setMessage] = useState('');
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => setFile(f);

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post(`${API}/api/resume/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage(`✅ Resume uploaded! ${res.data.length} characters extracted.`);
      setStatus('done');
    } catch (e: any) {
      setMessage(`❌ Upload failed: ${e.response?.data?.detail || e.message}`);
      setStatus('error');
    }
  };

  return (
    <div style={{ padding: 28, maxWidth: 700, margin: '0 auto', animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Upload Resume 📄</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 28 }}>
        Upload your resume once — AI will tailor it for every job automatically
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
        onClick={() => inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragging ? '#2563EB' : 'rgba(255,255,255,0.12)'}`,
          borderRadius: 16, padding: '48px 24px', textAlign: 'center', cursor: 'pointer',
          background: dragging ? 'rgba(37,99,235,0.08)' : 'rgba(255,255,255,0.02)',
          transition: 'all 0.2s', marginBottom: 20
        }}>
        <input ref={inputRef} type="file" accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
        <div style={{ fontSize: 40, marginBottom: 12 }}>📁</div>
        {file ? (
          <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#60A5FA' }}>{file.name}</div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>
              {(file.size / 1024).toFixed(1)} KB — ready to upload
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: 15, fontWeight: 500, color: 'rgba(255,255,255,0.7)' }}>
              Drop your resume here or click to browse
            </div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', marginTop: 6 }}>
              PDF, DOCX, or TXT supported
            </div>
          </div>
        )}
      </div>

      {/* Upload Button */}
      {file && status !== 'done' && (
        <button onClick={handleUpload} disabled={status === 'uploading'}
          style={{
            width: '100%', padding: '14px', marginBottom: 16,
            background: status === 'uploading' ? 'rgba(37,99,235,0.4)' : 'linear-gradient(135deg,#2563EB,#06B6D4)',
            border: 'none', borderRadius: 12, color: '#fff', fontSize: 15,
            fontWeight: 600, cursor: status === 'uploading' ? 'not-allowed' : 'pointer',
            boxShadow: '0 0 20px rgba(37,99,235,0.3)'
          }}>
          {status === 'uploading' ? '⏳ Uploading...' : '🚀 Upload Resume'}
        </button>
      )}

      {/* Status */}
      {message && (
        <div style={{
          padding: '14px 16px', borderRadius: 12, fontSize: 13, fontWeight: 500, marginBottom: 20,
          background: status === 'done' ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)',
          border: `1px solid ${status === 'done' ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}`,
          color: status === 'done' ? '#6EE7B7' : '#FB7185'
        }}>
          {message}
        </div>
      )}

      {/* Re-upload button */}
      {status === 'done' && (
        <button onClick={() => { setFile(null); setStatus('idle'); setMessage(''); }}
          style={{ width: '100%', padding: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, color: 'rgba(255,255,255,0.6)', fontSize: 13, cursor: 'pointer', marginBottom: 20 }}>
          📎 Upload Different Resume
        </button>
      )}

      {/* Tips */}
      <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 20 }}>
        <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 12, color: 'rgba(255,255,255,0.8)' }}>
          📌 Tips for best results
        </div>
        {[
          '✅ Use PDF format for best text extraction',
          '✅ Make sure your skills section is clearly listed',
          '✅ Include all your projects with technologies used',
          '✅ AI will match your skills to each job automatically',
          '✅ Upload once — works across all job searches',
        ].map(tip => (
          <div key={tip} style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', marginBottom: 6 }}>{tip}</div>
        ))}
      </div>
    </div>
  );
}