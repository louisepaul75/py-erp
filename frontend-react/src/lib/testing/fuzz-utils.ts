/**
 * Custom property testing generators for the pyERP frontend
 * 
 * This module provides helper functions and generators for property-based testing
 * to improve test coverage and catch edge cases.
 */

// Basic generators
export const stringGen = (minLength = 0, maxLength = 100) => {
  return () => {
    const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  };
};

export const emailGen = () => {
  return () => {
    const usernameLength = Math.floor(Math.random() * 10) + 5;
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let username = '';
    for (let i = 0; i < usernameLength; i++) {
      username += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return `${username}@example.com`;
  };
};

export const numberGen = (min = 0, max = 1000) => {
  return () => min + Math.random() * (max - min);
};

export const decimalGen = (min = 0, max = 1000, precision = 2) => {
  return () => parseFloat((min + Math.random() * (max - min)).toFixed(precision));
};

export const booleanGen = () => {
  return () => Math.random() > 0.5;
};

export const dateGen = (startDate = new Date(2000, 0, 1), endDate = new Date()) => {
  return () => {
    const startTime = startDate.getTime();
    const endTime = endDate.getTime();
    const randomTime = startTime + Math.random() * (endTime - startTime);
    return new Date(randomTime);
  };
};

export const arrayGen = (itemGen: any, minLength = 0, maxLength = 10) => {
  return () => {
    const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
    const result = [];
    for (let i = 0; i < length; i++) {
      result.push(itemGen());
    }
    return result;
  };
};

export const oneOfGen = (values: any[]) => {
  return () => values[Math.floor(Math.random() * values.length)];
};

// Business domain specific generators
export const productCodeGen = () => {
  return () => {
    const part1 = stringGen(3, 3)().toUpperCase();
    const part2 = String(Math.floor(Math.random() * 900) + 100);
    const part3 = stringGen(3, 3)().toUpperCase();
    return `${part1}-${part2}-${part3}`;
  };
};

export const statusGen = () => {
  return oneOfGen(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']);
};

// Complex domain objects
export const productGen = () => {
  return () => ({
    id: Math.floor(numberGen(1, 10000)()),
    code: productCodeGen()(),
    name: stringGen(5, 50)(),
    price: decimalGen(0.01, 1000)(),
    stock: Math.floor(numberGen(0, 1000)()),
    category: oneOfGen(['Electronics', 'Clothing', 'Food', 'Books'])(),
    active: booleanGen()(),
  });
};

export const customerGen = () => {
  return () => ({
    id: Math.floor(numberGen(1, 10000)()),
    name: stringGen(2, 50)(),
    email: emailGen()(),
    phone: `+1${String(Math.floor(Math.random() * 9000000000) + 1000000000)}`,
    address: stringGen(10, 100)(),
    active: booleanGen()(),
  });
};

export const orderItemGen = () => {
  return () => ({
    product_code: productCodeGen()(),
    quantity: Math.floor(numberGen(1, 100)()),
    price: decimalGen(0.01, 1000)(),
  });
};

export const orderGen = (includeItems = true) => {
  return () => {
    const baseOrder = {
      order_number: `ORD-${String(Math.floor(Math.random() * 900000) + 100000)}`,
      customer_id: Math.floor(numberGen(1, 10000)()),
      date: dateGen()().toISOString().split('T')[0],
      total: decimalGen(10, 10000)(),
      status: statusGen()(),
    };

    if (includeItems) {
      return {
        ...baseOrder,
        items: arrayGen(orderItemGen(), 1, 10)(),
      };
    }

    return baseOrder;
  };
}; 