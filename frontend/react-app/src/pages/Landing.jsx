import { useNavigate } from 'react-router-dom';
import GradeBadge from '../components/GradeBadge';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
      {/* Navigation */}
      <nav style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, margin: 0 }}>🧪 IngredientIQ</h1>
        <button
          onClick={() => navigate('/barcode')}
          style={{
            background: 'white',
            color: '#667eea',
            border: 'none',
            padding: '10px 24px',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Get Started
        </button>
      </nav>

      {/* Hero Section */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '80px 40px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '56px', fontWeight: 700, marginBottom: '24px', lineHeight: 1.2 }}>
          Know What's In Your Products
        </h2>
        <p style={{ fontSize: '20px', marginBottom: '48px', opacity: 0.9, maxWidth: '700px', margin: '0 auto 48px' }}>
          IngredientIQ uses AI to analyze product ingredients and provide personalized safety insights based on your health profile.
        </p>

        {/* CTA Buttons */}
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginBottom: '80px' }}>
          <button
            onClick={() => navigate('/barcode')}
            style={{
              background: 'white',
              color: '#667eea',
              border: 'none',
              padding: '16px 32px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '16px',
              cursor: 'pointer',
              boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
            }}
          >
            📱 Scan Barcode
          </button>
          <button
            onClick={() => navigate('/ingredient-checker')}
            style={{
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '2px solid white',
              padding: '14px 30px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '16px',
              cursor: 'pointer',
            }}
          >
            📋 Check Ingredients
          </button>
        </div>

        {/* Features Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '32px', marginTop: '80px' }}>
          {[
            { icon: '🔍', title: 'AI-Powered Analysis', desc: 'Advanced ML models score ingredient safety' },
            { icon: '👥', title: 'Health Profiles', desc: 'Personalized warnings for sensitive skin, pregnancy, allergies & more' },
            { icon: '📊', title: 'Safety Grades', desc: 'Get A-F grades for any product instantly' },
            { icon: '🎯', title: 'Detailed Insights', desc: 'Learn why ingredients matter for your health' },
          ].map((feature, i) => (
            <div
              key={i}
              style={{
                background: 'rgba(255,255,255,0.1)',
                padding: '32px',
                borderRadius: '12px',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.2)',
              }}
            >
              <div style={{ fontSize: '40px', marginBottom: '16px' }}>{feature.icon}</div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>{feature.title}</h3>
              <p style={{ fontSize: '14px', opacity: 0.8 }}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '80px 40px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '36px', fontWeight: 700, marginBottom: '60px' }}>How It Works</h2>
        <div style={{ display: 'flex', justifyContent: 'space-around', maxWidth: '1000px', margin: '0 auto', gap: '30px' }}>
          {[
            { num: '1️⃣', title: 'Scan or Enter', desc: 'Barcode, image, or ingredient list' },
            { num: '2️⃣', title: 'AI Analysis', desc: 'Our models analyze safety & risks' },
            { num: '3️⃣', title: 'Get Insights', desc: 'Personalized recommendations' },
          ].map((step, i) => (
            <div key={i} style={{ flex: 1 }}>
              <div style={{ fontSize: '32px', marginBottom: '16px' }}>{step.num}</div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>{step.title}</h3>
              <p style={{ fontSize: '14px', opacity: 0.8 }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer CTA */}
      <div style={{ padding: '80px 40px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '40px', fontWeight: 700, marginBottom: '32px' }}>Ready to Know What's Really In Your Products?</h2>
        <button
          onClick={() => navigate('/barcode')}
          style={{
            background: 'white',
            color: '#667eea',
            border: 'none',
            padding: '16px 40px',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '18px',
            cursor: 'pointer',
            boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
          }}
        >
          Start Scanning Now
        </button>
      </div>

      {/* Footer */}
      <div style={{ background: 'rgba(0,0,0,0.5)', padding: '40px', textAlign: 'center', fontSize: '14px', opacity: 0.7 }}>
        <p>IngredientIQ © 2026 | AI-Powered Product Safety Intelligence</p>
      </div>
    </div>
  );
}
