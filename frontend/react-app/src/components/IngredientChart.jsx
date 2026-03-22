import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const getBarColor = (score) => {
  if (score <= 3) return '#22c55e';
  if (score <= 6) return '#eab308';
  return '#ef4444';
};

export function IngredientChart({ ingredients }) {
  if (!ingredients || ingredients.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
        No ingredients to display
      </div>
    );
  }

  const chartData = ingredients.slice(0, 12).map((ing) => ({
    name: ing.name.length > 20 ? ing.name.substring(0, 17) + '...' : ing.name,
    score: parseFloat(ing.ewg_score),
    fullName: ing.name,
  }));

  const safeCount = ingredients.filter((ing) => ing.safety_label === 'SAFE').length;
  const moderateCount = ingredients.filter((ing) => ing.safety_label === 'MODERATE').length;
  const hazardousCount = ingredients.filter((ing) => ing.safety_label === 'HAZARDOUS').length;

  const pieData = [
    { name: 'Safe', value: safeCount, color: '#22c55e' },
    { name: 'Moderate', value: moderateCount, color: '#eab308' },
    { name: 'Hazardous', value: hazardousCount, color: '#ef4444' },
  ].filter((item) => item.value > 0);

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '24px',
        marginBottom: '32px',
      }}
    >
      {/* Left: Bar Chart */}
      <div
        style={{
          backgroundColor: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '16px',
        }}
      >
        <h3
          style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#1e293b',
            marginBottom: '16px',
          }}
        >
          Ingredient Safety Scores
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" domain={[0, 10]} stroke="#94a3b8" />
            <YAxis dataKey="name" type="category" stroke="#94a3b8" width={95} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '12px',
              }}
              formatter={(value) => `EWG: ${value.toFixed(1)}`}
              labelFormatter={(label) => label}
            />
            <Bar dataKey="score" fill="#6366f1" radius={[0, 8, 8, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Right: Pie Chart */}
      <div
        style={{
          backgroundColor: 'white',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '16px',
        }}
      >
        <h3
          style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#1e293b',
            marginBottom: '16px',
          }}
        >
          Safety Distribution
        </h3>
        {pieData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
            No data to display
          </div>
        )}
      </div>
    </div>
  );
}

export default IngredientChart;
