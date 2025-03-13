import { useState, useCallback } from 'react';
import { SocialPlatform } from '../api-integrations/types';
import { ApiErrorDetail } from '../api-integrations/types';

export interface ApiErrorState {
  hasError: boolean;
  error?: ApiErrorDetail;
  loading: boolean;
  retry: () => Promise<void>;
  clearError: () => void;
}

/**
 * Hook para gestionar errores de API en componentes React
 */
export function useApiError(
  platform?: SocialPlatform,
  onErrorCallback?: (error: ApiErrorDetail) => void
): ApiErrorState & {
  setError: (error: ApiErrorDetail | Error | string | null) => void;
  startLoading: () => void;
  stopLoading: () => void;
  withErrorHandling: <T>(promise: Promise<T>) => Promise<T>;
} {
  const [state, setState] = useState<{
    hasError: boolean;
    error?: ApiErrorDetail;
    loading: boolean;
    lastAction?: () => Promise<any>;
  }>({
    hasError: false,
    loading: false
  });
  
  /**
   * Establece el error
   */
  const setError = useCallback((error: ApiErrorDetail | Error | string | null) => {
    if (!error) {
      setState(prev => ({ ...prev, hasError: false, error: undefined }));
      return;
    }
    
    // Convertir diferentes tipos de error al formato estándar
    let formattedError: ApiErrorDetail;
    
    if (typeof error === 'string') {
      formattedError = {
        code: 'API_ERROR',
        message: error,
        platform: platform || 'meta'
      };
    } else if (error instanceof Error) {
      formattedError = {
        code: 'API_ERROR',
        message: error.message,
        platform: platform || 'meta',
        originalError: error
      };
    } else {
      formattedError = error;
    }
    
    setState(prev => ({ ...prev, hasError: true, error: formattedError }));
    
    // Llamar al callback si está definido
    if (onErrorCallback) {
      onErrorCallback(formattedError);
    }
  }, [platform, onErrorCallback]);
  
  /**
   * Limpia el error
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, hasError: false, error: undefined }));
  }, []);
  
  /**
   * Activa el estado de carga
   */
  const startLoading = useCallback(() => {
    setState(prev => ({ ...prev, loading: true }));
  }, []);
  
  /**
   * Desactiva el estado de carga
   */
  const stopLoading = useCallback(() => {
    setState(prev => ({ ...prev, loading: false }));
  }, []);
  
  /**
   * Reintenta la última acción
   */
  const retry = useCallback(async () => {
    if (!state.lastAction) return;
    
    clearError();
    startLoading();
    
    try {
      await state.lastAction();
    } catch (error) {
      setError(error as ApiErrorDetail | Error);
    } finally {
      stopLoading();
    }
  }, [state.lastAction, clearError, startLoading, stopLoading, setError]);
  
  /**
   * Helper para manejar errores en promesas
   */
  const withErrorHandling = useCallback(
    async <T>(promise: Promise<T>): Promise<T> => {
      // Guardar la promesa como última acción
      setState(prev => ({
        ...prev,
        lastAction: () => promise,
        loading: true,
        hasError: false,
        error: undefined
      }));
      
      try {
        const result = await promise;
        setState(prev => ({ ...prev, loading: false }));
        return result;
      } catch (error) {
        setError(error as ApiErrorDetail | Error);
        setState(prev => ({ ...prev, loading: false }));
        throw error;
      }
    },
    [setError]
  );
  
  return {
    hasError: state.hasError,
    error: state.error,
    loading: state.loading,
    retry,
    clearError,
    setError,
    startLoading,
    stopLoading,
    withErrorHandling
  };
}