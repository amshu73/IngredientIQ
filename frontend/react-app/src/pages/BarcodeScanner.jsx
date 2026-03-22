import { useContext, useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ProfileContext } from '../App';
import { scanBarcode } from '../api/client';
import IngredientChart from '../components/IngredientChart';
import IngredientCard from '../components/IngredientCard';
import WarningCard from '../components/WarningCard';
import GradeBadge from '../components/GradeBadge';

function BarcodeScanner() {
  const { profiles, selectedProfiles, setSelectedProfiles } = useContext(ProfileContext);
  const [searchParams] = useSearchParams();
  const [barcode, setBarcode] = useState(searchParams.get('barcode') || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!barcode.trim()) {
      setError('Please enter a barcode');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const response = await scanBarcode(barcode, selectedProfiles);
    setLoading(false);

    if (response.error) {
      setError(response.error);
    } else {
      setResult(response.data);
    }
  };

  const handleProfileToggle = (profileId) => {
    setSelectedProfiles((prev) =>
      prev.includes(profileId) ? prev.filter((p) => p !== profileId) : [...prev, profileId]
    );
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleAnalyze();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        minHeight: 'calc(100vh - 64px)',
        backgroundColor: '#f8fafc',
      }}
    >
      {/* Left Panel: Input (40%) */}
      <div
        style={{
          flex: '0 0 40%',
          padding: '40px',
          backgroundColor: 'white',
          borderRight: '1px solid #e2e8f0',
          overflowY: 'auto',
          maxHeight: 'calc(100vh - 64px)',
        }}
      >
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '32px' }}>🔍 Barcode Scanner</h1>

        {/* Barcode Input */}
        <div style={{ marginBottom: '32px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#334155' }}>
            Product Barcode
          </label>
          <input
            type="text"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., 5010724154018"
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              fontSize: '14px',
              boxSizing: 'border-box',
            }}
          />
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '6px' }}>
            Find barcodes on product packaging (usually 12-14 digits)
          </p>
        </div>

        {/* Profile Selection */}
        <div style={{ marginBottom: '32px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#334155' }}>
            Your Health Profile (Select All That Apply)
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {profiles.map((profile) => (
              <label
                key={profile.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  backgroundColor: selectedProfiles.includes(profile.id) ? '#eef2ff' : 'transparent',
                  transition: 'background-color 0.2s',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedProfiles.includes(profile.id)}
                  onChange={() => handleProfileToggle(profile.id)}
                  style={{ cursor: 'pointer' }}
                />
                <span style={{ fontSize: '14px' }}>{profile.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: loading ? '#cbd5e1' : '#6366f1',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            if (!loading) {
              e.target.style.backgroundColor = '#4f46e5';
              e.target.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseLeave={(e) => {
            if (!loading) {
              e.target.style.backgroundColor = '#6366f1';
              e.target.style.transform = 'translateY(0)';
            }
          }}
        >
          {loading ? '🔄 Analyzing...' : '🔍 Analyze Product'}
        </button>
      </div>

      {/* Right Panel: Results (60%) */}
      <div
        style={{
          flex: '0 0 60%',
          padding: '40px',
          overflowY: 'auto',
          maxHeight: 'calc(100vh - 64px)',
        }}
      >
        {error && (
          <div
            style={{
              padding: '16px',
              backgroundColor: '#fee2e2',
              borderLeft: '4px solid #ef4444',
              borderRadius: '8px',
              marginBottom: '24px',
            }}
          >
            <p style={{ margin: 0, color: '#991b1b', fontSize: '14px' }}>❌ {error}</p>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                border: '3px solid #e2e8f0',
                borderTop: '3px solid #6366f1',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px',
              }}
            />
            <p style={{ color: '#64748b', fontSize: '16px' }}>Analyzing product...</p>
          </div>
        )}

        {result && (
          <div>
            {/* Product Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: 700, margin: '0 0 8px 0' }}>
                  {result.product_name || 'Unknown Product'}
                </h2>
                <p style={{ fontSize: '14px', color: '#64748b', margin: 0 }}>
                  Barcode: <code style={{ backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>{barcode}</code>
                </p>
              </div>
              <GradeBadge grade={result.grade} size="lg" score={result.safety_score} />
            </div>

            {/* Charts */}
            {result.ingredients && result.ingredients.length > 0 && (
              <div style={{ marginBottom: '32px' }}>
                <IngredientChart ingredients={result.ingredients} />
              </div>
            )}

            {/* Warnings */}
            {result.warnings && result.warnings.length > 0 && (
              <div style={{ marginBottom: '32px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Warnings</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {result.warnings.map((warning, idx) => (
                    <WarningCard key={idx} warning={warning} />
                  ))}
                </div>
              </div>
            )}

            {/* Ingredients */}
            {result.ingredients && result.ingredients.length > 0 && (
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>
                  All Ingredients ({result.ingredients.length})
                </h3>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: '16px',
                  }}
                >
                  {result.ingredients.map((ingredient, idx) => (
                    <IngredientCard key={idx} ingredient={ingredient} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {!result && !loading && !error && (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
            <p style={{ fontSize: '16px' }}>Enter a barcode and click "Analyze Product" to get started</p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default BarcodeScanner;
