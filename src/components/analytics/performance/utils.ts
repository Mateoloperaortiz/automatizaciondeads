
// Combine current and previous data for comparison
export const combineDataForComparison = (current: any[], previous: any[]) => {
  return current.map((item, index) => ({
    name: item.name,
    current: item.value,
    previous: previous[index].value
  }));
};

// Calculate growth percentage
export const calculateGrowth = (current: number, previous: number): number => {
  if (previous === 0) return 100;
  return Number((((current - previous) / previous) * 100).toFixed(1));
};

// Calculate average values for each dataset
export const calculateAverage = (data: any[]): number => {
  const sum = data.reduce((acc, item) => acc + item.value, 0);
  return Number((sum / data.length).toFixed(1));
};

// Format number with commas
export const formatNumber = (num: number): string => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};
