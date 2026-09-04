import axios, { AxiosError } from 'axios';
import type { AppError } from '../types/api';

const getBaseUrl = () => {
  const envUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL) as string | undefined;
  if (envUrl !== undefined && envUrl !== '') {
    return envUrl;
  }
  if (import.meta.env.MODE === 'test') {
    return 'http://127.0.0.1:8000';
  }
  if (typeof window !== 'undefined' && window.location && window.location.port === '8000') {
    return '';
  }
  if (typeof window !== 'undefined' && window.location && window.location.origin) {
    return 'http://127.0.0.1:8000';
  }
  return 'http://127.0.0.1:8000';
};

const apiClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    let appError: AppError & { status?: number; response?: any } = {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred.'
    };

    if (error.response) {
      const data = error.response.data as any;
      const statusCode = error.response.status;
      appError.status = statusCode;
      appError.response = error.response;

      if (data && data.error) {
        let msg = data.error.message || 'An unexpected error occurred.';
        if (Array.isArray(data.error.details) && data.error.details.length > 0) {
          const detailMsgs = data.error.details
            .map((d: any) => (typeof d === 'string' ? d : d?.message || d?.field))
            .filter(Boolean);
          if (detailMsgs.length > 0) {
            msg = `${msg} (${detailMsgs.join('; ')})`;
          }
        }
        appError.code = data.error.code || (statusCode === 401 ? 'UNAUTHORIZED' : statusCode === 403 ? 'FORBIDDEN' : 'CLIENT_ERROR');
        appError.message = msg;
        appError.details = data.error.details;
      } else if (data && typeof data.detail === 'string') {
        appError.code = statusCode === 401 ? 'UNAUTHORIZED' : statusCode === 403 ? 'FORBIDDEN' : statusCode === 422 ? 'VALIDATION_ERROR' : 'CLIENT_ERROR';
        appError.message = data.detail;
      } else if (data && Array.isArray(data.detail) && data.detail.length > 0) {
        const msgs = data.detail.map((d: any) => d?.msg || d?.message || JSON.stringify(d));
        appError.code = 'VALIDATION_ERROR';
        appError.message = msgs.join('; ');
        appError.details = data.detail;
      } else if (data && typeof data.message === 'string') {
        appError.code = statusCode === 401 ? 'UNAUTHORIZED' : statusCode === 403 ? 'FORBIDDEN' : 'CLIENT_ERROR';
        appError.message = data.message;
      } else if (statusCode === 401) {
        appError.code = 'UNAUTHORIZED';
        appError.message = 'Incorrect username or password.';
      } else if (statusCode === 403) {
        appError.code = 'FORBIDDEN';
        appError.message = 'Account does not have permission.';
      } else if (statusCode === 400) {
        appError.code = 'CLIENT_ERROR';
        appError.message = typeof data === 'string' ? data : 'Bad request.';
      } else if (statusCode === 422) {
        appError.code = 'VALIDATION_ERROR';
        appError.message = 'Validation error occurred.';
      } else if (statusCode === 500) {
        appError.code = 'SERVER_ERROR';
        appError.message = 'Something went wrong on the CropShift service.';
      } else {
        appError.code = statusCode >= 500 ? 'SERVER_ERROR' : 'CLIENT_ERROR';
        appError.message = `Request failed with status ${statusCode}`;
      }
    } else if (!error.response && (error.request || error.code === 'ERR_NETWORK')) {
      appError.status = 0;
      appError.code = 'NETWORK_ERROR';
      appError.message = 'CropShift services are currently unreachable. Please check that backend service is running.';
    } else {
      appError.code = 'CLIENT_ERROR';
      appError.message = error.message || 'A client-side error occurred.';
    }

    return Promise.reject(appError);
  }
);

export default apiClient;
export { AxiosError };
