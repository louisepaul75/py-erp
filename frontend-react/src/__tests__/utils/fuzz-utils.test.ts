/**
 * Tests for our custom generators
 */

import fc from 'fast-check';
import {
  stringGen,
  emailGen,
  numberGen,
  decimalGen,
  booleanGen,
  dateGen,
  arrayGen,
  oneOfGen,
  productCodeGen,
  statusGen,
  productGen,
  customerGen,
  orderItemGen,
  orderGen
} from '@/lib/testing/fuzz-utils';

describe('Custom generators', () => {
  test('stringGen generates strings of expected length', () => {
    const minLength = 5;
    const maxLength = 10;
    const generator = stringGen(minLength, maxLength);
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThanOrEqual(minLength);
      expect(result.length).toBeLessThanOrEqual(maxLength);
    }
  });
  
  test('emailGen generates valid email addresses', () => {
    const generator = emailGen();
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(typeof result).toBe('string');
      expect(result).toMatch(/^[a-z0-9]+@example\.com$/);
    }
  });
  
  test('numberGen generates numbers in the expected range', () => {
    const min = 10;
    const max = 20;
    const generator = numberGen(min, max);
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(typeof result).toBe('number');
      expect(result).toBeGreaterThanOrEqual(min);
      expect(result).toBeLessThanOrEqual(max);
    }
  });
  
  test('decimalGen generates decimals with correct precision', () => {
    const min = 0;
    const max = 100;
    const precision = 2;
    const generator = decimalGen(min, max, precision);
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(typeof result).toBe('number');
      expect(result).toBeGreaterThanOrEqual(min);
      expect(result).toBeLessThanOrEqual(max);
      
      // Check precision
      const decimalPart = result.toString().split('.')[1] || '';
      expect(decimalPart.length).toBeLessThanOrEqual(precision);
    }
  });
  
  test('booleanGen generates true or false', () => {
    const generator = booleanGen();
    let trueCount = 0;
    let falseCount = 0;
    
    for (let i = 0; i < 100; i++) {
      const result = generator();
      expect(typeof result).toBe('boolean');
      
      if (result) trueCount++;
      else falseCount++;
    }
    
    // With 100 samples, we should have both true and false
    expect(trueCount).toBeGreaterThan(0);
    expect(falseCount).toBeGreaterThan(0);
  });
  
  test('dateGen generates dates in the expected range', () => {
    const startDate = new Date(2020, 0, 1);
    const endDate = new Date(2023, 11, 31);
    const generator = dateGen(startDate, endDate);
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(result instanceof Date).toBe(true);
      expect(result.getTime()).toBeGreaterThanOrEqual(startDate.getTime());
      expect(result.getTime()).toBeLessThanOrEqual(endDate.getTime());
    }
  });
  
  test('arrayGen generates arrays of expected length', () => {
    const minLength = 2;
    const maxLength = 5;
    const itemGenerator = () => 'item';
    const generator = arrayGen(itemGenerator, minLength, maxLength);
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThanOrEqual(minLength);
      expect(result.length).toBeLessThanOrEqual(maxLength);
      expect(result.every(item => item === 'item')).toBe(true);
    }
  });
  
  test('oneOfGen selects from provided values', () => {
    const values = ['a', 'b', 'c'];
    const generator = oneOfGen(values);
    
    for (let i = 0; i < 50; i++) {
      const result = generator();
      expect(values).toContain(result);
    }
  });
  
  test('Complex generators produce valid objects', () => {
    // Just verify they run without errors and return objects
    expect(typeof productCodeGen()()).toBe('string');
    expect(typeof statusGen()()).toBe('string');
    expect(typeof productGen()()).toBe('object');
    expect(typeof customerGen()()).toBe('object');
    expect(typeof orderItemGen()()).toBe('object');
    expect(typeof orderGen()()).toBe('object');
    
    // Check object properties
    const product = productGen()();
    expect(product).toHaveProperty('id');
    expect(product).toHaveProperty('name');
    expect(product).toHaveProperty('price');
    
    const customer = customerGen()();
    expect(customer).toHaveProperty('id');
    expect(customer).toHaveProperty('name');
    expect(customer).toHaveProperty('email');
    
    const order = orderGen()();
    expect(order).toHaveProperty('order_number');
    expect(order).toHaveProperty('items');
    expect(Array.isArray(order.items)).toBe(true);
  });
}); 