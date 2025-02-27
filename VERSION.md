# Version History

This document tracks the version history and roadmap for pyERP.

## Current Version

**0.1.0-alpha.1** (Phase 0: Foundation)

## Version Scheme

We follow Semantic Versioning (SemVer) with phase indicators:

```
MAJOR.MINOR.PATCH-PHASE
```

- **MAJOR**: Increment for incompatible API changes
- **MINOR**: Increment for new features (backward compatible)
- **PATCH**: Increment for bug fixes
- **PHASE**: Optional suffix indicating development phase (alpha, beta, rc)

## Development Phases

- **Phase 0 (Foundation)**: Versions starting with `0.x.y` - Project setup, infrastructure, core utilities
- **Phase 1 (MVP)**: Versions starting with `1.0.y` - Basic Product, BOM, Sales, Inventory, minimal Production
- **Phase 2**: Versions starting with `1.x.y` (increasing minor) - Multi-warehouse, advanced flows, integrations
- **Phase 3+**: May move to `2.x.y` if major changes are introduced

## Release History

### 0.1.0-alpha.1 (Current)
- Initial project structure and organization
- Development environment setup with Docker
- Configuration of CI/CD pipeline
- Core utilities and shared components
- Database environment configuration

## Planned Releases

### 0.2.0-alpha (Upcoming)
- Legacy data extraction API utilities
- Data synchronization framework
- Core data models
- Legacy database schema analysis

### 0.3.0-alpha
- Product management module
- Basic user management
- Test infrastructure enhancements

### 0.4.0-beta
- Sales management module (basic)
- Inventory management module (basic)
- Initial data migration tooling

### 0.5.0-beta
- Production management module (basic)
- Enhanced data migration with incremental sync
- UI improvements and basic reporting

### 1.0.0-rc
- Complete MVP feature set
- Full integration testing
- Performance optimization
- User acceptance testing

### 1.0.0
- Official MVP release
- Production-ready deployment
- Complete documentation
- Training materials

## Versioning Notes

1. Pre-release versions (alpha, beta, rc) indicate code that is not yet stable or complete
2. Alpha releases may have incomplete features and known issues
3. Beta releases have complete features but may have bugs or performance issues
4. Release candidates (rc) are feature-complete and tested, ready for final verification

## Version Bump Guidelines

- **MAJOR**: Increment when making incompatible API changes that require updates to integrations
- **MINOR**: Increment when adding functionality in a backward-compatible manner
- **PATCH**: Increment when making backward-compatible bug fixes
- **PHASE**: Update to reflect the current stability level (alpha → beta → rc → release)

Version bumps should be done as part of the release branch creation process. 