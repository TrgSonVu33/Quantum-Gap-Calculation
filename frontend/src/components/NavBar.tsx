import type { FC } from 'react';

interface NavBarProps {
  currentPath: string;
  navigate: (to: string) => void;
}

const HomeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    aria-hidden="true">
    <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

const NoteIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    aria-hidden="true">
    <rect x="5" y="2" width="14" height="20" rx="2" ry="2" />
    <line x1="9" y1="7" x2="15" y2="7" />
    <line x1="9" y1="11" x2="15" y2="11" />
    <line x1="9" y1="15" x2="13" y2="15" />
  </svg>
);

const NAV_LINKS = [
  { label: 'Home',      Icon: HomeIcon, path: '/' },
  { label: 'Dashboard', Icon: NoteIcon, path: '/dashboard' },
];

export const NavBar: FC<NavBarProps> = ({ currentPath, navigate }) => {
  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, to: string) => {
    e.preventDefault();
    navigate(to);
  };

  return (
    <nav className="navbar glass-panel" role="navigation" aria-label="Main navigation">
      <span className="navbar-brand">
        <span>Quantum Gap Calculation</span>
      </span>
      <ul className="navbar-links" role="list">
        {NAV_LINKS.map(({ label, Icon, path }) => (
          <li key={path}>
            <a
              href={path}
              className={`nav-link nav-link--icon${currentPath === path ? ' nav-link--active' : ''}`}
              aria-current={currentPath === path ? 'page' : undefined}
              aria-label={label}
              title={label}
              onClick={(e) => handleClick(e, path)}
            >
              <Icon />
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};
