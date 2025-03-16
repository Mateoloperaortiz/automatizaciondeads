
import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';
import { useAudience } from './AudienceContext';

interface TagInputProps {
  field: string;
  placeholder: string;
  items: string[];
}

const TagInput: React.FC<TagInputProps> = ({ field, placeholder, items }) => {
  const [newItem, setNewItem] = useState('');
  const { handleAddItem, handleRemoveItem } = useAudience();
  
  return (
    <div className="space-y-4">
      <div className="flex space-x-2">
        <Input
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          placeholder={placeholder}
          className="flex-1"
        />
        <Button
          onClick={() => {
            handleAddItem(field, newItem);
            setNewItem('');
          }}
          className="shrink-0"
        >
          Add
        </Button>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {items.map((item, index) => (
          <Badge 
            key={index} 
            variant="secondary"
            className="pl-2 pr-1 py-1 flex items-center space-x-1"
          >
            <span>{item}</span>
            <Button
              variant="ghost"
              size="icon"
              className="h-4 w-4 rounded-full"
              onClick={() => handleRemoveItem(field, index)}
            >
              <X className="h-2 w-2" />
            </Button>
          </Badge>
        ))}
      </div>
    </div>
  );
};

export default TagInput;
