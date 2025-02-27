# Docker & CI/CD Infrastructure User Stories

## Overview
These user stories cover the infrastructure setup for Docker containers and CI/CD pipelines for the pyERP system. They document requirements, lessons learned, and implementation details for reliable deployment and infrastructure management.

## User Stories

### Docker Infrastructure

#### US-D101: System Dependencies for Complex Python Packages
**As a** DevOps Engineer  
**I want to** ensure all necessary system dependencies are installed in Docker containers  
**So that** Python packages with complex C extensions compile successfully

**Acceptance Criteria:**
- Docker build succeeds without dependency-related errors
- WeasyPrint and other packages with C dependencies install correctly
- The Docker image remains as small as possible while including all required dependencies
- Both development and production containers have appropriate dependency sets

**Implementation Notes:**
- WeasyPrint requires multiple system libraries including:
  - `build-essential` for compilation
  - `libcairo2-dev`, `libpango1.0-dev`, `libgdk-pixbuf2.0-dev` for PDF rendering
  - `libffi-dev` and `pkg-config` for interface generation
  - `shared-mime-info` for MIME type detection
- MySQL client requires `default-libmysqlclient-dev`
- Runtime containers need appropriate runtime libraries:
  - `fonts-liberation` for proper font rendering in PDFs
  - Runtime equivalents of development libraries (e.g., `libcairo2` vs `libcairo2-dev`)

#### US-D102: Multi-Stage Docker Builds
**As a** DevOps Engineer  
**I want to** implement multi-stage Docker builds  
**So that** production images remain small and secure

**Acceptance Criteria:**
- Build stage includes all development dependencies
- Final stage includes only runtime dependencies
- Wheels are compiled in build stage and copied to final stage
- Final image runs as non-root user
- Image size is optimized

### CI/CD Pipeline

#### US-C101: GitHub Actions Container Registry Integration
**As a** DevOps Engineer  
**I want to** push Docker images to GitHub Container Registry as part of CI/CD  
**So that** images are versioned and readily available for deployment

**Acceptance Criteria:**
- GitHub Actions workflow successfully builds Docker images
- Images are pushed to GitHub Container Registry
- Proper permissions are configured in workflow files
- Images are tagged appropriately based on branch/tag

**Implementation Notes:**
- GitHub Actions workflows require explicit permissions:
  ```yaml
  permissions:
    contents: read
    packages: write
  ```
- Container Registry authentication uses GitHub token:
  ```yaml
  with:
    registry: ghcr.io
    username: ${{ github.repository_owner }}
    password: ${{ secrets.GITHUB_TOKEN }}
  ```
- Images should be properly tagged for different environments:
  - `master`/`main` branches for latest development
  - Semantic version tags for releases
  - Commit SHA for unique version tracking

#### US-C102: CI/CD Workflow Optimization
**As a** Developer  
**I want to** fast and reliable CI/CD pipelines  
**So that** feedback on changes is quick and deployment is efficient

**Acceptance Criteria:**
- CI/CD workflows complete in reasonable time
- Docker layers are properly cached
- Dependencies are efficiently managed
- Failed builds provide clear error messages

## Technical Tasks

### Docker Tasks
- [x] Configure multi-stage Docker builds
- [x] Identify and add all system dependencies for Python packages
- [x] Optimize final image size
- [x] Implement non-root user configuration
- [x] Add proper build caching

### CI/CD Tasks
- [x] Set up GitHub Actions for Docker builds
- [x] Configure GitHub Container Registry integration
- [x] Add proper permissions to GitHub workflows 
- [x] Implement intelligent tagging strategy
- [ ] Add vulnerability scanning for container images
- [ ] Configure deployment pipeline for different environments 