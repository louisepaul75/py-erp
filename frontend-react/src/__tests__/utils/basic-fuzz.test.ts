/**
 * Basic property-based testing example without jest-fuzz
 */

// Simple utility functions for testing
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
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

// Property-based tests using regular Jest functions
describe('Property-based testing without jest-fuzz', () => {
  // Test 1: formatCurrency should always return a string with $ symbol
  test('formatCurrency returns string with $ sign', () => {
    // Test 100 random values
    for (let i = 0; i < 100; i++) {
      const num = Math.random() * 1000 - 500; // Random value between -500 and 500
      const formatted = formatCurrency(num);
      expect(typeof formatted).toBe('string');
      expect(formatted).toContain('$');
      
      // For negative values, it should have a minus sign
      if (num < 0) {
        expect(formatted).toContain('-');
      }
    }
  });

  // Test 2: truncateText respects max length
  test('truncateText respects max length', () => {
    for (let i = 0; i < 100; i++) {
      // Generate random text and max length
      const textLength = Math.floor(Math.random() * 100) + 1;
      const text = 'a'.repeat(textLength);
      const maxLength = Math.floor(Math.random() * 50) + 5;
      
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

  // Test 3: slugify follows expected rules
  test('slugify removes special characters and spacing', () => {
    const testCases = [
      'Hello World',
      'Special@#$%^&*Characters',
      '  Trim Spaces  ',
      'UPPERCASE text',
      'multiple--hyphens--here',
      '-start-and-end-hyphens-',
      'numbers123'
    ];
    
    for (const text of testCases) {
      const slug = slugify(text);
      
      // Properties of a valid slug
      expect(slug).not.toContain(' ');  // No spaces
      expect(slug).toEqual(slug.toLowerCase());  // All lowercase
      expect(slug).toMatch(/^[a-z0-9-]+$/);  // Only alphanumeric and hyphens
      expect(slug).not.toMatch(/--/);  // No consecutive hyphens
      expect(slug).not.toMatch(/^-/);  // Doesn't start with hyphen
      expect(slug).not.toMatch(/-$/);  // Doesn't end with hyphen
    }
  });
});