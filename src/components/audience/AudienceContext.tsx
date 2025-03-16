
import React, { createContext, useContext, useState, useEffect } from 'react';

export interface AudienceData {
  name?: string;
  ageRange?: [number, number];
  locations?: string[];
  jobTitles?: string[];
  skills?: string[];
  education?: string[];
  experienceYears?: [number, number];
  isAdvancedTargeting?: boolean;
}

export const defaultAudience: AudienceData = {
  name: 'Tech professionals',
  ageRange: [25, 45],
  locations: ['New York', 'San Francisco', 'London'],
  jobTitles: ['Software Engineer', 'Product Manager', 'Data Scientist'],
  skills: ['React', 'Python', 'Machine Learning', 'Product Management'],
  education: ['Bachelor degree', 'Master degree'],
  experienceYears: [2, 10],
  isAdvancedTargeting: false,
};

interface AudienceContextType {
  audience: AudienceData;
  setAudience: React.Dispatch<React.SetStateAction<AudienceData>>;
  handleAddItem: (field: string, value: string) => void;
  handleRemoveItem: (field: string, index: number) => void;
}

const AudienceContext = createContext<AudienceContextType | undefined>(undefined);

export const useAudience = () => {
  const context = useContext(AudienceContext);
  if (!context) {
    throw new Error('useAudience must be used within an AudienceProvider');
  }
  return context;
};

interface AudienceProviderProps {
  initialValues?: AudienceData;
  children: React.ReactNode;
}

export const AudienceProvider: React.FC<AudienceProviderProps> = ({
  initialValues,
  children,
}) => {
  const [audience, setAudience] = useState<AudienceData>(defaultAudience);

  useEffect(() => {
    if (initialValues) {
      setAudience(prev => ({
        ...prev,
        ...initialValues
      }));
    }
  }, [initialValues]);

  const handleAddItem = (field: string, value: string) => {
    if (!value.trim()) return;
    
    setAudience((prev) => {
      const updatedArray = [...prev[field as keyof typeof prev] as string[], value];
      return {
        ...prev,
        [field]: updatedArray,
      };
    });
  };
  
  const handleRemoveItem = (field: string, index: number) => {
    setAudience((prev) => {
      const updatedArray = [...prev[field as keyof typeof prev] as string[]];
      updatedArray.splice(index, 1);
      return {
        ...prev,
        [field]: updatedArray,
      };
    });
  };

  return (
    <AudienceContext.Provider
      value={{
        audience,
        setAudience,
        handleAddItem,
        handleRemoveItem
      }}
    >
      {children}
    </AudienceContext.Provider>
  );
};
