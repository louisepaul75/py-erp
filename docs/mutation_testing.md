# Mutation Testing with mutmut

This guide explains how to use mutation testing with mutmut to improve the quality of your test suite.

## What is Mutation Testing?

Mutation testing is a technique to evaluate the quality of your tests by introducing small changes (mutations) to your code and checking if your tests can detect these changes. A good test suite should fail when code is mutated, showing that the tests are sensitive to changes in the code's behavior.

## Setup

Mutmut is already included in the development dependencies. If you need to install it manually:

```bash
pip install mutmut
```

## Running Mutation Tests

### Option 1: Using the Convenience Script

We've created a script that makes it easier to run mutation tests on specific modules:

```bash
./run_mutmut.sh <module_path> [test_path]
```

For example:

```bash
./run_mutmut.sh pyerp/users/models.py tests/unit/users
```

### Option 2: Running Directly with mutmut

You can run mutmut directly with various options:

```bash
# Run on the entire codebase (might take a long time)
mutmut run

# Run on a specific file or module
mutmut run --paths-to-mutate "pyerp/users/models.py"

# Run with specific test directory
mutmut run --paths-to-mutate "pyerp/users/models.py" --tests-dir "tests/unit/users"
```

## Analyzing Results

After running mutation tests, you can analyze the results:

```bash
# Show overall results
mutmut results

# Show a specific mutation
mutmut show <id>

# Generate HTML report
mutmut html
```

The HTML report will be available at `html/index.html`.

## Configuration

Mutmut is configured through `mutmut_config.py` in the project root. You can modify this file to:

- Change which files are included/excluded from mutation testing
- Modify how tests are run
- Configure other mutmut options

## Improving Test Quality

If mutmut finds mutations that your tests don't catch (survived mutations), you should:

1. Examine the mutation to understand what was changed
2. Update your tests to detect this change
3. Re-run mutation testing to confirm your fix

## Integration with CI/CD

For continuous integration, you can add a step to run mutation testing:

```yaml
# Example GitHub Actions step
- name: Run mutation tests
  run: |
    pip install mutmut
    mutmut run --paths-to-mutate "critical_module.py"
    # Optional: Fail if too many mutations survived
    mutmut junitxml > mutmut-results.xml
```

## Common Issues

- **Tests are too slow**: Limit mutation testing to critical modules rather than the entire codebase
- **Too many survived mutations**: Focus on improving tests for critical code paths first
- **Database connection issues**: Ensure your test database is properly configured and accessible

## Resources

- [Mutmut Documentation](https://mutmut.readthedocs.io/)
- [Python Mutation Testing Best Practices](https://medium.com/analytics-vidhya/mutation-testing-in-python-using-mutmut-4b15795d4064) 