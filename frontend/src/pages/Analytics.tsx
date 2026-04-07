import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const card = (style = {}) => ({ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: 18, ...style });

const weekData   = [{ day:'Mon',apps:3 },{ day:'Tue',apps:8 },{ day:'Wed',apps:12 },{ day:'Thu',apps:7 },{ day:'Fri',apps:5 },{ day:'Sat',apps:2 },{ day:'Sun',apps:1 }];
const trendData  = [{ week:'W1',rate:8 },{ week:'W2',rate:10 },{ week:'W3',rate:9 },{ week:'W4',rate:14 },{ week:'W5',rate:12 }];
const sourceData = [{ name:'Greenhouse',value:45 },{ name:'LinkedIn',value:30 },{ name:'Lever',value:15 },{ name:'Remotive',value:10 }];
const COLORS     = ['#2563EB','#06B6D4','#10B981','#F59E0B'];

const TooltipStyle = { background:'rgba(6,11,24,0.9)', border:'1px solid rgba(255,255,255,0.1)', borderRadius:8, color:'#fff', fontSize:12 };

export default function Analytics() {
  return (
    <div style={{ padding: 28, animation: 'fadeUp 0.5s ease' }}>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>Analytics 📊</div>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 24 }}>Understand what's working in your job search</div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <div style={card()}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>Applications Per Day</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={weekData}>
              <XAxis dataKey="day" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={TooltipStyle} />
              <Bar dataKey="apps" fill="#2563EB" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={card()}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>Response Rate Trend</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <XAxis dataKey="week" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={TooltipStyle} />
              <Line type="monotone" dataKey="rate" stroke="#06B6D4" strokeWidth={2} dot={{ fill:'#06B6D4' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <div style={card()}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>Applications by Platform</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={sourceData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}%`} labelLine={false}>
                {sourceData.map((_,i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={TooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div style={card()}>
          <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 16 }}>🏆 Key Insights</div>
          {[
            ['Best day to apply','Wednesday 10am','#10B981'],
            ['Highest response role','Data Analyst (18%)','#2563EB'],
            ['Best platform','Greenhouse','#06B6D4'],
            ['Avg fit score','74% all apps','#F59E0B'],
            ['Total applications','136','#fff'],
            ['Response rate','12%','#10B981'],
            ['Interviews scheduled','3','#F59E0B'],
          ].map(([label,value,color]) => (
            <div key={label as string} style={{ display:'flex', justifyContent:'space-between', padding:'8px 0', borderBottom:'1px solid rgba(255,255,255,0.04)', fontSize:13 }}>
              <span style={{ color:'rgba(255,255,255,0.4)' }}>{label}</span>
              <span style={{ color: color as string, fontWeight:500 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}