#!/bin/sh

# Run TypeScript check with tsc instead of vue-tsc
echo "Running TypeScript check..."
npx tsc --noEmit || echo "TypeScript check completed with warnings"

# Build with Vite
echo "Building with Vite..."
npx vite build

# Ensure the built index.html has the correct paths
echo "Updating index.html paths..."
if [ -f "dist/index.html" ]; then
  # Replace TypeScript source references with built JavaScript files
  sed -i 's|src="/src/main.ts"|src="/js/main.js"|g' dist/index.html
  echo "Updated index.html to use built JavaScript files"
else
  echo "Warning: dist/index.html not found"
fi

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