import '@testing-library/jest-dom';

// Polyfill ResizeObserver for JSDOM / Vitest testing environment with React Three Fiber
if (typeof window !== 'undefined' && !window.ResizeObserver) {
  window.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// Suppress React Router warnings in testing console
const originalWarn = console.warn;
console.warn = (...args: any[]) => {
  if (args[0] && typeof args[0] === 'string' && args[0].includes('React Router Future Flag Warning')) {
    return;
  }
  originalWarn(...args);
};
