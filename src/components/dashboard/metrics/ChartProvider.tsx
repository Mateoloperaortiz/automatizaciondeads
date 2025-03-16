
import React, { createContext, useContext, useState } from 'react';

interface ChartContextProps {
  isExpanded: boolean;
  setIsExpanded: React.Dispatch<React.SetStateAction<boolean>>;
}

const ChartContext = createContext<ChartContextProps | null>(null);

export const useChartContext = () => {
  const context = useContext(ChartContext);
  if (!context) {
    throw new Error('useChartContext must be used within a ChartProvider');
  }
  return context;
};

interface ChartProviderProps {
  children: React.ReactNode;
}

export const ChartProvider: React.FC<ChartProviderProps> = ({ children }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <ChartContext.Provider value={{ isExpanded, setIsExpanded }}>
      {children}
    </ChartContext.Provider>
  );
};
