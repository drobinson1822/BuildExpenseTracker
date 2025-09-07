export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatDate = (dateString) => {
  if (!dateString) return 'Not set';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatPercent = (value) => {
  if (value === null || value === undefined) return '0%';
  return `${value}%`;
};

export const capitalizeWords = (str) => {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Utility function to determine if variance should be shown
export const shouldShowVariance = (actual, status) => {
  const actualAmount = parseFloat(actual) || 0;
  return !(actualAmount === 0 && status !== "Complete");
};

// Enhanced variance display with proper handling for non-calculated cases
export const getVarianceDisplay = (budgeted, actual, status) => {
  const budgetedAmount = parseFloat(budgeted) || 0;
  const actualAmount = parseFloat(actual) || 0;
  
  // Check if variance should be calculated
  if (!shouldShowVariance(actualAmount, status)) {
    return {
      amount: '—',
      percentage: '',
      color: 'text-gray-600',
      showDash: true,
      tooltip: 'Variance not calculated until spending occurs or item is marked Complete'
    };
  }
  
  const difference = budgetedAmount - actualAmount;
  
  // Handle edge case where budgeted is 0 or negative
  if (budgetedAmount <= 0) {
    return {
      amount: formatCurrency(Math.abs(difference)),
      percentage: '—',
      color: difference >= 0 ? 'text-green-600' : 'text-red-600',
      showDash: false,
      tooltip: null
    };
  }
  
  const percentage = (difference / budgetedAmount) * 100;
  
  if (difference > 0) {
    return {
      amount: formatCurrency(Math.abs(difference)),
      percentage: `(-${Math.abs(percentage).toFixed(1)}%)`,
      color: 'text-green-600',
      showDash: false,
      tooltip: null
    };
  } else if (difference < 0) {
    return {
      amount: `+${formatCurrency(Math.abs(difference))}`,
      percentage: `(${Math.abs(percentage).toFixed(1)}%)`,
      color: 'text-red-600',
      showDash: false,
      tooltip: null
    };
  }
  
  return {
    amount: formatCurrency(0),
    percentage: '(0.0%)',
    color: 'text-gray-600',
    showDash: false,
    tooltip: null
  };
};
