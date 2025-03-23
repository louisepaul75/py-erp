# Property-Based Testing in pyERP

This document describes our approach to property-based testing in the pyERP project, covering both the Python backend and JavaScript/TypeScript frontend.

## What is Property-Based Testing?

Property-based testing is a testing approach where, instead of writing specific test cases with predefined inputs and expected outputs, you define properties that should hold true for a range of inputs. The testing framework then generates random inputs to test those properties.

Key advantages:
- Finds edge cases you might not have thought of
- Tests a broader range of inputs than manual test cases
- Helps you think about your code's invariants and properties
- Can automatically "shrink" failing cases to minimal counterexamples

## Tools in Use

### Python Backend

For the Python backend, we use [Hypothesis](https://hypothesis.readthedocs.io/), a powerful property-based testing library:

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_is_commutative(a, b):
    assert a + b == b + a
```

### JavaScript/TypeScript Frontend

For the frontend, we have implemented a custom property testing framework. While we initially tried using jest-fuzz, we found it had compatibility issues with our setup. Our custom implementation allows us to:

1. Create generators for various types of test data
2. Run tests with many random inputs
3. Define properties in a clear, maintainable way

Basic example:
```typescript
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
```

## Examples

We have several examples in the codebase:

### Python (Hypothesis)
- `pyerp/utils/testing/test_hypothesis_example.py` - Example tests
- Includes tests for functions with numeric values, strings, and business objects

### TypeScript 
- `frontend-react/src/__tests__/utils/basic-fuzz.test.ts` - Simple property tests
- `frontend-react/src/__tests__/utils/generator-fuzz.test.ts` - Generator-based approach
- `frontend-react/src/__tests__/utils/business-property-test.test.ts` - Testing business logic

## Best Practices

### When to Use Property Testing

Property testing works best for:
- Pure functions with clear properties
- Code with lots of edge cases
- Numeric calculations
- String transformations
- Data structure operations
- Business logic with invariants

### Defining Good Properties

A good property should be:
1. **True** - Describes something that should always hold
2. **General** - Applies to a wide range of inputs
3. **Precise** - Checks exactly what you care about
4. **Simple** - Easy to understand and reason about

Common types of properties:
- **Invariants**: `reverse(reverse(x)) == x`
- **Equivalence**: `optimizedFn(x) == simpleFn(x)`
- **Idempotence**: `process(process(x)) == process(x)`
- **Round-tripping**: `deserialize(serialize(x)) == x`
- **Conservation**: `count(x) == count(transform(x))`

### Writing Generators

For complex domains, create custom generators that:
- Focus on the relevant parts of the input space
- Generate realistic test data
- Occasionally include edge cases

Example:
```typescript
const generateOrderItem = () => {
  const quantity = Math.max(1, Math.floor(Math.random() * 10));
  const unitPrice = parseFloat(generateNumber(0.01, 100).toFixed(2));
  
  return {
    productId: Math.floor(Math.random() * 10000),
    description: `Product ${Math.floor(Math.random() * 1000)}`,
    quantity,
    unitPrice,
    lineTotal: parseFloat((quantity * unitPrice).toFixed(2))
  };
};
```

## Debugging Failed Tests

When a property test fails:

1. For Hypothesis:
   - The output will show the minimal failing case
   - Use `@settings(verbosity=Verbosity.verbose)` to see more details
   - Use `@example()` to add specific test cases

2. For our custom TypeScript framework:
   - The error will show which iteration failed and with what value
   - Add more specific checks to identify the exact failure condition

## Further Learning

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing with PropEr, Erlang, and Elixir](https://pragprog.com/titles/fhproper/property-based-testing-with-proper-erlang-and-elixir/) (good general concepts)
- [Choosing Properties for Property-Based Testing](https://fsharpforfunandprofit.com/posts/property-based-testing-2/) 