export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';

export const delay = (ms: number = 500) => 
  new Promise((resolve) => setTimeout(resolve, ms));
