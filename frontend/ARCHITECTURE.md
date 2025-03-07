# ERP-Frontend – Overview and Guidelines

This document provides a concise set of decisions and recommendations for our ERP frontend. It serves as a README for our development team, ensuring a consistent structure and approach.

## 1. Architecture & Modularization
We use a single Vue application without a complex subdivision into multiple frontend modules. The frontend resides in a dedicated `frontend/` folder within the Django project (e.g.  and `pyerp/frontend/` for Vue).

## 2. UI/UX & Style Guide
A dedicated style guide defines how we use UI components (colors, spacing, layout examples). We currently use a combination of Bootstrap and Tailwind CSS for styling. We will create a comprehensive style guide based on these components to ensure consistency across the application.

## 3. Layout & Navigation
We employ a top bar (for global actions like user menu, search, notifications) plus a sidebar that can display recently accessed pages or pinned items instead of acting purely as a menu. We do not use breadcrumbs since we only have one or two navigation levels. Sidebar should be hidden by default on tablet but can be shown via a button.

## 4. State Management & Data Flow
We rely on Pinia for state management, simplifying shared data handling. To manage concurrency, we use server-side optimistic locking (e.g., a version column in the Django model) so simultaneous edits do not overwrite each other unexpectedly.

## 5. Security & Roles
We support both authentication methods:
- **Session-based authentication**: Using Django's session cookie for seamless integration with the Django backend
- **JWT-based authentication**: For more decoupled frontend applications with automatic token refresh

The current implementation uses JWT-based authentication, but we may transition to session-based authentication in the future for simplicity. Certain menu items or areas are hidden in the frontend based on user roles (e.g., admin, staff), with final access checks still enforced in Django.

## 6. Performance & Optimization
We leverage lazy-loading and code-splitting for routes and larger components to keep initial load times down. Tables (customers, products, etc.) are paginated on the server side, and basic caching is handled by the browser and/or via the Pinia store for frequently accessed data.

## 7. Internationalization (i18n)
We support both English and German through Vue I18n (or a similar solution). Additional languages can be added later, and an external translation API can be integrated if needed.

## 8. API Design & Backend Integration
We use Django Rest Framework for REST endpoints rather than GraphQL. We document these endpoints via Swagger/OpenAPI, allowing developers and stakeholders to easily see how data is structured.

## Maintenance & Further Development
The aforementioned style guide is our central reference for consistent UI components. The backend returns standardized JSON error messages for uniform handling in the frontend. Any new features or layout changes should align with the existing style guide to maintain consistency over time.

With this setup, we meet our requirements for clarity, flexible authentication, flexible navigation, and multilingual support. We integrate Pinia, REST APIs (with Swagger), server-side optimistic locking, and pagination to address typical ERP challenges effectively. 