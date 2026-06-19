import { useContext, useState } from 'react';
import { ProfileContext } from '../App';
import { analyzeIngredients } from '../api/client';
import IngredientCard from '../components/IngredientCard';
import WarningCard from '../components/WarningCard';
import GradeBadge from '../components/GradeBadge';

function IngredientChecker() {
  const { profiles, selectedProfiles, setSelectedProfiles } = useContext(ProfileContext);
  const [ingredientText, setIngredientText] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const exampleIngredients = [
    { name: 'Water, Glycerin, Cetyl Alcohol, Stearic Acid, Petrolatum', label: 'Basic Moisturizer' },
    { name: 'Water, Butylene Glycol, Niacinamide, Mica, CI 77891', label: 'Tinted Serum' },
    { name: 'Aqua, Paraben, Lead Acetate, Titanium Dioxide, Talc', label: 'Budget Powder' },
  ];

  const handleAnalyze = async () => {
    if (!ingredientText.trim()) {
      setError('Please enter or select ingredients');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setProgress(0);

    const ingredients = ingredientText
      .split(',')
      .map((ing) => ing.trim())
      .filter((ing) => ing.length > 0);

    // Single batch call instead of N+1 individual calls
    setProgress(50);
    const response = await analyzeIngredients(ingredientText, selectedProfiles);

    if (response.error || !response.data) {
      setError(response.error || 'Failed to analyze ingredients');
      setLoading(false);
      return;
    }

    const allResults = response.data.ingredients || [];
    const warnings = response.data.warnings || [];
    let totalScore = 0;
    let hazardousCounts = { SAFE: 0, MODERATE: 0, HAZARDOUS: 0 };

    for (const ingredient of allResults) {
      totalScore += ingredient.ewg_score || 0;
      const safetyLabel = ingredient.safety_label;
      hazardousCounts[safetyLabel] = (hazardousCounts[safetyLabel] || 0) + 1;
    }

    setProgress(100);
    setLoading(false);

    // Calculate overall grade
    const averageScore = allResults.length > 0 ? totalScore / allResults.length : 0;
    let grade = 'A';
    if (hazardousCounts.HAZARDOUS > 0) grade = 'F';
    else if (hazardousCounts.MODERATE > allResults.length * 0.5) grade = 'C';
    else if (hazardousCounts.MODERATE > 0) grade = 'B';

    setResult({
      grade,
      safety_score: Math.round((10 - averageScore / 10) * 100) / 100,
      ingredients: allResults,
      warnings,
      distribution: hazardousCounts,
    });
  };

  const handleProfileToggle = (profileId) => {
    setSelectedProfiles((prev) =>
      prev.includes(profileId) ? prev.filter((p) => p !== profileId) : [...prev, profileId]
    );
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey && !loading) {
      handleAnalyze();
    }
  };

  const topConcerns = result
    ? result.ingredients
        .filter((ing) => ing.safety_level !== 'SAFE')
        .sort((a, b) => (b.ewg_score || 0) - (a.ewg_score || 0))
        .slice(0, 5)
    : [];

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
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '32px' }}>📋 Ingredient Checker</h1>

        {/* Ingredient Textarea */}
        <div style={{ marginBottom: '32px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#334155' }}>
            Ingredients List
          </label>
          <textarea
            value={ingredientText}
            onChange={(e) => setIngredientText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Water, Glycerin, Cetyl Alcohol, Stearic Acid..."
            style={{
              width: '100%',
              height: '150px',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              fontSize: '14px',
              fontFamily: 'Segoe UI, -apple-system, sans-serif',
              boxSizing: 'border-box',
              resize: 'none',
            }}
          />
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '6px' }}>
            Paste or type ingredients separated by commas (Ctrl+Enter to analyze)
          </p>
        </div>

        {/* Example Buttons */}
        <div style={{ marginBottom: '32px' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '8px' }}>Quick Examples:</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {exampleIngredients.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setIngredientText(example.name)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0',
                  backgroundColor: 'white',
                  fontSize: '12px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#eef2ff';
                  e.target.style.borderColor = '#6366f1';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = 'white';
                  e.target.style.borderColor = '#e2e8f0';
                }}
              >
                {example.label}
              </button>
            ))}
          </div>
        </div>

        {/* Profile Selection */}
        <div style={{ marginBottom: '32px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#334155' }}>
            Your Health Profile
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
          {loading ? `🔄 Analyzing ${Math.round(progress)}%` : '✨ Analyze Ingredients'}
        </button>

        {/* Progress Bar */}
        {loading && (
          <div style={{ marginTop: '16px' }}>
            <div
              style={{
                width: '100%',
                height: '6px',
                backgroundColor: '#e2e8f0',
                borderRadius: '3px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  backgroundColor: '#6366f1',
                  width: `${progress}%`,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>
        )}
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

        {result && (
          <div>
            {/* Header with Grade */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <h2 style={{ fontSize: '28px', fontWeight: 700, margin: 0 }}>Analysis Results</h2>
              <GradeBadge grade={result.grade} size="lg" score={result.safety_score} />
            </div>

            {/* Top Concerns */}
            {topConcerns.length > 0 && (
              <div style={{ marginBottom: '32px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Top Concerns</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {topConcerns.map((ingredient, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '12px',
                        backgroundColor: '#fff5f5',
                        borderLeft: '4px solid #ef4444',
                        borderRadius: '6px',
                      }}
                    >
                      <div style={{ fontWeight: 600, color: '#991b1b' }}>{ingredient.name}</div>
                      <div style={{ fontSize: '12px', color: '#be123c', marginTop: '4px' }}>
                        EWG Score: {ingredient.ewg_score}/10 • {ingredient.safety_level}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Safety Distribution */}
            <div
              style={{
                padding: '16px',
                backgroundColor: '#f1f5f9',
                borderRadius: '8px',
                marginBottom: '32px',
              }}
            >
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Safe</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#22c55e' }}>
                    {result.distribution.SAFE}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Moderate</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#f59e0b' }}>
                    {result.distribution.MODERATE}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Hazardous</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#ef4444' }}>
                    {result.distribution.HAZARDOUS}
                  </div>
                </div>
              </div>
            </div>

            {/* All Ingredients */}
            {result.ingredients.length > 0 && (
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>
                  All Ingredients ({result.ingredients.length})
                </h3>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
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
            <p style={{ fontSize: '16px' }}>Enter ingredients on the left to analyze them</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default IngredientChecker;
