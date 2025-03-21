# Mutation Testing with Stryker

This document explains how to use Stryker for mutation testing in the pyERP frontend React application.

## What is Mutation Testing?

Mutation testing is a way to evaluate the quality of your test suite by making small changes (mutations) to your code and checking if your tests can detect these changes. It helps identify weak spots in your test coverage that might not be detected by traditional code coverage metrics.

## How Stryker Works

Stryker works by:

1. Creating mutations (small changes) in your code
2. Running your test suite against each mutation
3. Reporting which mutations were "killed" (detected by tests) and which "survived" (not detected)

## Running Mutation Tests

You can run mutation tests for the entire codebase or for specific files/directories:

### Full Mutation Test

```bash
npm run test:mutation
```

This will run mutation tests on all files specified in the `stryker.conf.js` configuration.

### Testing Specific Files

```bash
npx stryker run --mutate "src/**/utils/**/*.{js,jsx,ts,tsx}"
```

Replace the pattern with any glob pattern that matches the files you want to test.

## Viewing the Report

After running mutation tests, Stryker generates an HTML report. You can view this report by running:

```bash
npm run test:mutation:report
```

This will serve the HTML report on a local server, typically at http://localhost:3000.

## Understanding the Results

The mutation score indicates the percentage of mutations that were detected by your tests:

- **Killed**: Mutations that were detected by your tests (good)
- **Survived**: Mutations that were not detected by your tests (bad)
- **No Coverage**: Mutations in code that isn't covered by tests
- **Timeout**: Mutations that caused tests to timeout
- **Runtime Errors**: Mutations that caused errors during test execution

## Configuration

The Stryker configuration is stored in `stryker.conf.js` in the root of the frontend-react directory. Key settings include:

- **mutate**: File patterns to include or exclude for mutation
- **testRunner**: Set to "jest" to use Jest for running tests
- **coverageAnalysis**: Strategy for determining which tests to run for each mutation
- **timeoutMS**: Maximum time allowed for each mutation test
- **concurrency**: Number of parallel test runners
- **thresholds**: Quality gates for mutation scores

## Tips for Effective Mutation Testing

1. **Start Small**: Begin with small, focused modules or utilities
2. **Target Critical Code**: Focus on business-critical code paths
3. **Limit Scope**: Use specific glob patterns to test only what you're interested in
4. **Lower Concurrency**: If you experience performance issues, reduce the concurrency
5. **Improve Tests**: Use the report to identify and fix weak tests

## Integration with CI/CD

You can add mutation testing to your CI/CD pipeline by adding a step that runs:

```bash
npm run test:mutation
```

And configure it to fail if the mutation score falls below a certain threshold (configured in `stryker.conf.js`). 