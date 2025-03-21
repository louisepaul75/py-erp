/**
 * Simple property-based test example
 */

// Simple function to test
const add = (a: number, b: number): number => a + b;

// Basic fuzz test
describe('Simple fuzz test example', () => {
  test('Adding two numbers', () => {
    // Generate 50 random test cases
    for (let i = 0; i < 50; i++) {
      const a = Math.random() * 100;
      const b = Math.random() * 100;
      const result = add(a, b);
      expect(result).toBe(a + b);
    }
  });
}); 