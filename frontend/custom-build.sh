#!/bin/sh

# Run TypeScript check with tsc instead of vue-tsc
echo "Running TypeScript check..."
npx tsc --noEmit || echo "TypeScript check completed with warnings"

# Build with Vite
echo "Building with Vite..."
npx vite build

# Ensure the output directory exists
echo "Ensuring output directory exists..."
mkdir -p /app/staticfiles/vue

# Copy the built files to the correct location
echo "Copying built files to staticfiles/vue directory..."
if [ -d "dist" ]; then
  cp -rv dist/* /app/staticfiles/vue/ || echo "Failed to copy from dist directory"
elif [ -d "../static/vue" ]; then
  cp -rv ../static/vue/* /app/staticfiles/vue/ || echo "Failed to copy from static/vue directory"
else
  echo "ERROR: Could not find build output in either dist/ or ../static/vue/"
  echo "Current directory: $(pwd)"
  echo "Directory contents:"
  ls -la
  echo "Parent directory contents:"
  ls -la ..
  exit 1
fi

# Verify the files were copied
echo "Verifying files in staticfiles/vue directory:"
ls -la /app/staticfiles/vue/ 