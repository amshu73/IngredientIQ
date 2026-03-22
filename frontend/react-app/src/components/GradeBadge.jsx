const getGradeColor = (grade) => {
  const colors = {
    A: { bg: '#dcfce7', text: '#166534', border: '#86efac' },
    B: { bg: '#d1fae5', text: '#065f46', border: '#6ee7b7' },
    C: { bg: '#fef9c3', text: '#854d0e', border: '#fde047' },
    D: { bg: '#ffedd5', text: '#9a3412', border: '#fed7aa' },
    F: { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' },
  };
  return colors[grade] || colors.F;
};

export function GradeBadge({ grade, score, size = 'md' }) {
  const colors = getGradeColor(grade);
  
  const sizes = {
    sm: { circle: 48, fontSize: 20, scoreFontSize: 0 },
    md: { circle: 80, fontSize: 32, scoreFontSize: 12 },
    lg: { circle: 120, fontSize: 48, scoreFontSize: 14 },
  };
  
  const sizeConfig = sizes[size];
  const isPulse = grade === 'F';

  return (
    <div
      className={isPulse ? 'pulse' : ''}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: size === 'sm' ? 0 : 8,
      }}
    >
      <div
        style={{
          width: sizeConfig.circle,
          height: sizeConfig.circle,
          borderRadius: '50%',
          backgroundColor: colors.bg,
          border: `2px solid ${colors.border}`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 700,
          fontSize: sizeConfig.fontSize,
          color: colors.text,
        }}
      >
        {grade}
      </div>
      {score !== undefined && sizeConfig.scoreFontSize > 0 && (
        <div
          style={{
            fontSize: sizeConfig.scoreFontSize,
            color: colors.text,
            fontWeight: 600,
          }}
        >
          {score.toFixed(1)}/10
        </div>
      )}
    </div>
  );
}

export default GradeBadge;
