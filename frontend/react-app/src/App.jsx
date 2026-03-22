import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { createContext, useState } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import BarcodeScanner from './pages/BarcodeScanner';
import IngredientChecker from './pages/IngredientChecker';
import PhotoScanner from './pages/PhotoScanner';
import './index.css';

export const ProfileContext = createContext();

function AppContent() {
  const [selectedProfiles, setSelectedProfiles] = useState([]);

  const profiles = [
    { id: 'SENSITIVE_SKIN', label: '😢 Sensitive Skin' },
    { id: 'PREGNANT', label: '🤰 Pregnant' },
    { id: 'DIABETIC', label: '🩺 Diabetic' },
    { id: 'VEGAN', label: '🌱 Vegan' },
    { id: 'NUT_ALLERGY', label: '🥜 Nut Allergy' },
    { id: 'FRAGRANCE_ALLERGY', label: '👃 Fragrance Allergy' },
    { id: 'ACNE_PRONE', label: '🧴 Acne-Prone' },
  ];

  return (
    <ProfileContext.Provider value={{ selectedProfiles, setSelectedProfiles, profiles }}>
      <Navbar />
      <div style={{ paddingTop: '64px' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/barcode" element={<BarcodeScanner />} />
          <Route path="/ingredients" element={<IngredientChecker />} />
          <Route path="/photo" element={<PhotoScanner />} />
        </Routes>
      </div>
    </ProfileContext.Provider>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
