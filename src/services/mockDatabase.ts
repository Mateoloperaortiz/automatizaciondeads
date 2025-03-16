
// Mock database to persist data across service files
export const campaignDatabase: Record<string, any> = {
  "camp-001": {
    id: "camp-001",
    title: "Senior Frontend Developer",
    status: "active",
    platform: "Meta, LinkedIn, Google",
    createdDate: "May 15, 2023",
    jobDetails: {
      title: "Senior Frontend Developer",
      company: "Magneto",
      location: "San Francisco, CA",
      jobType: "full-time",
      salary: "$120,000 - $150,000",
      applicationUrl: "https://careers.magneto.com/frontend-dev",
      description: "We are looking for a Senior Frontend Developer to join our team and help build innovative web applications. The ideal candidate will have extensive experience with React, TypeScript, and modern frontend architecture.",
      requirements: "5+ years of experience with JavaScript and frontend frameworks (React preferred)\nStrong understanding of TypeScript\nExperience with state management solutions\nFamiliarity with modern build tools and CI/CD pipelines\nBachelor's degree in Computer Science or related field"
    },
    platforms: ["meta", "linkedin", "google"],
    audience: {
      name: "Experienced frontend developers",
      ageRange: [25, 45],
      experienceYears: [5, 15],
      locations: ["San Francisco", "New York", "Remote"],
      jobTitles: ["Frontend Developer", "UI Developer", "JavaScript Developer"],
      skills: ["React", "TypeScript", "JavaScript", "HTML/CSS", "Redux"]
    }
  },
  "camp-002": {
    id: "camp-002",
    title: "UX/UI Designer",
    status: "active",
    platform: "LinkedIn, Twitter",
    createdDate: "May 18, 2023",
    jobDetails: {
      title: "UX/UI Designer",
      company: "Magneto",
      location: "Remote",
      jobType: "full-time",
      salary: "$90,000 - $120,000",
      applicationUrl: "https://careers.magneto.com/ux-designer",
      description: "Join our product team as a UX/UI Designer and help create beautiful, intuitive user experiences. You'll work closely with product managers, developers, and other stakeholders to design features that delight our users.",
      requirements: "3+ years of experience in UX/UI design\nProficiency in design tools like Figma or Adobe XD\nExperience conducting user research and usability testing\nStrong portfolio showcasing your design process\nExcellent communication and collaboration skills"
    },
    platforms: ["linkedin", "twitter"],
    audience: {
      name: "UX/UI Designers",
      ageRange: [22, 40],
      experienceYears: [3, 10],
      locations: ["New York", "Los Angeles", "Remote"],
      jobTitles: ["UX Designer", "UI Designer", "Product Designer"],
      skills: ["Figma", "User Research", "Wireframing", "Prototyping", "Visual Design"]
    }
  },
  "camp-003": {
    id: "camp-003",
    title: "Product Manager",
    status: "active",
    platform: "Meta, LinkedIn",
    createdDate: "May 12, 2023",
    jobDetails: {
      title: "Product Manager",
      company: "Magneto",
      location: "Chicago, IL",
      jobType: "full-time",
      salary: "$110,000 - $140,000",
      applicationUrl: "https://careers.magneto.com/product-manager",
      description: "We're seeking a Product Manager to drive the strategy and execution of our core products. You'll work with cross-functional teams to identify opportunities, define requirements, and deliver features that solve real customer problems.",
      requirements: "4+ years of product management experience\nProven track record of shipping successful products\nStrong analytical skills and data-driven decision making\nExcellent communication and stakeholder management\nTechnical background preferred"
    },
    platforms: ["meta", "linkedin"],
    audience: {
      name: "Product Managers",
      ageRange: [28, 45],
      experienceYears: [4, 12],
      locations: ["Chicago", "Boston", "Remote"],
      jobTitles: ["Product Manager", "Technical Product Manager", "Product Owner"],
      skills: ["Product Strategy", "Agile Methodologies", "User Stories", "Market Analysis", "Roadmapping"]
    }
  },
  "camp-004": {
    id: "camp-004",
    title: "Full Stack Developer",
    status: "ended",
    platform: "Meta, LinkedIn, Google",
    createdDate: "April 28, 2023",
    jobDetails: {
      title: "Full Stack Developer",
      company: "Magneto",
      location: "Austin, TX",
      jobType: "full-time",
      salary: "$100,000 - $130,000",
      applicationUrl: "https://careers.magneto.com/fullstack-dev",
      description: "Join our engineering team as a Full Stack Developer and work on complex problems across our entire stack. You'll build features from the database to the user interface and contribute to the architecture of our applications.",
      requirements: "4+ years of full stack development experience\nProficiency in JavaScript/TypeScript and at least one backend language\nExperience with React and Node.js\nFamiliarity with databases and API design\nStrong problem-solving and debugging skills"
    },
    platforms: ["meta", "linkedin", "google"],
    audience: {
      name: "Full Stack Developers",
      ageRange: [25, 45],
      experienceYears: [4, 12],
      locations: ["Austin", "Denver", "Remote"],
      jobTitles: ["Full Stack Developer", "Software Engineer", "Web Developer"],
      skills: ["JavaScript", "TypeScript", "React", "Node.js", "SQL", "NoSQL"]
    }
  },
  "camp-005": {
    id: "camp-005",
    title: "Data Scientist",
    status: "scheduled",
    platform: "LinkedIn, Google",
    createdDate: "May 22, 2023",
    jobDetails: {
      title: "Data Scientist",
      company: "Magneto",
      location: "Seattle, WA",
      jobType: "full-time",
      salary: "$130,000 - $160,000",
      applicationUrl: "https://careers.magneto.com/data-scientist",
      description: "We're looking for a Data Scientist to help us extract insights from our data and build predictive models. You'll work with large datasets and collaborate with engineering and product teams to drive data-informed decisions.",
      requirements: "Advanced degree in Statistics, Computer Science, or related field\n3+ years of experience in data science or similar role\nProficiency in Python and data analysis libraries\nExperience with machine learning frameworks\nStrong statistical knowledge and experimental design"
    },
    platforms: ["linkedin", "google"],
    audience: {
      name: "Data Scientists",
      ageRange: [25, 45],
      experienceYears: [3, 10],
      locations: ["Seattle", "San Francisco", "Remote"],
      jobTitles: ["Data Scientist", "ML Engineer", "Statistician"],
      skills: ["Python", "Machine Learning", "Statistics", "SQL", "Data Visualization"]
    }
  },
  "camp-006": {
    id: "camp-006",
    title: "DevOps Engineer",
    status: "draft",
    platform: "Meta, LinkedIn",
    createdDate: "May 20, 2023",
    jobDetails: {
      title: "DevOps Engineer",
      company: "Magneto",
      location: "Remote",
      jobType: "full-time",
      salary: "$110,000 - $140,000",
      applicationUrl: "https://careers.magneto.com/devops",
      description: "Join our infrastructure team as a DevOps Engineer and help us build and maintain our cloud infrastructure. You'll automate processes, improve reliability, and collaborate with development teams to deploy and monitor our applications.",
      requirements: "3+ years of experience in DevOps or similar role\nStrong knowledge of cloud platforms (AWS preferred)\nExperience with infrastructure as code (Terraform, CloudFormation)\nFamiliarity with CI/CD tools and practices\nStrong scripting skills (Python, Bash)"
    },
    platforms: ["meta", "linkedin"],
    audience: {
      name: "DevOps Engineers",
      ageRange: [25, 45],
      experienceYears: [3, 10],
      locations: ["Remote"],
      jobTitles: ["DevOps Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
      skills: ["AWS", "Terraform", "Docker", "Kubernetes", "CI/CD", "Linux"]
    }
  }
};

// Helper function to simulate API delay
export const simulateNetworkDelay = async (ms: number = 800) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};
