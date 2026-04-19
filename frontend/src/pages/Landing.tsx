import React, { useEffect } from 'react';
import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import Agents from '../components/landing/Agents';
import Features from '../components/landing/Features';
import Demo from '../components/landing/Demo';
import Stats from '../components/landing/Stats';
import Testimonials from '../components/landing/Testimonials';
import CTA from '../components/landing/CTA';
import Footer from '../components/landing/Footer';

const Divider: React.FC = () => (
  <div className="max-w-6xl mx-auto px-6">
    <div
      className="h-px"
      style={{
        background: 'linear-gradient(90deg, transparent 0%, rgba(99,102,241,0.2) 30%, rgba(168,85,247,0.25) 50%, rgba(99,102,241,0.2) 70%, transparent 100%)',
      }}
    />
  </div>
);

const Landing: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
    document.body.style.background = '#050510';
    return () => { document.body.style.background = ''; };
  }, []);

  return (
    <div className="min-h-screen bg-[#050510] text-white overflow-x-hidden">
      <Navbar />

      <main>
        <Hero />
        <Divider />
        <Agents />
        <Divider />
        <Features />
        <Divider />
        <Demo />
        <Divider />
        <Stats />
        <Divider />
        <Testimonials />
        <Divider />
        <CTA />
      </main>

      <Footer />
    </div>
  );
};

export default Landing;
