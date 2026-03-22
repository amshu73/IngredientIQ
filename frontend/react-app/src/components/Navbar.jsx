import { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { checkHealth } from '../api/client';

export function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isApiOnline, setIsApiOnline] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    checkHealth().then((response) => {
      setIsApiOnline(response.status === 200);
    });
  }, []);

  const navItems = [
    { label: '🏠 Home', path: '/' },
    { label: '🔍 Barcode', path: '/barcode' },
    { label: '📋 Ingredients', path: '/ingredients' },
    { label: '📷 Photo', path: '/photo' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        width: '100%',
        height: '64px',
        backgroundColor: 'white',
        borderBottom: '1px solid #e2e8f0',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        paddingLeft: '24px',
        paddingRight: '24px',
      }}
    >
      {/* Logo */}
      <Link
        to="/"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          textDecoration: 'none',
          marginRight: '32px',
        }}
      >
        <span style={{ fontSize: '24px' }}>🔬</span>
        <span
          style={{
            fontSize: '20px',
            fontWeight: 700,
            color: '#6366f1',
          }}
        >
          IngredientIQ
        </span>
      </Link>

      {/* Desktop Navigation */}
      <div
        style={{
          display: 'none',
          '@media (min-width: 768px)': {
            display: 'flex',
          },
          gap: '32px',
          flex: 1,
        }}
      >
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              color: isActive(item.path) ? '#6366f1' : '#64748b',
              textDecoration: 'none',
              fontSize: '15px',
              fontWeight: 500,
              paddingBottom: '4px',
              borderBottom: isActive(item.path) ? '2px solid #6366f1' : 'none',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!isActive(item.path)) {
                e.target.style.color = '#6366f1';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive(item.path)) {
                e.target.style.color = '#64748b';
              }
            }}
          >
            {item.label}
          </Link>
        ))}
      </div>

      {/* Right side: API Status + GitHub */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
          marginLeft: 'auto',
        }}
      >
        {/* API Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            color: isApiOnline ? '#22c55e' : '#ef4444',
          }}
        >
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isApiOnline ? '#22c55e' : '#ef4444',
            }}
          />
          {isApiOnline ? 'API Online' : 'API Offline'}
        </div>

        {/* GitHub Link */}
        <a
          href="https://github.com/yourusername/ingredientiq"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: '#6366f1',
            textDecoration: 'none',
            fontSize: '13px',
            fontWeight: 500,
          }}
        >
          GitHub
        </a>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          style={{
            display: 'none',
            '@media (max-width: 768px)': {
              display: 'block',
            },
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '24px',
          }}
        >
          {mobileMenuOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div
          style={{
            position: 'absolute',
            top: '64px',
            left: 0,
            width: '100%',
            backgroundColor: 'white',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            flexDirection: 'column',
            padding: '16px',
            gap: '12px',
          }}
        >
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              style={{
                color: isActive(item.path) ? '#6366f1' : '#64748b',
                textDecoration: 'none',
                fontSize: '15px',
                fontWeight: 500,
              }}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}

export default Navbar;
