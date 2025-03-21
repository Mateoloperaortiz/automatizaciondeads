
import { simulateNetworkDelay } from './mockDatabase';

interface OptimizationResult {
  optimizedDescription: string;
  suggestions: {
    category: string;
    suggestion: string;
  }[];
  improvements: string[];
}

const platformSpecificTips = {
  linkedin: [
    "Use industry-specific keywords for LinkedIn's algorithm",
    "Highlight company culture and values",
    "Include specific benefits that appeal to professionals",
    "Mention growth opportunities explicitly"
  ],
  indeed: [
    "Keep descriptions concise for mobile readers",
    "Include salary range for better visibility",
    "Use bullet points for easy scanning",
    "Be specific about day-to-day responsibilities"
  ],
  glassdoor: [
    "Highlight company ratings and reviews",
    "Address work-life balance explicitly",
    "Include detailed benefits information",
    "Showcase diversity and inclusion initiatives"
  ]
};

export const optimizeJobDescription = async (
  description: string,
  requirements: string,
  platforms: string[] = ['linkedin', 'indeed', 'glassdoor']
): Promise<OptimizationResult> => {
  // Simulate an API call delay
  await simulateNetworkDelay(2000);
  
  // In a real implementation, this would call an NLP service
  // For now, we'll provide a mock optimization based on common practices
  
  const keywordsToInclude = [
    'collaborative', 'innovative', 'flexible',
    'growth', 'development', 'competitive', 'benefits',
    'inclusive', 'diverse', 'remote', 'hybrid'
  ];
  
  const phrasesToAvoid = [
    'ninja', 'rockstar', 'superstar', 'guru',
    'young', 'energetic', 'mature',
    'male', 'female', 'man', 'woman'
  ];
  
  // Generate mock improvements based on description analysis
  const improvements: string[] = [];
  
  // Check description length
  if (description.length < 300) {
    improvements.push("Added more details to make the description comprehensive");
  } else if (description.length > 1000) {
    improvements.push("Condensed lengthy sections while preserving key information");
  }
  
  // Check for keywords
  const missingKeywords = keywordsToInclude.filter(
    keyword => !description.toLowerCase().includes(keyword.toLowerCase())
  );
  
  if (missingKeywords.length > 0) {
    improvements.push(`Added key terms to improve searchability: ${missingKeywords.slice(0, 3).join(', ')}${missingKeywords.length > 3 ? '...' : ''}`);
  }
  
  // Check for problematic phrases
  const problematicPhrases = phrasesToAvoid.filter(
    phrase => description.toLowerCase().includes(phrase.toLowerCase())
  );
  
  if (problematicPhrases.length > 0) {
    improvements.push(`Replaced potentially biased or unprofessional terms: ${problematicPhrases.join(', ')}`);
  }
  
  // Check for structure
  if (!description.includes('•') && !description.includes('-')) {
    improvements.push("Added bullet points for better readability");
  }
  
  if (!description.toLowerCase().includes('benefit') && !description.toLowerCase().includes('offer')) {
    improvements.push("Added a benefits section to increase candidate interest");
  }
  
  if (!description.toLowerCase().includes('about') && !description.toLowerCase().includes('our company')) {
    improvements.push("Added a company introduction to establish brand connection");
  }
  
  // Generate platform-specific suggestions
  const suggestions = platforms.map(platform => {
    const tips = platformSpecificTips[platform as keyof typeof platformSpecificTips] || [];
    return {
      category: `${platform.charAt(0).toUpperCase() + platform.slice(1)} Optimization`,
      suggestion: tips[Math.floor(Math.random() * tips.length)] || 
        "Optimize your posting for this platform's specific algorithm and audience"
    };
  });
  
  // Add general suggestions
  suggestions.push({
    category: "Language & Tone",
    suggestion: "Used inclusive language and an engaging, conversational tone to attract diverse candidates"
  });
  
  suggestions.push({
    category: "Structure & Formatting",
    suggestion: "Improved formatting with clear sections, bullet points, and scannable content"
  });
  
  // Generate optimized description
  let optimizedDescription = description;
  
  // Simulate improvements (in a real app, we'd use NLP to actually improve the text)
  if (!optimizedDescription.includes('About Us') && !optimizedDescription.includes('About Our Company')) {
    optimizedDescription = `About Our Company:\nWe're a collaborative and innovative team focused on making a meaningful impact. We value diversity and inclusion in our workplace.\n\n${optimizedDescription}`;
  }
  
  if (!optimizedDescription.includes('Benefits') && !optimizedDescription.includes('We offer')) {
    optimizedDescription = `${optimizedDescription}\n\nBenefits & Perks:\n• Competitive salary and equity options\n• Flexible work arrangements (remote/hybrid available)\n• Comprehensive health, dental, and vision insurance\n• Professional development opportunities\n• Collaborative and inclusive work environment`;
  }
  
  if (!optimizedDescription.includes('•') && !optimizedDescription.includes('-')) {
    const paragraphs = optimizedDescription.split('\n\n');
    for (let i = 0; i < paragraphs.length; i++) {
      if (paragraphs[i].length > 100 && !paragraphs[i].includes('•') && !paragraphs[i].includes(':')) {
        const sentences = paragraphs[i].split('. ').filter(s => s.trim().length > 0);
        if (sentences.length > 2) {
          paragraphs[i] = `${sentences[0]}.\n\n${sentences.slice(1).map(s => `• ${s}${!s.endsWith('.') ? '.' : ''}`).join('\n')}`;
        }
      }
    }
    optimizedDescription = paragraphs.join('\n\n');
  }

  // In a real implementation, this would be handled by an AI service
  // to generate truly optimized content
  
  return {
    optimizedDescription,
    suggestions,
    improvements: improvements.length > 0 ? improvements : ["Refined language for clarity and impact"]
  };
};
