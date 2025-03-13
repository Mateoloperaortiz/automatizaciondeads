import React, { Component, ErrorInfo, ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Componente que captura errores en la interfaz de usuario y muestra un mensaje amigable
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Registrar el error
    console.error('Error capturado por ErrorBoundary:', error, errorInfo);
    
    // Llamar al callback onError si está definido
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // Mostrar el fallback personalizado o el mensaje por defecto
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      return (
        <div className="p-4 bg-red-50 border-l-4 border-red-400 rounded">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg 
                className="h-5 w-5 text-red-400" 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 20 20" 
                fill="currentColor" 
                aria-hidden="true"
              >
                <path 
                  fillRule="evenodd" 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                  clipRule="evenodd" 
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Se ha producido un error
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  Lo sentimos, ha ocurrido un error al procesar su solicitud. Por favor, intente de nuevo más tarde.
                </p>
                {process.env.NODE_ENV === 'development' && (
                  <details className="mt-2 bg-gray-50 p-2 rounded">
                    <summary className="font-mono text-xs">Detalles del error</summary>
                    <pre className="mt-2 text-xs overflow-auto">{this.state.error?.toString()}</pre>
                  </details>
                )}
              </div>
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => this.setState({ hasError: false, error: null })}
                  className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Intentar nuevamente
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

/**
 * Componente específico para errores de API
 */
export const ApiErrorDisplay: React.FC<{ 
  error: {
    code?: string;
    message?: string;
    platform?: string;
    statusCode?: number;
    retryable?: boolean;
  }; 
  onRetry?: () => void;
}> = ({ error, onRetry }) => {
  // Determinar si es un error de autenticación
  const isAuthError = error.statusCode === 401 || error.statusCode === 403 || 
    error.code?.includes('AUTH') || error.code?.includes('TOKEN');
  
  // Mensaje amigable basado en el tipo de error
  let errorMessage = error.message || 'Ha ocurrido un error al procesar la solicitud.';
  let actionMessage = '';
  
  if (isAuthError) {
    actionMessage = 'Por favor, vuelva a autenticarse con la plataforma.';
  } else if (error.code?.includes('RATE_LIMIT')) {
    actionMessage = 'Por favor, espere un momento antes de intentarlo nuevamente.';
  } else if (error.retryable) {
    actionMessage = 'Puede intentar nuevamente la operación.';
  }
  
  return (
    <div className="p-4 bg-red-50 border-l-4 border-red-400 rounded">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg 
            className="h-5 w-5 text-red-400" 
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
          <h3 className="text-sm font-medium text-red-800">
            Error {error.platform && `en ${error.platform}`}
            {error.code && <span className="text-xs ml-1">({error.code})</span>}
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{errorMessage}</p>
            {actionMessage && <p className="mt-1">{actionMessage}</p>}
          </div>
          {onRetry && error.retryable && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Reintentar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Hook para manejar errores de API
 */
export const useApiError = () => {
  const [error, setError] = React.useState<{
    code?: string;
    message?: string;
    platform?: string;
    statusCode?: number;
    retryable?: boolean;
  } | null>(null);
  
  const clearError = () => setError(null);
  
  return {
    error,
    setError,
    clearError,
    hasError: !!error,
  };
};