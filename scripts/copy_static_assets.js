#!/usr/bin/env node

/**
 * Script to copy static assets from frontend/src/assets to static/images
 * This ensures that the images are available in both development and production
 */

const fs = require('fs');
const path = require('path');

// Define source and destination directories
const sourceDir = path.join(__dirname, '..', 'frontend', 'src', 'assets');
const destDir = path.join(__dirname, '..', 'static', 'images');
const staticfilesDir = path.join(__dirname, '..', 'staticfiles', 'images');

// Create destination directories if they don't exist
if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
  console.log(`Created directory: ${destDir}`);
}

if (!fs.existsSync(staticfilesDir)) {
  fs.mkdirSync(staticfilesDir, { recursive: true });
  console.log(`Created directory: ${staticfilesDir}`);
}

// Copy files from source to destination
fs.readdir(sourceDir, (err, files) => {
  if (err) {
    console.error(`Error reading source directory: ${err.message}`);
    process.exit(1);
  }

  files.forEach(file => {
    const sourcePath = path.join(sourceDir, file);
    const destPath = path.join(destDir, file);
    const staticfilesPath = path.join(staticfilesDir, file);

    // Skip directories
    if (fs.statSync(sourcePath).isDirectory()) {
      console.log(`Skipping directory: ${file}`);
      return;
    }

    // Copy to static/images
    fs.copyFile(sourcePath, destPath, err => {
      if (err) {
        console.error(`Error copying ${file} to static/images: ${err.message}`);
      } else {
        console.log(`Copied ${file} to static/images`);
      }
    });

    // Copy to staticfiles/images
    fs.copyFile(sourcePath, staticfilesPath, err => {
      if (err) {
        console.error(`Error copying ${file} to staticfiles/images: ${err.message}`);
      } else {
        console.log(`Copied ${file} to staticfiles/images`);
      }
    });
  });
});

console.log('Static assets copy process completed.');
