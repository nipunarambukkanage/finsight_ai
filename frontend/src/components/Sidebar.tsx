import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Bot,
  Sparkles,
  FileText,
  Database,
  BarChart2,
  PieChart,
  Calculator,
  Cpu,
  Image,
  Mic,
  Award,
  Settings,
  ShieldCheck,
  Workflow
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navGroups = [
    {
      group: 'INTELLIGENCE WORKSPACES',
      items: [
        { path: '/', label: 'AI Dashboard', icon: LayoutDashboard, id: 'nav-dashboard' },
        { path: '/stocks', label: 'Stocks & Markets', icon: TrendingUp, id: 'nav-stocks' },
        { path: '/assistant', label: 'AI Research Assistant', icon: Bot, id: 'nav-assistant' },
        { path: '/research-agent', label: 'AI Research Agent', icon: Sparkles, id: 'nav-agent', badge: 'PRO' },
        { path: '/workflow', label: 'Autonomous Research Workflow', icon: Workflow, id: 'nav-workflow', badge: 'NEW' },
        { path: '/documents', label: 'Document Intelligence', icon: FileText, id: 'nav-documents' },
        { path: '/rag', label: 'RAG Knowledge System', icon: Database, id: 'nav-rag' },
      ]
    },
    {
      group: 'QUANTITATIVE & ML',
      items: [
        { path: '/portfolio', label: 'Portfolio Intelligence', icon: PieChart, id: 'nav-portfolio' },
        { path: '/sentiment', label: 'Financial Sentiment', icon: BarChart2, id: 'nav-sentiment' },
        { path: '/analytics-lab', label: 'Quantitative Analytics Lab', icon: Calculator, id: 'nav-analytics' },
        { path: '/ml-lab', label: 'ML Stock Lab', icon: Cpu, id: 'nav-ml', badge: 'LAB' },
      ]
    },
    {
      group: 'ADVANCED AI & PLATFORM',
      items: [
        { path: '/multimodal', label: 'Multimodal Vision', icon: Image, id: 'nav-multimodal' },
        { path: '/voice', label: 'Voice AI Briefing', icon: Mic, id: 'nav-voice' },
        { path: '/showcase', label: 'Technology Showcase', icon: Award, id: 'nav-showcase', badge: 'CLIENT' },
        { path: '/settings', label: 'Settings & Providers', icon: Settings, id: 'nav-settings' },
      ]
    }
  ];

  return (
    <aside
      id="main-sidebar"
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        position: 'fixed',
        top: 0,
        left: 0,
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 50,
        overflowY: 'auto'
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: '22px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          borderBottom: '1px solid var(--border-subtle)'
        }}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 16px var(--accent-cyan-glow)'
          }}
        >
          <ShieldCheck size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '16px', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            FinSight<span style={{ color: 'var(--accent-cyan)' }}>AI</span>
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Investment Intelligence
          </div>
        </div>
      </div>

      {/* Nav List */}
      <div style={{ padding: '16px 14px', display: 'flex', flexDirection: 'column', gap: '20px', flex: 1 }}>
        {navGroups.map((grp) => (
          <div key={grp.group}>
            <div
              style={{
                fontSize: '10px',
                fontWeight: 600,
                color: 'var(--text-muted)',
                letterSpacing: '0.08em',
                padding: '0 10px 8px 10px'
              }}
            >
              {grp.group}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              {grp.items.map((item) => {
                const IconComponent = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    id={item.id}
                    style={({ isActive }) => ({
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius-md)',
                      textDecoration: 'none',
                      fontSize: '13px',
                      fontWeight: isActive ? 600 : 400,
                      color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                      backgroundColor: isActive ? 'rgba(6, 182, 212, 0.08)' : 'transparent',
                      borderLeft: isActive ? '3px solid var(--accent-cyan)' : '3px solid transparent',
                      transition: 'all 0.15s ease'
                    })}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <IconComponent size={17} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`badge ${
                          item.badge === 'PRO' ? 'badge-amber' : item.badge === 'CLIENT' ? 'badge-purple' : 'badge-cyan'
                        }`}
                        style={{ fontSize: '9px', padding: '1px 6px' }}
                      >
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer info */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '11px',
          color: 'var(--text-muted)'
        }}
      >
        <div>Commercial Demo Platform v1.0</div>
        <div style={{ marginTop: '2px', color: 'var(--accent-emerald)' }}>● Engines Operational</div>
      </div>
    </aside>
  );
};
