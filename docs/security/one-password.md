Setting up the 1Password integration for development

This guide explains how to set up your local development environment to use the 1Password integration for managing secrets and how this integration works within the `pyERP` codebase.

## Setup

**Obtain Your 1Password Connect Token**: You will be provided with a 1Password Connect Token by the project administrators. This token grants temporary, read-only access to the necessary development secrets stored in our 1Password vault.

**Configure Your `.env` File**:

Locate the `.env` file at config/env/.env.dev. If it doesn't exist, you might need to copy it from an example file (e.g., `.env.dev.example`) or create it.

Add the following line to your `.env` file, replacing `<your_1password_connect_token>` with the actual token you received:

        

OP_CONNECT_TOKEN=<your_1password_connect_token>
OP_CONNECT_HOST=http://192.168.73.65:8080

**Important**: Ensure that your `.env` file is listed in your `.gitignore` file. Never commit your `.env` file or your token to version control.

## How it Works in the Code

The application uses the 1Password Connect SDK to fetch secrets during runtime.

**Initialization**: When the application starts (or when secrets are first needed), it reads the OP_CONNECT_TOKEN` from the environment variables (loaded from your `.env` file in local development).

**Fetching Secrets**: The SDK uses this token to authenticate with the 1Password Connect server (specified by the OP_CONNECT_HOST` environment variable, typically pre-configured). It then fetches the required secrets from the designated vault and item path.

**Usage**: The fetched secrets are then made available to the application, often through a configuration object or dependency injection, ensuring sensitive information is not hardcoded.

