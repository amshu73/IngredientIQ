import { useContext, useState } from 'react';
import { ProfileContext } from '../App';
import { scanImage } from '../api/client';
import IngredientChart from '../components/IngredientChart';
import IngredientCard from '../components/IngredientCard';
import WarningCard from '../components/WarningCard';
import GradeBadge from '../components/GradeBadge';

function PhotoScanner() {
  const { profiles, selectedProfiles, setSelectedProfiles } = useContext(ProfileContext);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [rawText, setRawText] = useState('');
  const [showRawText, setShowRawText] = useState(false);

  const handleFileSelect = async (file) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    // Read preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Convert to base64 for API
    const fileReader = new FileReader();
    fileReader.onload = async (e) => {
      const base64String = e.target.result.split(',')[1];
      await handleAnalyzeImage(base64String);
    };
    fileReader.readAsDataURL(file);
  };

  const handleAnalyzeImage = async (base64Image) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setRawText('');

    const response = await scanImage(base64Image, selectedProfiles);
    setLoading(false);

    if (response.error) {
      setError(response.error);
    } else {
      if (response.data.extracted_text) {
        setRawText(response.data.extracted_text);
      }
      setResult(response.data);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleProfileToggle = (profileId) => {
    setSelectedProfiles((prev) =>
      prev.includes(profileId) ? prev.filter((p) => p !== profileId) : [...prev, profileId]
    );
  };

  return (
    <div
      style={{
        display: 'flex',
        minHeight: 'calc(100vh - 64px)',
        backgroundColor: '#f8fafc',
      }}
    >
      {/* Left Panel: Upload (40%) */}
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
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '32px' }}>📷 Photo Scanner</h1>

        {/* Upload Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          style={{
            border: '2px dashed #cbd5e1',
            borderRadius: '8px',
            padding: '40px',
            textAlign: 'center',
            cursor: 'pointer',
            marginBottom: '32px',
            transition: 'all 0.2s',
            backgroundColor: imagePreview ? '#f1f5f9' : '#fafbfc',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#6366f1';
            e.currentTarget.style.backgroundColor = '#eef2ff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#cbd5e1';
            e.currentTarget.style.backgroundColor = imagePreview ? '#f1f5f9' : '#fafbfc';
          }}
        >
          <input
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            style={{ display: 'none' }}
            id="imageInput"
          />
          <label htmlFor="imageInput" style={{ cursor: 'pointer', display: 'block' }}>
            {imagePreview ? (
              <div>
                <p style={{ fontSize: '14px', fontWeight: 600, color: '#334155' }}>
                  ✅ Image selected
                </p>
                <p style={{ fontSize: '12px', color: '#64748b' }}>Click to change image</p>
              </div>
            ) : (
              <div>
                <p style={{ fontSize: '32px', marginBottom: '8px' }}>📸</p>
                <p style={{ fontSize: '14px', fontWeight: 600, color: '#334155' }}>
                  Drag image here or click to browse
                </p>
                <p style={{ fontSize: '12px', color: '#64748b' }}>
                  JPG, PNG, or WebP • Up to 10MB
                </p>
              </div>
            )}
          </label>
        </div>

        {/* Image Preview */}
        {imagePreview && (
          <div style={{ marginBottom: '32px' }}>
            <p style={{ fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '8px' }}>Preview:</p>
            <img
              src={imagePreview}
              alt="Preview"
              style={{
                width: '100%',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                maxHeight: '200px',
                objectFit: 'cover',
              }}
            />
          </div>
        )}

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

        {/* Extract Button */}
        <button
          onClick={() => imagePreview && handleAnalyzeImage(imagePreview.split(',')[1])}
          disabled={loading || !imagePreview}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: !imagePreview || loading ? '#cbd5e1' : '#6366f1',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: !imagePreview || loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            if (imagePreview && !loading) {
              e.target.style.backgroundColor = '#4f46e5';
              e.target.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseLeave={(e) => {
            if (imagePreview && !loading) {
              e.target.style.backgroundColor = '#6366f1';
              e.target.style.transform = 'translateY(0)';
            }
          }}
        >
          {loading ? '🔄 Extracting Text...' : '✨ Extract & Analyze'}
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
            <p style={{ color: '#64748b', fontSize: '16px' }}>Extracting text from image...</p>
          </div>
        )}

        {result && (
          <div>
            {/* Product Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: 700, margin: '0 0 8px 0' }}>
                  Analysis Results
                </h2>
              </div>
              {result.grade && <GradeBadge grade={result.grade} size="lg" score={result.safety_score} />}
            </div>

            {/* Raw OCR Text */}
            {rawText && (
              <div style={{ marginBottom: '32px' }}>
                <button
                  onClick={() => setShowRawText(!showRawText)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#334155',
                    cursor: 'pointer',
                    marginBottom: '12px',
                  }}
                >
                  {showRawText ? '▼ Hide Extracted Text' : '▶ Show Extracted Text'}
                </button>
                {showRawText && (
                  <div
                    style={{
                      padding: '16px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0',
                      marginBottom: '32px',
                    }}
                  >
                    <p style={{ fontSize: '12px', whiteSpace: 'pre-wrap', color: '#334155', margin: 0 }}>
                      {rawText}
                    </p>
                  </div>
                )}
              </div>
            )}

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
            <p style={{ fontSize: '16px' }}>Upload an image of an ingredient list to get started</p>
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

export default PhotoScanner;
