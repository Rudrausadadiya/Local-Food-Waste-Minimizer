/**
 * Environmental Impact Calculator
 * Calculates CO2 emissions prevented and water saved based on UN FAO environmental standards.
 */

// Function: calculateEnvironmentalImpact
export const calculateEnvironmentalImpact = (category = 'General', quantity = 1, weightPerUnitKg = 0.5) => {
  const totalWeightKg = quantity * weightPerUnitKg;

  let co2Factor = 2.5;
  let waterFactor = 250;

  const catLower = (category || '').toLowerCase();
  if (catLower.includes('bakery') || catLower.includes('bread')) {
    co2Factor = 1.8;
    waterFactor = 180;
  } else if (catLower.includes('meal') || catLower.includes('prepared')) {
    co2Factor = 3.2;
    waterFactor = 320;
  } else if (catLower.includes('produce') || catLower.includes('fruit') || catLower.includes('veg')) {
    co2Factor = 1.2;
    waterFactor = 120;
  } else if (catLower.includes('dairy') || catLower.includes('cheese')) {
    co2Factor = 4.5;
    waterFactor = 450;
  }

  const co2SavedKg = Number((totalWeightKg * co2Factor).toFixed(1));
  const waterSavedLiters = Math.round(totalWeightKg * waterFactor);

  return {
    weightKg: totalWeightKg,
    co2SavedKg,
    waterSavedLiters,
  };
};
