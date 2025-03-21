# Mutation Testing Demo

This folder contains a demonstration of mutation testing using the `mutmut` library for Python.

## What is Mutation Testing?

Mutation testing is a type of software testing where specific statements in the source code are changed (mutated) to ensure the test suite can detect these changes. It helps you evaluate the quality of your tests by measuring how many "bugs" (mutations) they can detect.

## Files in this Demo

- `basic_functions.py` - Contains simple functions to be tested
- `test_basic_functions.py` - Contains test cases (both weak and strong examples)
- `run_basic_mutmut.sh` - Script to run mutation testing
- `mutmut_example.py` - A self-contained example (legacy, not needed)
- `run_example_mutmut.sh` - Legacy script (not needed)

## How to Run the Demo

```bash
# Make the script executable
chmod +x run_basic_mutmut.sh

# Run the mutation testing
./run_basic_mutmut.sh
```

## Understanding the Results

The script will:
1. Run the normal tests to make sure they pass
2. Run mutation testing
3. Show a summary of the results
4. Present an example of a survived mutation if any are found

If mutations survive, it means your tests are not detecting changes to the code that could introduce bugs. This indicates that your tests might not be comprehensive enough.

## Improving Test Coverage

The demo includes two versions of tests for the `get_grade` function:
- `test_get_grade_weak` - A minimal test that only checks a couple of cases
- `test_get_grade_comprehensive` - A thorough test that checks boundaries and edge cases

The comprehensive test catches many more mutations, showing how careful test design can improve code quality.

## Key Concepts

1. **Mutation** - A small change to your code that simulates a bug
2. **Killed Mutation** - A mutation that is detected by your tests (test fails)
3. **Survived Mutation** - A mutation that is NOT detected by your tests (test passes)
4. **Mutation Score** - Percentage of mutations killed by your tests

A higher mutation score suggests better test quality.

## Integrating with a Larger Project

To use mutation testing in your project:

1. Install mutmut: `pip install mutmut`
2. Create a `setup.cfg` file with the following content:
```
[mutmut]
paths_to_mutate=your_module/
backup=False
runner=python -m unittest discover
```
3. Run: `python -m mutmut run`
4. View results: `python -m mutmut results`

## Limitations of Mutation Testing

- Can be slow for large codebases
- May generate invalid mutations that don't represent real bugs
- Some mutations may be equivalent (functionally identical to original code)

## Resources

- [mutmut documentation](https://mutmut.readthedocs.io/)
- [Mutation Testing on Wikipedia](https://en.wikipedia.org/wiki/Mutation_testing) 