import React from 'react';
import { ApiErrorDetail } from '@/lib/api-integrations/types';
import { cn } from '@/lib/utils';

interface ApiErrorProps {
  error: ApiErrorDetail;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
  compact?: boolean;
}

/**
 * Componente para mostrar errores de API con estilos y acciones
 */
export function ApiError({
  error,
  onRetry,
  onDismiss,
  className,
  compact = false
}: ApiErrorProps) {
  // Determinar tipo de error para mostrar icono y estilo adecuados
  const isAuthError = 
    error.statusCode === 401 || 
    error.statusCode === 403 ||
    error.code?.includes('AUTH') ||
    error.code?.includes('TOKEN');
  
  const isRateLimit = 
    error.statusCode === 429 ||
    error.code?.includes('RATE') || 
    error.rateLimited;
  
  const isNetworkError = 
    error.code?.includes('NETWORK') ||
    (error.message && (
      error.message.includes('network') || 
      error.message.includes('conexión') || 
      error.message.includes('timeout')
    ));
  
  // Determinar tipo de error
  let errorType = 'Error';
  let errorIcon = 'x-circle';
  let colorClass = 'border-red-400 bg-red-50 text-red-800';
  
  if (isAuthError) {
    errorType = 'Error de autenticación';
    errorIcon = 'lock';
    colorClass = 'border-amber-400 bg-amber-50 text-amber-800';
  } else if (isRateLimit) {
    errorType = 'Límite de peticiones';
    errorIcon = 'clock';
    colorClass = 'border-amber-400 bg-amber-50 text-amber-800';
  } else if (isNetworkError) {
    errorType = 'Error de red';
    errorIcon = 'wifi-off';
    colorClass = 'border-amber-400 bg-amber-50 text-amber-800';
  }
  
  // Mensaje amigable basado en el tipo de error
  const errorMessage = error.message || 'Ha ocurrido un error inesperado.';
  let actionMessage = '';
  
  if (isAuthError) {
    actionMessage = 'Por favor, vuelva a autenticarse con la plataforma.';
  } else if (isRateLimit) {
    actionMessage = 'Por favor, espere un momento antes de intentarlo nuevamente.';
  } else if (error.retryable) {
    actionMessage = 'Puede intentar nuevamente la operación.';
  }
  
  // Version compacta (para inline)
  if (compact) {
    return (
      <div className={cn(
        'text-sm rounded-md p-2 flex items-center gap-2',
        colorClass,
        className
      )}>
        <span className="flex-shrink-0">
          <svg 
            className="h-4 w-4" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
            />
          </svg>
        </span>
        <span>{errorMessage}</span>
        {onRetry && error.retryable && (
          <button 
            type="button" 
            onClick={onRetry}
            className="ml-auto text-xs font-medium underline"
          >
            Reintentar
          </button>
        )}
      </div>
    );
  }
  
  // Versión completa
  return (
    <div className={cn(
      'p-4 border-l-4 rounded-md',
      colorClass,
      className
    )}>
      <div className="flex">
        <div className="flex-shrink-0">
          <svg 
            className="h-5 w-5" 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 20 20" 
            fill="currentColor"
          >
            <path 
              fillRule="evenodd" 
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" 
              clipRule="evenodd" 
            />
          </svg>
        </div>
        <div className="ml-3">
          <div className="flex items-center">
            <h3 className="text-sm font-medium">
              {errorType} {error.platform && `en ${error.platform}`}
              {error.code && <span className="text-xs ml-1 opacity-75">({error.code})</span>}
            </h3>
            {onDismiss && (
              <button 
                type="button" 
                className="ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                onClick={onDismiss}
              >
                <span className="sr-only">Cerrar</span>
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path>
                </svg>
              </button>
            )}
          </div>
          <div className="mt-2 text-sm">
            <p>{errorMessage}</p>
            {actionMessage && <p className="mt-1">{actionMessage}</p>}
          </div>
          {(onRetry && error.retryable) && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Reintentar
              </button>
            </div>
          )}
          {error.statusCode && (
            <div className="mt-2 text-xs opacity-75">
              Código de estado: {error.statusCode}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Componente para mostrar múltiples errores de API
 */
export function ApiErrorList({
  errors,
  onRetry,
  onDismiss,
  className
}: {
  errors: ApiErrorDetail[];
  onRetry?: (error: ApiErrorDetail, index: number) => void;
  onDismiss?: (error: ApiErrorDetail, index: number) => void;
  className?: string;
}) {
  if (!errors || errors.length === 0) return null;
  
  return (
    <div className={cn('space-y-2', className)}>
      {errors.map((error, index) => (
        <ApiError
          key={`${error.code}-${index}`}
          error={error}
          onRetry={onRetry ? () => onRetry(error, index) : undefined}
          onDismiss={onDismiss ? () => onDismiss(error, index) : undefined}
        />
      ))}
    </div>
  );
}