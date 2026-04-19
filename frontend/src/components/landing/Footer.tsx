import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <footer className="border-t border-white/[0.06] py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">

          {/* Brand */}
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-sm">⚡</div>
            <span className="font-bold text-white text-base tracking-tight">
              JobPilot{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
                AI
              </span>
            </span>
          </Link>

          {/* Nav links */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-white/40">
            <button onClick={() => scrollTo('how-it-works')} className="hover:text-white transition-colors">How It Works</button>
            <button onClick={() => scrollTo('features')} className="hover:text-white transition-colors">Features</button>
            <button onClick={() => scrollTo('stats')} className="hover:text-white transition-colors">Stats</button>
            <a
              href="https://github.com/phoneixvenkat/ai-job-agent"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              GitHub
            </a>
            <a href="mailto:venkatasaikumarerla@gmail.com" className="hover:text-white transition-colors">
              Contact
            </a>
          </div>

          {/* Credit */}
          <div className="text-xs text-white/25 text-center md:text-right leading-relaxed">
            Built by <span className="text-white/50">Venkatasaikumar Erla</span>
            <br />
            MS Data Science Capstone · UNH 2026
            <br />
            Advisor: Dr. Moin Bhuiyan
          </div>

        </div>

        {/* Bottom line */}
        <div className="mt-8 pt-6 border-t border-white/[0.04] text-center text-xs text-white/20">
          © 2026 JobPilot AI. Open source under MIT License.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
