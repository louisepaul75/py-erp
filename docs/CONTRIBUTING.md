# Contributing to pyERP

Thank you for considering contributing to pyERP! This document provides guidelines and workflows to follow when contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Branching Strategy](#branching-strategy)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

This project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Branching Strategy

We follow a modified GitFlow workflow with the following branches:

### Main Branches

- **`prod`**: Production-ready code, always stable and deployable
- **`dev`**: Integration branch for active development

### Supporting Branches

- **`feature/*`**: For new features (e.g., `feature/product-bom-creation`)
- **`bugfix/*`**: For bug fixes in development
- **`hotfix/*`**: For critical fixes that need to go directly to production
- **`release/*`**: For preparing version releases (e.g., `release/1.0.0`)

## Development Workflow

### For New Features

1. Create a new feature branch from `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Develop your feature, making regular commits.

3. Keep your feature branch updated with `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout feature/your-feature-name
   git merge dev
   ```

4. When your feature is complete, push your branch and create a pull request to `dev`.

### For Bug Fixes

1. Create a new bugfix branch from `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b bugfix/bug-description
   ```

2. Fix the bug and commit your changes.

3. Push your branch and create a pull request to `dev`.

### For Hotfixes

1. Create a hotfix branch from `prod`:
   ```bash
   git checkout prod
   git pull
   git checkout -b hotfix/critical-bug-description
   ```

2. Fix the critical bug and commit your changes.

3. Push your branch and create a pull request to `prod`.

4. After merging to `prod`, ensure the fix is also merged to `dev`.

### For Releases

1. Create a release branch from `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b release/x.y.z
   ```

2. Make any final version updates and fixes on this branch.

3. When ready, create pull requests to both `prod` and `dev`.

4. After merging to `prod`, tag the release:
   ```bash
   git checkout prod
   git pull
   git tag -a vx.y.z -m "Version x.y.z"
   git push origin vx.y.z
   ```

## Pull Request Process

1. Ensure your code adheres to the project's coding standards.
2. Update documentation as necessary.
3. Add or update tests as appropriate.
4. Fill out the pull request template completely.
5. Request review from at least one maintainer.
6. Address any feedback from reviewers.
7. Once approved, your PR will be merged by a maintainer.

## Coding Standards

We follow Django's coding style and PEP 8 with the following specific requirements:

1. Use 4 spaces for indentation (no tabs).
2. Maximum line length of 119 characters.
3. Follow Django naming conventions:
   - CamelCase for classes
   - snake_case for functions, methods, and variables
   - UPPERCASE for constants
4. Write docstrings for all public modules, functions, classes, and methods.
5. Include type hints for function parameters and return values.

Our pre-commit hooks will check many of these standards automatically.

## Commit Message Guidelines

We use conventional commits to standardize our commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding or modifying tests
- **chore**: Changes to the build process or auxiliary tools

Example:
```
feat(products): add BOM management functionality

Implement the ability to create and manage Bills of Materials for manufactured products.

Closes #123
```

## Testing Guidelines

- Write tests for all new features and bug fixes.
- Maintain minimum 80% code coverage for all new code.
- Tests should be independent and idempotent.
- Use pytest as the primary testing framework.
- Follow the test organization structure as defined in the project.

Thank you for contributing to pyERP!
