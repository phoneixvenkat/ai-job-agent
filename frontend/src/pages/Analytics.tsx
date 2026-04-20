import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const API = 'http://127.0.0.1:8000';
const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });
const COLORS = ['#2563EB', '#06B6D4', '#10B981', '#F59E0B', '#F43F5E'];
const TooltipStyle = { background: 'rgba(6,11,24,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', fontSize: 12 };

export default function Analytics() {
  const [stats, setStats]   = useState<any>({});
  const [apps, setApps]     = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/api/stats`),
      axios.get(`${API}/api/applications`)
    ]).then(([s, a]) => {
      setStats(s.data.data || {});
      setApps((a.data.data || {}).applications || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  // Build chart data from real applications
  const buildDayData = () => {
    const days: any = {};
    apps.forEach(app => {
      const date = String(app.applied_at || '').slice(0, 10);
      if (date) days[date] = (days[date] || 0) + 1;
    });
    return Object.entries(days).slice(-7).map(([day, apps]) => ({
      day: day.slice(5), apps
    }));
  };

  const buildSourceData = () => {
    const sources: any = {};
    apps.forEach(app => {
      const s = app.source || 'Unknown';
      sources[s] = (sources[s] || 0) + 1;
    });
    return Object.entries(sources).map(([name, value]) => ({ name, value }));
  };

  const buildStatusData = () => {
    const statuses: any = {};
    apps.forEach(app => {
      const s = app.status || 'unknown';
      statuses[s] = (statuses[s] || 0) + 1;
    });
    return Object.entries(statuses).map(([name, value]) => ({ name, value }));
  };

  const dayData    = buildDayData();
  const sourceData = buildSourceData();
  const statusData = buildStatusData();

  const responseRate = apps.length > 0
    ? Math.round((apps.filter(a => a.status === 'interview' || a.status === 'offer').length / apps.length) * 100)
    : 0;

  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Analytics 📊</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>
        Real data from your MySQL database
      </div>

      {/* Summary metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 20 }}>
        {[
          ['Total Apps',    stats.total     || 0, '#2563EB'],
          ['Response Rate', `${responseRate}%`,   '#06B6D4'],
          ['Interviews',    stats.interview || 0, '#10B981'],
          ['Offers',        stats.offer     || 0, '#F59E0B'],
        ].map(([label, val, color]) => (
          <div key={label as string} style={{ background: 'rgba(255,255,255,0.04)', border: `1px solid ${color}33`, borderRadius: 12, padding: '14px 16px' }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 6 }}>{label as string}</div>
            <div style={{ fontSize: 24, fontWeight: 600, color: color as string }}>{val as any}</div>
          </div>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'rgba(255,255,255,0.4)' }}>⏳ Loading analytics...</div>
      ) : apps.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16 }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
          <div style={{ fontSize: 15, color: 'rgba(255,255,255,0.5)' }}>No data yet</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.3)', marginTop: 4 }}>Apply to some jobs to see analytics!</div>
        </div>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div style={card()}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>Applications Per Day</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={dayData}>
                  <XAxis dataKey="day" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.5)' }} />
                  <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.5)' }} />
                  <Tooltip contentStyle={TooltipStyle} />
                  <Bar dataKey="apps" fill="#2563EB" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={card()}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>By Platform</div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sourceData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                    {sourceData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={TooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={card()}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>Application Status</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={statusData} layout="vertical">
                  <XAxis type="number" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.5)' }} />
                  <YAxis type="category" dataKey="name" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.5)' }} width={70} />
                  <Tooltip contentStyle={TooltipStyle} />
                  <Bar dataKey="value" fill="#06B6D4" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={card()}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>🏆 Key Insights</div>
              {[
                ['Total Applications', stats.total     || 0],
                ['Applied',           stats.applied   || 0],
                ['Interviews',        stats.interview || 0],
                ['Offers',            stats.offer     || 0],
                ['Rejected',          stats.rejected  || 0],
                ['Avg Fit Score',     `${stats.avg_fit || 0}%`],
                ['Response Rate',     `${responseRate}%`],
              ].map(([label, value]) => (
                <div key={label as string} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 13 }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>{label as string}</span>
                  <span style={{ color: 'rgba(255,255,255,0.8)', fontWeight: 500 }}>{value as any}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}