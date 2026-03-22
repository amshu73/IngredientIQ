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

export const analyzeIngredients = async (ingredientList, profiles = []) => {
  const ingredients = ingredientList
    .split(',')
    .map((ing) => ing.trim())
    .filter((ing) => ing.length > 0);

  const results = [];
  let safeCount = 0;
  let moderateCount = 0;
  let hazardousCount = 0;

  for (const ingredient of ingredients) {
    const result = await getIngredient(ingredient);
    if (result.data) {
      results.push({
        ...result.data,
        original_input: ingredient,
      });

      const hazardLevel = result.data.hazard_level;
      if (hazardLevel === 'SAFE') safeCount++;
      else if (hazardLevel === 'MODERATE') moderateCount++;
      else if (hazardLevel === 'HAZARDOUS') hazardousCount++;
    }
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
