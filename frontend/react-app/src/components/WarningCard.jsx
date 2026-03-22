const getSeverityStyle = (severity) => {
  const styles = {
    DANGER: {
      bg: '#fee2e2',
      text: '#991b1b',
      borderLeft: '#ef4444',
      badgeBg: '#ef4444',
      badgeText: 'white',
    },
    WARNING: {
      bg: '#ffedd5',
      text: '#9a3412',
      borderLeft: '#f97316',
      badgeBg: '#f97316',
      badgeText: 'white',
    },
    CAUTION: {
      bg: '#fef9c3',
      text: '#854d0e',
      borderLeft: '#eab308',
      badgeBg: '#eab308',
      badgeText: '#1e293b',
    },
    'SAFE_NOTE': {
      bg: '#dcfce7',
      text: '#166534',
      borderLeft: '#22c55e',
      badgeBg: '#22c55e',
      badgeText: 'white',
    },
  };
  return styles[severity] || styles.CAUTION;
};

export function WarningCard({ warning }) {
  const style = getSeverityStyle(warning.severity);

  return (
    <div
      style={{
        backgroundColor: style.bg,
        color: style.text,
        borderLeft: `4px solid ${style.borderLeft}`,
        padding: '16px',
        borderRadius: '8px',
        marginBottom: '12px',
      }}
    >
      <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
        <span
          style={{
            display: 'inline-block',
            backgroundColor: style.badgeBg,
            color: style.badgeText,
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 600,
            whiteSpace: 'nowrap',
          }}
        >
          {warning.severity}
        </span>
        <span
          style={{
            display: 'inline-block',
            backgroundColor: 'rgba(0, 0, 0, 0.08)',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 500,
          }}
        >
          {warning.profile}
        </span>
      </div>
      <p style={{ fontSize: '15px', fontWeight: 600, marginBottom: '8px' }}>
        {warning.ingredient}
      </p>
      <p style={{ fontSize: '14px', lineHeight: '1.5', opacity: 0.9 }}>
        {warning.message}
      </p>
    </div>
  );
}

export default WarningCard;
