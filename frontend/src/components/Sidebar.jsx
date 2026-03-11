import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, MessageSquare, ScrollText,
  Server, BarChart3, Settings, Shield
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/playground', label: 'Playground', icon: MessageSquare },
  { path: '/logs', label: 'Request Logs', icon: ScrollText },
  { path: '/models', label: 'Models', icon: Server },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Shield size={24} />
        </div>
        <div className="brand-text">
          <span className="brand-name">AegisNet</span>
          <span className="brand-tag">Control Plane</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} strokeWidth={isActive ? 2.5 : 2} />
              <span>{item.label}</span>
              {isActive && <div className="nav-active-indicator" />}
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <div className="status-dot" />
          <span>System Healthy</span>
        </div>
        <div className="sidebar-version">v0.1.0</div>
      </div>
    </aside>
  );
}
