import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const handleResponse = async (promise) => {
  const startTime = performance.now();
  try {
    const response = await promise;
    const duration = performance.now() - startTime;
    return {
      data: response.data,
      status: response.status,
      error: null,
      duration: Math.round(duration),
    };
  } catch (error) {
    const duration = performance.now() - startTime;
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
    return {
      data: null,
      status: error.response?.status || 500,
      error: errorMsg,
      duration: Math.round(duration),
    };
  }
};

export const checkHealth = () =>
  handleResponse(client.get('/health'));

export const getProfiles = () =>
  handleResponse(client.get('/profiles'));

export const getGrades = () =>
  handleResponse(client.get('/grades'));

export const getIngredient = (name) =>
  handleResponse(client.get(`/ingredient/${encodeURIComponent(name)}`));

export const scanBarcode = (barcode, profiles = []) =>
  handleResponse(
    client.post('/scan/barcode', {
      barcode,
      user_profiles: profiles,
    })
  );

export const scanImage = (base64, profiles = []) =>
  handleResponse(
    client.post('/scan/image', {
      image_base64: base64,
      user_profiles: profiles,
    })
  );

export const getIngredientsBatch = (ingredientNames) =>
  handleResponse(client.post('/ingredients/batch', ingredientNames));

export const analyzeIngredients = async (ingredientList, profiles = []) => {
  const ingredients = ingredientList
    .split(',')
    .map((ing) => ing.trim())
    .filter((ing) => ing.length > 0);

  // Use batch endpoint to avoid N+1 API calls
  const batchResult = await getIngredientsBatch(ingredients);
  
  if (batchResult.error || !batchResult.data) {
    return {
      data: null,
      status: batchResult.status,
      error: batchResult.error || 'Failed to analyze ingredients',
    };
  }

  const results = batchResult.data.results || [];
  let safeCount = 0;
  let moderateCount = 0;
  let hazardousCount = 0;

  for (const ingredient of results) {
    const safetyLabel = ingredient.safety_label;
    if (safetyLabel === 'SAFE') safeCount++;
    else if (safetyLabel === 'MODERATE') moderateCount++;
    else if (safetyLabel === 'HAZARDOUS') hazardousCount++;
  }

  return {
    data: {
      ingredients: results,
      summary: {
        total: ingredients.length,
        safe: safeCount,
        moderate: moderateCount,
        hazardous: hazardousCount,
      },
    },
    status: 200,
    error: null,
  };
};

export default client;
