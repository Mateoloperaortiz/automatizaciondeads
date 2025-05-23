import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

// Define types for the audience primitives from Python service
interface AudiencePrimitive {
    category: string;
    value: string;
    confidence?: number;
}

// Define type for the structure of audience_taxonomy.yaml
interface AudienceTaxonomy {
    industry_map: Record<string, string>;
    skill_categories: Record<string, string[]>; // Category name to list of raw skill strings
    location_map: Record<string, string>;
    seniority_map: Record<string, string>;
    fallback_audience: {
        industries?: string[];
        skills?: string[];
        locations?: string[];
        seniority?: string[];
    };
}

// Define the structure of the platform-agnostic targeting parameters output
export interface PlatformAgnosticTargeting {
    industries: string[];      // Standardized industry codes (e.g., ["TECH_SOFTWARE_DEV"])
    skillKeywords: string[];   // Raw skill keywords, or categorized skill codes
    locations: string[];       // Standardized location codes (e.g., ["LOCATION_REMOTE", "COUNTRY_US"])
    seniority: string[];       // Standardized seniority codes (e.g., ["SENIORITY_SENIOR"])
    // Add other common fields like interests, behaviors if applicable across platforms
}

let _taxonomy: AudienceTaxonomy | null = null;

function loadTaxonomy(): AudienceTaxonomy {
    if (_taxonomy) {
        return _taxonomy;
    }
    try {
        const taxonomyPath = path.join(process.cwd(), 'lib/automation/audience_taxonomy.yaml');
        const fileContents = fs.readFileSync(taxonomyPath, 'utf8');
        const loadedYaml = yaml.load(fileContents) as AudienceTaxonomy;
        if (!loadedYaml) {
            throw new Error('Taxonomy YAML is empty or invalid.');
        }
        _taxonomy = loadedYaml;
        console.log('Audience taxonomy loaded successfully.');
        return _taxonomy;
    } catch (e) {
        console.error('Failed to load audience_taxonomy.yaml:', e);
        // Fallback to a minimal default if loading fails to prevent crashes
        // In production, you might want to raise an error or have a more robust default
        _taxonomy = {
            industry_map: {}, skill_categories: {}, location_map: {}, seniority_map: {},
            fallback_audience: { industries: ['GENERAL_INDUSTRY'], locations: ['COUNTRY_US'] }
        };
        return _taxonomy;
    }
}

// Ensure taxonomy is loaded on module initialization
loadTaxonomy();

const LOW_CONFIDENCE_THRESHOLD = 0.25; // Match the threshold used in engine.ts

export function mapAudiencePrimitivesToTargeting(
    primitives: AudiencePrimitive[],
    segmentationConfidence?: number // e.g., cluster_assignment_confidence from Python service
): PlatformAgnosticTargeting {
    const taxonomy = loadTaxonomy(); // Get cached or load taxonomy

    if (segmentationConfidence !== undefined && segmentationConfidence < LOW_CONFIDENCE_THRESHOLD) {
        console.log(`Low segmentation confidence (${segmentationConfidence}), using fallback audience.`);
        return {
            industries: taxonomy.fallback_audience.industries || [],
            skillKeywords: taxonomy.fallback_audience.skills || [],
            locations: taxonomy.fallback_audience.locations || [],
            seniority: taxonomy.fallback_audience.seniority || [],
        };
    }

    const targeting: PlatformAgnosticTargeting = {
        industries: [],
        skillKeywords: [],
        locations: [],
        seniority: [],
    };

    for (const primitive of primitives) {
        switch (primitive.category.toLowerCase()) {
            case 'industry':
                if (taxonomy.industry_map[primitive.value]) {
                    targeting.industries.push(taxonomy.industry_map[primitive.value]);
                } else {
                    console.warn(`Unmapped industry: ${primitive.value}. Consider adding to taxonomy.`);
                    // Optionally add a general fallback if no direct map
                    if (taxonomy.industry_map['General'] && !targeting.industries.includes(taxonomy.industry_map['General'])) {
                        targeting.industries.push(taxonomy.industry_map['General']);
                    }
                }
                break;
            case 'skill_keyword':
                // For skills, we might pass them through directly or categorize them.
                // The current YAML has skill_categories, but this mapper just passes through for simplicity.
                // You could extend this to map to skill category codes if desired.
                targeting.skillKeywords.push(primitive.value);
                break;
            case 'location':
                if (taxonomy.location_map[primitive.value]) {
                    targeting.locations.push(taxonomy.location_map[primitive.value]);
                } else {
                    console.warn(`Unmapped location: ${primitive.value}. Consider adding to taxonomy.`);
                }
                break;
            case 'seniority':
                if (taxonomy.seniority_map[primitive.value]) {
                    targeting.seniority.push(taxonomy.seniority_map[primitive.value]);
                } else {
                    console.warn(`Unmapped seniority: ${primitive.value}. Consider adding to taxonomy.`);
                }
                break;
            default:
                console.warn(`Unknown audience primitive category: ${primitive.category}`);
        }
    }

    // Ensure unique values if multiple primitives mapped to the same code
    targeting.industries = [...new Set(targeting.industries)];
    targeting.skillKeywords = [...new Set(targeting.skillKeywords)];
    targeting.locations = [...new Set(targeting.locations)];
    targeting.seniority = [...new Set(targeting.seniority)];

    // If no specific targeting could be derived but confidence was high, use fallback.
    // This handles cases where primitives were empty or all unmapped.
    if (targeting.industries.length === 0 && targeting.skillKeywords.length === 0 && targeting.locations.length === 0 && targeting.seniority.length === 0) {
        console.log('No specific targeting derived despite acceptable confidence, using fallback audience.');
        return {
            industries: taxonomy.fallback_audience.industries || [],
            skillKeywords: taxonomy.fallback_audience.skills || [],
            locations: taxonomy.fallback_audience.locations || [],
            seniority: taxonomy.fallback_audience.seniority || [],
        };
    }

    // If we have some targeting but no locations, add default location
    if (targeting.locations.length === 0 && taxonomy.fallback_audience.locations) {
        targeting.locations = taxonomy.fallback_audience.locations;
    }

    return targeting;
} 