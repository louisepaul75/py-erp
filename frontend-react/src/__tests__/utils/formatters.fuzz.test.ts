/**
 * Property-based tests for formatter utilities
 * 
 * Demonstrates property-based testing in the frontend codebase.
 */

import fc from 'fast-check';
import { 
  numberGen, 
  decimalGen, 
  dateGen, 
  stringGen,
  productGen,
  booleanGen
} from '@/lib/testing/fuzz-utils';

// Formatter functions to test
// In a real application, you would import these from your actual code
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
};

// Property-based test runner
const forAll = <T>(
  generator: () => T, 
  testFn: (value: T) => void | boolean,
  iterations = 100
) => {
  for (let i = 0; i < iterations; i++) {
    const value = generator();
    const result = testFn(value);
    
    if (result === false) {
      throw new Error(`Property test failed on iteration ${i} with value: ${JSON.stringify(value)}`);
    }
  }
};

// Property tests
describe('Formatter utilities property tests', () => {
  // Example 1: Simple property test with number generator
  test('formatCurrency returns string with $ sign', () => {
    forAll(numberGen(), (num) => {
      const formatted = formatCurrency(num);
      return typeof formatted === 'string' && formatted.includes('$');
    });
  });

  // Example 2: Testing with multiple properties
  test('truncateText respects max length', () => {
    const textGen = stringGen(1, 100);
    const maxLengthGen = numberGen(5, 50);
    
    for (let i = 0; i < 50; i++) {
      const text = textGen();
      const maxLength = Math.floor(maxLengthGen());
      const truncated = truncateText(text, maxLength);
      
      // Property 1: Output should never be longer than maxLength + 3 (for "...")
      expect(truncated.length).toBeLessThanOrEqual(
        text.length <= maxLength ? text.length : maxLength + 3
      );
      
      // Property 2: If original text is shorter, it should remain unchanged
      if (text.length <= maxLength) {
        expect(truncated).toEqual(text);
      }
      
      // Property 3: If truncated, it should end with "..."
      if (text.length > maxLength) {
        expect(truncated.endsWith('...')).toBe(true);
      }
    }
  });

  // Example 3: Testing dates
  test('formatDate returns valid formatted date', () => {
    forAll(dateGen(), (date) => {
      const dateString = date.toISOString();
      const formatted = formatDate(dateString);
      
      // Format has month, day, and year
      return formatted.match(/[A-Za-z]+\s\d{1,2},\s\d{4}/) !== null;
    });
  });

  // Example 4: Testing with custom business object
  test('product name can be slugified', () => {
    forAll(productGen(), (product) => {
      const slug = slugify(product.name);
      
      // Properties of a valid slug
      return (
        !slug.includes(' ') &&  // No spaces
        slug === slug.toLowerCase() &&  // All lowercase
        slug.match(/^[a-z0-9-]+$/) !== null &&  // Only alphanumeric and hyphens
        slug.match(/--/) === null &&  // No consecutive hyphens
        slug.match(/^-/) === null &&  // Doesn't start with hyphen
        slug.match(/-$/) === null  // Doesn't end with hyphen
      );
    });
  });

  // Example 5: Testing formatter behavior at boundaries
  test('formatCurrency handles zero and negative values', () => {
    const negativeOrZeroGen = () => {
      const options = [0, -1, -100, -999.99];
      return options[Math.floor(Math.random() * options.length)];
    };
    
    forAll(negativeOrZeroGen, (negativeOrZero) => {
      const formatted = formatCurrency(negativeOrZero);
      
      if (negativeOrZero < 0) {
        // Contains minus sign for negative values
        expect(formatted).toContain('-');
      }
      
      // Always has $ symbol
      expect(formatted).toContain('$');
      return true;
    });
  });

  // Example 6: Multiple iterations with the same generator
  test('slugify removes special characters', () => {
    const specialCharGen = () => {
      const length = Math.floor(Math.random() * 15) + 5;
      const chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+';
      let result = '';
      for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return result;
    };
    
    for (let i = 0; i < 100; i++) {
      const textWithSpecialChars = specialCharGen();
      const slug = slugify(textWithSpecialChars);
      
      // Slug should only contain allowed characters
      // Underscores are allowed in our slugify implementation
      expect(slug).toMatch(/^[a-z0-9_-]*$/);
    }
  });
}); 