import React, { useState } from 'react';
import axios from 'axios';
import { Search, MapPin, ExternalLink, Zap } from 'lucide-react';

const API = 'http://127.0.0.1:8000';

export default function JobSearch() {
  const [role, setRole]         = useState('AI Engineer');
  const [location, setLocation] = useState('Remote');
  const [jobs, setJobs]         = useState<any[]>([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [tailoring, setTailoring] = useState<number | null>(null);
  const [tailored, setTailored]   = useState<any>(null);

  const searchJobs = async () => {
    setLoading(true);
    setError('');
    setJobs([]);
    try {
      const res = await axios.post(`${API}/api/jobs/search`, { role, location, limit: 20 });
      setJobs(res.data.jobs || []);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Search failed. Make sure your resume is uploaded first.');
    }
    setLoading(false);
  };

  const tailorResume = async (jobId: number) => {
    setTailoring(jobId);
    setTailored(null);
    try {
      const res = await axios.post(`${API}/api/resume/tailor`, { job_id: jobId });
      setTailored(res.data);
    } catch {
      setError('Tailoring failed. Make sure Ollama is running.');
    }
    setTailoring(null);
  };

  const applyJob = async (jobId: number) => {
    try {
      await axios.post(`${API}/api/jobs/${jobId}/apply`);
      setJobs(jobs.map(j => j.id === jobId ? { ...j, status: 'applied' } : j));
    } catch {
      setError('Apply failed.');
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-2">Job Search</h1>
      <p className="text-gray-400 mb-8">Search jobs and get AI fit scores based on your resume.</p>

      {/* Search Bar */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-3.5 text-gray-400" />
            <input value={role} onChange={e => setRole(e.target.value)}
              placeholder="Job title (e.g. AI Engineer)"
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500" />
          </div>
          <div className="flex-1 relative">
            <MapPin size={18} className="absolute left-3 top-3.5 text-gray-400" />
            <input value={location} onChange={e => setLocation(e.target.value)}
              placeholder="Location (e.g. Remote)"
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500" />
          </div>
          <button onClick={searchJobs} disabled={loading}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50">
            {loading ? '⏳ Searching...' : '🔍 Search'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && <div className="mb-4 p-4 bg-red-900 border border-red-700 rounded-xl text-red-400 text-sm">{error}</div>}

      {/* Results */}
      {jobs.length > 0 && (
        <div className="mb-4 text-gray-400 text-sm">Found <span className="text-white font-semibold">{jobs.length}</span> jobs</div>
      )}

      <div className="space-y-4">
        {jobs.map(job => (
          <div key={job.id} className="bg-gray-900 border border-gray-800 hover:border-blue-700 rounded-xl p-6 transition-all">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-white font-semibold text-lg">{job.title}</h3>
                <p className="text-gray-400">{job.company} · {job.location}</p>
                <p className="text-gray-500 text-xs mt-1">via {job.source}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-4 py-1.5 rounded-full text-sm font-bold
                  ${job.fit_score >= 70 ? 'bg-green-900 text-green-400 border border-green-700' :
                    job.fit_score >= 40 ? 'bg-orange-900 text-orange-400 border border-orange-700' :
                    'bg-red-900 text-red-400 border border-red-700'}`}>
                  {job.fit_score}% fit
                </span>
              </div>
            </div>

            <p className="text-gray-400 text-sm mb-4 line-clamp-2">{job.description}</p>

            {/* Keywords */}
            {job.keywords?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {job.keywords.slice(0, 8).map((kw: string) => (
                  <span key={kw} className="px-2 py-0.5 bg-blue-900/50 text-blue-300 text-xs rounded-md border border-blue-800">
                    {kw}
                  </span>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <a href={job.url} target="_blank" rel="noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-sm rounded-lg transition-all">
                <ExternalLink size={14} /> View Job
              </a>
              <button onClick={() => tailorResume(job.id)} disabled={tailoring === job.id}
                className="flex items-center gap-2 px-4 py-2 bg-purple-900 hover:bg-purple-800 text-purple-300 text-sm rounded-lg transition-all disabled:opacity-50">
                <Zap size={14} /> {tailoring === job.id ? 'Tailoring...' : 'Tailor Resume'}
              </button>
              {job.status !== 'applied' ? (
                <button onClick={() => applyJob(job.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-all">
                  ✅ Mark Applied
                </button>
              ) : (
                <span className="px-4 py-2 bg-green-900 text-green-400 text-sm rounded-lg">Applied</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Tailored Resume Modal */}
      {tailored && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-8 max-w-3xl w-full max-h-[80vh] overflow-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">✍️ AI Tailored Resume</h2>
              <button onClick={() => setTailored(null)} className="text-gray-400 hover:text-white text-2xl">×</button>
            </div>
            <p className="text-blue-400 text-sm mb-4">{tailored.job_title} at {tailored.company}</p>
            <div className="mb-6">
              <h3 className="text-white font-semibold mb-2">Tailored Resume</h3>
              <pre className="bg-gray-800 p-4 rounded-lg text-gray-300 text-sm whitespace-pre-wrap">{tailored.tailored_resume}</pre>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Cover Letter</h3>
              <pre className="bg-gray-800 p-4 rounded-lg text-gray-300 text-sm whitespace-pre-wrap">{tailored.cover_letter}</pre>
            </div>
            <button onClick={() => setTailored(null)}
              className="mt-6 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}