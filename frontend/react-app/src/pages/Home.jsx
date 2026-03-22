import { useNavigate } from 'react-router-dom';
import GradeBadge from '../components/GradeBadge';

function Home() {
  const navigate = useNavigate();

  const features = [
    {
      icon: '🔍',
      title: 'Barcode Scanning',
      description: 'Scan product barcodes to instantly analyze ingredients',
    },
    {
      icon: '📷',
      title: 'Photo Recognition',
      description: 'Photograph ingredient lists for automatic extraction',
    },
    {
      icon: '📋',
      title: 'Manual Entry',
      description: 'Paste ingredient lists or type them manually',
    },
  ];

  const exampleProducts = [
    {
      barcode: '5010724154018',
      name: 'Example Foundation',
      grade: 'C',
      concerns: 5,
    },
    {
      barcode: '8718951320065',
      name: 'Example Moisturizer',
      grade: 'B',
      concerns: 2,
    },
    {
      barcode: '3614270406127',
      name: 'Example Serum',
      grade: 'A',
      concerns: 0,
    },
  ];

  const steps = [
    { number: 1, title: 'Input', description: 'Scan, upload, or paste product details' },
    { number: 2, title: 'Extract', description: 'AI extracts and normalizes ingredients' },
    { number: 3, title: 'Analyze', description: 'ML model scores safety & identifies issues' },
    { number: 4, title: 'Personalize', description: 'Get warnings for your health profile' },
  ];

  return (
    <main style={{ paddingBottom: '80px' }}>
      {/* Hero Section */}
      <section
        style={{
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          color: 'white',
          padding: '80px 24px',
          textAlign: 'center',
          marginBottom: '60px',
        }}
      >
        <h1 style={{ fontSize: '48px', fontWeight: 800, marginBottom: '16px', lineHeight: 1.2 }}>
          Know Your Skincare
        </h1>
        <p
          style={{
            fontSize: '20px',
            marginBottom: '32px',
            opacity: 0.95,
            maxWidth: '600px',
            margin: '0 auto 32px',
          }}
        >
          Discover what's really in your beauty products. Get personalized safety warnings for your skin and health.
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={() => navigate('/barcode')}
            style={{
              backgroundColor: 'white',
              color: '#6366f1',
              padding: '12px 32px',
              borderRadius: '12px',
              border: 'none',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            🔍 Scan Barcode
          </button>
          <button
            onClick={() => navigate('/ingredients')}
            style={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              padding: '12px 32px',
              borderRadius: '12px',
              border: '2px solid white',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'rgba(255,255,255,0.3)';
              e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'rgba(255,255,255,0.2)';
              e.target.style.transform = 'translateY(0)';
            }}
          >
            📋 Check Ingredients
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '0 24px', marginBottom: '80px', maxWidth: '1200px', margin: '0 auto 80px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 700, textAlign: 'center', marginBottom: '48px' }}>
          How It Works
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '32px',
          }}
        >
          {features.map((feature, idx) => (
            <div
              key={idx}
              style={{
                padding: '32px',
                backgroundColor: 'white',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                textAlign: 'center',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.08)';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>{feature.icon}</div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '8px' }}>{feature.title}</h3>
              <p style={{ fontSize: '14px', color: '#64748b' }}>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Steps Section */}
      <section
        style={{
          backgroundColor: '#f8fafc',
          padding: '64px 24px',
          marginBottom: '80px',
        }}
      >
        <h2 style={{ fontSize: '32px', fontWeight: 700, textAlign: 'center', marginBottom: '48px' }}>
          Our Process
        </h2>
        <div
          style={{
            maxWidth: '1000px',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '32px',
          }}
        >
          {steps.map((step) => (
            <div key={step.number} style={{ textAlign: 'center' }}>
              <div
                style={{
                  width: '60px',
                  height: '60px',
                  backgroundColor: '#6366f1',
                  color: 'white',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '28px',
                  fontWeight: 700,
                  margin: '0 auto 16px',
                }}
              >
                {step.number}
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>{step.title}</h3>
              <p style={{ fontSize: '14px', color: '#64748b' }}>{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Example Products */}
      <section style={{ padding: '0 24px', marginBottom: '80px', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 700, textAlign: 'center', marginBottom: '48px' }}>
          Try These Examples
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '32px',
          }}
        >
          {exampleProducts.map((product, idx) => (
            <div
              key={idx}
              onClick={() => navigate(`/barcode?barcode=${product.barcode}`)}
              style={{
                padding: '24px',
                backgroundColor: 'white',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(99, 102, 241, 0.12)';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 700 }}>{product.name}</h3>
                <GradeBadge grade={product.grade} size="md" />
              </div>
              <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '12px' }}>
                Barcode: <code style={{ backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>{product.barcode}</code>
              </p>
              <p style={{ fontSize: '13px', color: '#f97316' }}>⚠️ {product.concerns} concern{product.concerns !== 1 ? 's' : ''}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Footer */}
      <section
        style={{
          backgroundColor: '#6366f1',
          color: 'white',
          padding: '64px 24px',
          textAlign: 'center',
        }}
      >
        <h2 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '16px' }}>
          Ready to Know What's In Your Products?
        </h2>
        <p style={{ fontSize: '18px', marginBottom: '32px', opacity: 0.95 }}>
          Start scanning, uploading, or typing now. Your personalized analysis takes seconds.
        </p>
        <button
          onClick={() => navigate('/barcode')}
          style={{
            backgroundColor: 'white',
            color: '#6366f1',
            padding: '14px 40px',
            borderRadius: '12px',
            border: 'none',
            fontSize: '16px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = 'none';
          }}
        >
          Get Started Now →
        </button>
      </section>
    </main>
  );
}

export default Home;
