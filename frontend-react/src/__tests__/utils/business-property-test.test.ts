/**
 * Business Logic Property Tests
 * 
 * Testing order calculation and discount logic with property-based testing
 * This simulates testing real business logic in the frontend
 */

// Generators for our test data
const generateNumber = (min = -1000, max = 1000): number => {
  return min + Math.random() * (max - min);
};

const generateArray = <T>(generator: () => T, minLength = 0, maxLength = 10): T[] => {
  const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
  const result: T[] = [];
  for (let i = 0; i < length; i++) {
    result.push(generator());
  }
  return result;
};

const generateOrderItem = () => {
  const quantity = Math.max(1, Math.floor(Math.random() * 10));
  const unitPrice = parseFloat(generateNumber(0.01, 100).toFixed(2));
  
  return {
    productId: Math.floor(Math.random() * 10000),
    description: `Product ${Math.floor(Math.random() * 1000)}`,
    quantity,
    unitPrice,
    // Pre-calculate this for verification
    lineTotal: parseFloat((quantity * unitPrice).toFixed(2))
  };
};

const generateOrder = () => {
  const items = generateArray(generateOrderItem, 1, 10);
  return {
    id: `ORD-${Math.floor(Math.random() * 10000)}`,
    customerId: Math.floor(Math.random() * 1000),
    date: new Date().toISOString(),
    items
  };
};

// Business logic to test
interface OrderItem {
  productId: number;
  description: string;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
}

interface Order {
  id: string;
  customerId: number;
  date: string;
  items: OrderItem[];
}

// Calculate order totals with various discount rules
// This is the function we want to test with property testing
const calculateOrderTotal = (order: Order): {
  subtotal: number;
  discountPercent: number;
  discountAmount: number;
  tax: number;
  total: number;
} => {
  // Calculate subtotal from line items - using reduce and precision handling
  const subtotal = parseFloat(
    order.items.reduce((sum, item) => sum + item.lineTotal, 0).toFixed(2)
  );
  
  // Apply quantity discount rule
  let discountPercent = 0;
  const totalItems = order.items.reduce(
    (sum, item) => sum + item.quantity, 
    0
  );
  
  if (totalItems >= 20) {
    discountPercent = 0.15; // 15% discount
  } else if (totalItems >= 10) {
    discountPercent = 0.10; // 10% discount
  } else if (totalItems >= 5) {
    discountPercent = 0.05; // 5% discount
  }
  
  // Override with subtotal discount if better
  if (subtotal >= 1000) {
    discountPercent = Math.max(discountPercent, 0.15); // 15% discount
  } else if (subtotal >= 500) {
    discountPercent = Math.max(discountPercent, 0.10); // 10% discount
  } else if (subtotal >= 200) {
    discountPercent = Math.max(discountPercent, 0.05); // 5% discount
  }
  
  // Use Math.round for consistent rounding to avoid floating point precision issues
  const discountAmount = parseFloat((subtotal * discountPercent).toFixed(2));
  const afterDiscount = parseFloat((subtotal - discountAmount).toFixed(2));
  const tax = parseFloat((afterDiscount * 0.08).toFixed(2)); // 8% tax
  const total = parseFloat((afterDiscount + tax).toFixed(2));
  
  return {
    subtotal,
    discountPercent,
    discountAmount,
    tax,
    total
  };
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

// Tests
describe('Order processing business logic', () => {
  test('Subtotal equals sum of line totals', () => {
    forAll(generateOrder, (order) => {
      const result = calculateOrderTotal(order);
      
      // Calculate expected subtotal manually
      const expectedSubtotal = parseFloat(
        order.items.reduce((sum, item) => sum + item.lineTotal, 0).toFixed(2)
      );
      
      return result.subtotal === expectedSubtotal;
    });
  });
  
  test('Discount percent is applied according to rules', () => {
    forAll(generateOrder, (order) => {
      const result = calculateOrderTotal(order);
      
      // Calculate total items
      const totalItems = order.items.reduce(
        (sum, item) => sum + item.quantity, 
        0
      );
      
      // Calculate expected discount percent
      let expectedDiscountPercent = 0;
      
      // Quantity discount
      if (totalItems >= 20) {
        expectedDiscountPercent = 0.15;
      } else if (totalItems >= 10) {
        expectedDiscountPercent = 0.10;
      } else if (totalItems >= 5) {
        expectedDiscountPercent = 0.05;
      }
      
      // Subtotal discount (take the better discount)
      const subtotal = parseFloat(
        order.items.reduce((sum, item) => sum + item.lineTotal, 0).toFixed(2)
      );
      
      if (subtotal >= 1000) {
        expectedDiscountPercent = Math.max(expectedDiscountPercent, 0.15);
      } else if (subtotal >= 500) {
        expectedDiscountPercent = Math.max(expectedDiscountPercent, 0.10);
      } else if (subtotal >= 200) {
        expectedDiscountPercent = Math.max(expectedDiscountPercent, 0.05);
      }
      
      return result.discountPercent === expectedDiscountPercent;
    });
  });
  
  test('Discount amount equals subtotal times discount percent', () => {
    forAll(generateOrder, (order) => {
      const result = calculateOrderTotal(order);
      
      // Since we've fixed the rounding in the function, we should get exact matches
      const expectedDiscountAmount = parseFloat(
        (result.subtotal * result.discountPercent).toFixed(2)
      );
      
      return result.discountAmount === expectedDiscountAmount;
    });
  });
  
  test('Tax is calculated on post-discount amount', () => {
    forAll(generateOrder, (order) => {
      const result = calculateOrderTotal(order);
      
      const afterDiscount = result.subtotal - result.discountAmount;
      const expectedTax = parseFloat((afterDiscount * 0.08).toFixed(2));
      
      return result.tax === expectedTax;
    });
  });
  
  test('Total equals subtotal minus discount plus tax', () => {
    forAll(generateOrder, (order) => {
      const result = calculateOrderTotal(order);
      
      const expectedTotal = parseFloat(
        (result.subtotal - result.discountAmount + result.tax).toFixed(2)
      );
      
      return result.total === expectedTotal;
    });
  });
}); 