import React, { useState } from 'react';
import axios from 'axios';
import { Upload, CheckCircle, FileText } from 'lucide-react';

const API = 'http://127.0.0.1:8000';

export default function ResumeUpload() {
  const [file, setFile]         = useState<File | null>(null);
  const [status, setStatus]     = useState<'idle'|'uploading'|'done'|'error'>('idle');
  const [message, setMessage]   = useState('');
  const [dragging, setDragging] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post(`${API}/api/resume/upload`, formData);
      setMessage(`✅ Resume uploaded! ${res.data.text_length} characters extracted.`);
      setStatus('done');
    } catch {
      setMessage('❌ Upload failed. Please try again.');
      setStatus('error');
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-2">Upload Resume</h1>
      <p className="text-gray-400 mb-8">Upload your resume once — AI will tailor it for every job automatically.</p>

      {/* Drop Zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); setFile(e.dataTransfer.files[0]); }}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all
          ${dragging ? 'border-blue-400 bg-blue-900/20' : 'border-gray-600 hover:border-blue-500 hover:bg-gray-800/50'}`}
        onClick={() => document.getElementById('fileInput')?.click()}
      >
        <input id="fileInput" type="file" accept=".pdf,.docx,.txt"
               className="hidden" onChange={e => setFile(e.target.files?.[0] || null)} />
        <Upload size={48} className="mx-auto mb-4 text-blue-400" />
        {file ? (
          <div>
            <p className="text-white font-semibold text-lg">{file.name}</p>
            <p className="text-gray-400 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div>
            <p className="text-white font-medium">Drop your resume here or click to browse</p>
            <p className="text-gray-400 text-sm mt-2">Supports PDF, DOCX, TXT</p>
          </div>
        )}
      </div>

      {/* Upload Button */}
      {file && status !== 'done' && (
        <button onClick={handleUpload} disabled={status === 'uploading'}
          className="mt-6 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50">
          {status === 'uploading' ? '⏳ Uploading...' : '🚀 Upload Resume'}
        </button>
      )}

      {/* Status Message */}
      {message && (
        <div className={`mt-4 p-4 rounded-xl text-sm font-medium
          ${status === 'done' ? 'bg-green-900 text-green-400 border border-green-700' :
            'bg-red-900 text-red-400 border border-red-700'}`}>
          {message}
        </div>
      )}

      {/* Tips */}
      <div className="mt-8 bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
          <FileText size={18} /> Tips for best results
        </h2>
        <ul className="space-y-2 text-gray-400 text-sm">
          <li>✅ Use a PDF or DOCX format</li>
          <li>✅ Make sure your skills section is clearly written</li>
          <li>✅ Include your education and experience clearly</li>
          <li>✅ The AI will match your skills to each job automatically</li>
        </ul>
      </div>
    </div>
  );
}