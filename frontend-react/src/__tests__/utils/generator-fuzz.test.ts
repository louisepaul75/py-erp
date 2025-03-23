/**
 * Generator-based property testing example
 * 
 * This approach creates custom generators for test data
 * similar to what jest-fuzz and other property testing
 * libraries provide
 */

// Generator functions
const generateNumber = (min = -1000, max = 1000): number => {
  return min + Math.random() * (max - min);
};

const generateString = (minLength = 0, maxLength = 100): string => {
  const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

const generateBoolean = (): boolean => {
  return Math.random() > 0.5;
};

const generateArray = <T>(generator: () => T, minLength = 0, maxLength = 10): T[] => {
  const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
  const result: T[] = [];
  for (let i = 0; i < length; i++) {
    result.push(generator());
  }
  return result;
};

const generateOneOf = <T>(values: T[]): T => {
  return values[Math.floor(Math.random() * values.length)];
};

// Domain-specific generators
const generateProduct = () => {
  return {
    id: Math.floor(generateNumber(1, 10000)),
    code: `PRD-${Math.floor(generateNumber(100, 999))}`,
    name: generateString(5, 30),
    price: parseFloat(generateNumber(0.01, 1000).toFixed(2)),
    stock: Math.floor(generateNumber(0, 1000)),
    category: generateOneOf(['Electronics', 'Clothing', 'Food', 'Books']),
    active: generateBoolean(),
  };
};

// Utility functions to test
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

const formatProduct = (product: any): string => {
  return `${product.name} (${product.code}) - ${formatCurrency(product.price)}`;
};

// Property-based test function that runs a test multiple times
const forAll = <T>(
  generator: () => T, 
  testFn: (value: T) => void | boolean,
  iterations = 100
) => {
  for (let i = 0; i < iterations; i++) {
    const value = generator();
    const result = testFn(value);
    
    // If testFn returns false, the test fails
    if (result === false) {
      throw new Error(`Property test failed on iteration ${i} with value: ${JSON.stringify(value)}`);
    }
  }
};

// Tests using our property testing utilities
describe('Generator-based property testing', () => {
  test('formatCurrency works for any number', () => {
    forAll(generateNumber, (num) => {
      const formatted = formatCurrency(num);
      return (
        typeof formatted === 'string' &&
        formatted.includes('$') &&
        (num < 0 ? formatted.includes('-') : true)
      );
    });
  });

  test('formatProduct displays correctly for any product', () => {
    forAll(generateProduct, (product) => {
      const formatted = formatProduct(product);
      return (
        formatted.includes(product.name) &&
        formatted.includes(product.code) &&
        formatted.includes('$')
      );
    });
  });
  
  // Example with multiple generators
  test('number arrays can be summed', () => {
    const generateNumberArray = () => generateArray(
      () => generateNumber(0, 100), 
      1, 
      10
    );
    
    forAll(generateNumberArray, (numbers) => {
      const sum = numbers.reduce((total, num) => total + num, 0);
      return sum >= 0 && sum <= numbers.length * 100;
    });
  });
}); 