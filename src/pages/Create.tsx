
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Create: React.FC = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Redirect to the create-campaign page
    navigate('/create-campaign');
  }, [navigate]);
  
  return (
    // Simple loading state while redirecting
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-muted-foreground">Redirecting to campaign creation...</p>
    </div>
  );
};

export default Create;
