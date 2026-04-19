import React from 'react';
import { motion, type Variants } from 'framer-motion';

interface Agent {
  icon: string;
  title: string;
  description: string;
  tags: string[];
  iconGradient: string;
  iconGlow: string;
  borderGlow: string;
  cardGlow: string;
  tagStyle: string;
}

const agents: Agent[] = [
  {
    icon: '🔭',
    title: 'Scout Agent',
    description: 'Scans Greenhouse, Lever, LinkedIn, Remotive, and more — 24/7 — surfacing fresh opportunities the moment they post.',
    tags: ['LinkedIn', 'Greenhouse', 'Lever', 'Remotive'],
    iconGradient: 'linear-gradient(135deg, rgba(99,102,241,0.5), rgba(67,56,202,0.3))',
    iconGlow: '0 0 20px rgba(99,102,241,0.6)',
    borderGlow: 'rgba(99,102,241,0.5)',
    cardGlow: '0 20px 60px rgba(99,102,241,0.15)',
    tagStyle: 'bg-indigo-500/10 border border-indigo-500/25 text-indigo-400',
  },
  {
    icon: '🧠',
    title: 'Analyst Agent',
    description: 'TF-IDF + Llama3 scoring measures your resume against every JD, estimating fit score, ATS compatibility, and salary range.',
    tags: ['TF-IDF', 'Llama3', 'ATS Check'],
    iconGradient: 'linear-gradient(135deg, rgba(168,85,247,0.5), rgba(124,58,237,0.3))',
    iconGlow: '0 0 20px rgba(168,85,247,0.6)',
    borderGlow: 'rgba(168,85,247,0.5)',
    cardGlow: '0 20px 60px rgba(168,85,247,0.15)',
    tagStyle: 'bg-purple-500/10 border border-purple-500/25 text-purple-400',
  },
  {
    icon: '✍️',
    title: 'Writer Agent',
    description: 'Tailors your resume and generates a unique cover letter for every role in seconds — powered by LLM reasoning and your bullet bank.',
    tags: ['Resume', 'Cover Letter', 'Tailoring'],
    iconGradient: 'linear-gradient(135deg, rgba(52,211,153,0.5), rgba(16,185,129,0.3))',
    iconGlow: '0 0 20px rgba(52,211,153,0.6)',
    borderGlow: 'rgba(52,211,153,0.5)',
    cardGlow: '0 20px 60px rgba(52,211,153,0.15)',
    tagStyle: 'bg-emerald-500/10 border border-emerald-500/25 text-emerald-400',
  },
  {
    icon: '⚡',
    title: 'Applier Agent',
    description: 'Fills out application forms autonomously using Playwright with human-like behavior simulation — zero manual effort required.',
    tags: ['Playwright', 'Auto-Fill', 'Human-like'],
    iconGradient: 'linear-gradient(135deg, rgba(251,146,60,0.5), rgba(234,88,12,0.3))',
    iconGlow: '0 0 20px rgba(251,146,60,0.6)',
    borderGlow: 'rgba(251,146,60,0.5)',
    cardGlow: '0 20px 60px rgba(251,146,60,0.15)',
    tagStyle: 'bg-orange-500/10 border border-orange-500/25 text-orange-400',
  },
  {
    icon: '📊',
    title: 'Tracker Agent',
    description: 'Logs every application to MySQL, generates polished Excel reports, and automatically manages follow-up timelines.',
    tags: ['MySQL', 'Excel', 'Follow-up'],
    iconGradient: 'linear-gradient(135deg, rgba(34,211,238,0.5), rgba(6,182,212,0.3))',
    iconGlow: '0 0 20px rgba(34,211,238,0.6)',
    borderGlow: 'rgba(34,211,238,0.5)',
    cardGlow: '0 20px 60px rgba(34,211,238,0.15)',
    tagStyle: 'bg-cyan-500/10 border border-cyan-500/25 text-cyan-400',
  },
  {
    icon: '📧',
    title: 'Email Agent',
    description: 'Scans Gmail & Outlook to detect interview invitations and rejections — automatically syncing your status in real time.',
    tags: ['Gmail', 'Outlook', 'NLP'],
    iconGradient: 'linear-gradient(135deg, rgba(244,114,182,0.5), rgba(219,39,119,0.3))',
    iconGlow: '0 0 20px rgba(244,114,182,0.6)',
    borderGlow: 'rgba(244,114,182,0.5)',
    cardGlow: '0 20px 60px rgba(244,114,182,0.15)',
    tagStyle: 'bg-pink-500/10 border border-pink-500/25 text-pink-400',
  },
];

const containerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 35 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' as const } },
};

const Agents: React.FC = () => (
  <section id="how-it-works" className="relative py-32 lg:py-40 overflow-hidden">
    <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-600/12 rounded-full blur-3xl pointer-events-none" />
    <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

    <div className="max-w-7xl mx-auto px-6">

      {/* Section header */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.6 }}
        className="text-center max-w-2xl mx-auto mb-16"
      >
        <div
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium mb-5"
          style={{
            background: 'rgba(99,102,241,0.08)',
            border: '1px solid rgba(99,102,241,0.25)',
            color: '#818cf8',
          }}
        >
          6 Specialized AI Agents
        </div>
        <h2 className="text-5xl sm:text-6xl font-black text-white mb-5 leading-tight">
          A full team of AI{' '}
          <span
            className="bg-clip-text text-transparent"
            style={{ backgroundImage: 'linear-gradient(135deg, #818cf8, #a78bfa, #34d399)' }}
          >
            working for you
          </span>
        </h2>
        <p className="text-white/45 text-lg leading-relaxed">
          Every step of the job hunt automated by a dedicated specialist agent — scout, analyse, write, apply, track, and respond.
        </p>
      </motion.div>

      {/* Agent grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-80px' }}
        className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5"
      >
        {agents.map((agent) => (
          <motion.div
            key={agent.title}
            variants={cardVariants}
            whileHover={{
              y: -8,
              boxShadow: agent.cardGlow,
            }}
            transition={{ type: 'spring', stiffness: 280, damping: 22 }}
            className="relative rounded-2xl p-[1px] cursor-default group"
            style={{
              background: `linear-gradient(135deg, ${agent.borderGlow.replace(')', ', 0.3)').replace('rgba', 'rgba')}, rgba(255,255,255,0.05), rgba(255,255,255,0.02))`,
            }}
          >
            {/* Inner card */}
            <div
              className="rounded-2xl p-6 h-full"
              style={{ background: 'rgba(8,8,24,0.95)' }}
            >
              {/* Icon with gradient background */}
              <motion.div
                whileHover={{ boxShadow: agent.iconGlow }}
                className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-4 transition-shadow duration-300"
                style={{ background: agent.iconGradient }}
              >
                {agent.icon}
              </motion.div>

              {/* Title */}
              <h3 className="text-lg font-bold text-white mb-2">{agent.title}</h3>

              {/* Description */}
              <p className="text-white/45 text-sm leading-relaxed mb-4">{agent.description}</p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1.5">
                {agent.tags.map((tag) => (
                  <span key={tag} className={`px-2.5 py-0.5 rounded-md text-xs font-mono ${agent.tagStyle}`}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  </section>
);

export default Agents;
