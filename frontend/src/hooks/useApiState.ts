import { useState, useCallback } from 'react';
import { getFarmerFriendlyMessage } from '../utils/errorMessages';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApiState<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const run = useCallback(async (promise: Promise<T>): Promise<T | null> => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await promise;
      setState({ data, loading: false, error: null });
      return data;
    } catch (err: any) {
      const status = err?.response?.status;
      const code = err?.response?.data?.error?.code || err?.code || (status === 404 ? 'NOT_FOUND' : 'UNKNOWN_ERROR');
      const rawMessage = err?.response?.data?.error?.message || err?.message || '';
      
      let friendlyMessage: string;
      if (rawMessage && !rawMessage.includes('server is unavailable') && !rawMessage.includes('unexpected error') && !rawMessage.includes("couldn't reach")) {
        friendlyMessage = rawMessage;
      } else {
        friendlyMessage = getFarmerFriendlyMessage(code, status);
      }
      
      setState({ data: null, loading: false, error: friendlyMessage });
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  const setData = useCallback((data: T | null) => {
    setState(s => ({ ...s, data }));
  }, []);

  return {
    ...state,
    run,
    reset,
    setData,
  };
}
