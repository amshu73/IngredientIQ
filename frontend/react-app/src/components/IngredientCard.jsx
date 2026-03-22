import { useState } from 'react';

const getProgressColor = (score) => {
  if (score <= 3) return '#22c55e';
  if (score <= 6) return '#eab308';
  return '#ef4444';
};

const getSafetyStyle = (label) => {
  const styles = {
    SAFE: { bg: '#dcfce7', text: '#166534' },
    MODERATE: { bg: '#fef9c3', text: '#854d0e' },
    HAZARDOUS: { bg: '#fee2e2', text: '#991b1b' },
    UNKNOWN: { bg: '#f1f5f9', text: '#475569' },
  };
  return styles[label] || styles.UNKNOWN;
};

export function IngredientCard({ ingredient }) {
  const [showWarnings, setShowWarnings] = useState(false);
  const safetyStyle = getSafetyStyle(ingredient.safety_label);
  const progressColor = getProgressColor(ingredient.ewg_score);
  const warningCount = ingredient.profile_warnings?.length || 0;

  return (
    <div
      style={{
        backgroundColor: 'white',
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '16px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <h3
          style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#1e293b',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            flex: 1,
          }}
        >
          {ingredient.name}
        </h3>
        {warningCount > 0 && (
          <button
            onClick={() => setShowWarnings(!showWarnings)}
            style={{
              background: '#ef4444',
              color: 'white',
              fontSize: '11px',
              fontWeight: 600,
              border: 'none',
              borderRadius: '50%',
              width: '24px',
              height: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              marginLeft: '8px',
              flexShrink: 0,
            }}
          >
            {warningCount}
          </button>
        )}
      </div>

      <div style={{ marginBottom: '12px' }}>
        <span
          style={{
            backgroundColor: safetyStyle.bg,
            color: safetyStyle.text,
            padding: '3px 10px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 500,
            display: 'inline-block',
          }}
        >
          {ingredient.safety_label}
        </span>
      </div>

      <div style={{ marginBottom: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <label style={{ fontSize: '12px', color: '#64748b', fontWeight: 500 }}>EWG Score</label>
          <span style={{ fontSize: '14px', fontWeight: 600, color: '#1e293b' }}>
            {ingredient.ewg_score.toFixed(1)}/10
          </span>
        </div>
        <div
          style={{
            width: '100%',
            height: '6px',
            backgroundColor: '#e2e8f0',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${(ingredient.ewg_score / 10) * 100}%`,
              height: '100%',
              backgroundColor: progressColor,
              transition: 'width 0.3s ease',
            }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        <span
          style={{
            backgroundColor: '#f1f5f9',
            color: '#475569',
            padding: '4px 10px',
            borderRadius: '16px',
            fontSize: '11px',
            fontWeight: 500,
          }}
        >
          {ingredient.chemical_family}
        </span>
        {ingredient.allergen && (
          <span
            style={{
              backgroundColor: '#fee2e2',
              color: '#991b1b',
              padding: '4px 10px',
              borderRadius: '16px',
              fontSize: '11px',
              fontWeight: 500,
            }}
          >
            Allergen
          </span>
        )}
        {ingredient.endocrine_disruptor && (
          <span
            style={{
              backgroundColor: '#ffedd5',
              color: '#9a3412',
              padding: '4px 10px',
              borderRadius: '16px',
              fontSize: '11px',
              fontWeight: 500,
            }}
          >
            Endocrine
          </span>
        )}
        {!ingredient.pregnancy_safe && (
          <span
            style={{
              backgroundColor: '#e9d5ff',
              color: '#6b21a8',
              padding: '4px 10px',
              borderRadius: '16px',
              fontSize: '11px',
              fontWeight: 500,
            }}
          >
            Pregnancy
          </span>
        )}
        {!ingredient.vegan && (
          <span
            style={{
              backgroundColor: '#fef3c7',
              color: '#78350f',
              padding: '4px 10px',
              borderRadius: '16px',
              fontSize: '11px',
              fontWeight: 500,
            }}
          >
            Not vegan
          </span>
        )}
      </div>

      {showWarnings && ingredient.profile_warnings && ingredient.profile_warnings.length > 0 && (
        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e2e8f0' }}>
          <p style={{ fontSize: '12px', fontWeight: 600, color: '#ef4444', marginBottom: '8px' }}>
            Health Warnings:
          </p>
          {ingredient.profile_warnings.map((warning, idx) => (
            <div key={idx} style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>
              • {warning.profile}: {warning.severity}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default IngredientCard;
