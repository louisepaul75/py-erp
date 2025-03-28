/**
 * This script exports the dashboard layout from localStorage to a JSON file.
 * Can be run in browser or Node.js environment.
 */

// Function to export the dashboard layout
async function exportDashboardLayout(providedLayout) {
  try {
    let layout;

    // Validate input first
    if (providedLayout === null || providedLayout === undefined) {
      throw new Error('Invalid layout format');
    }

    // If we're in a browser environment and no layout provided, try localStorage
    if (typeof window !== 'undefined' && !providedLayout) {
      const layoutJson = localStorage.getItem('dashboard-grid-layout');
      if (!layoutJson) {
        throw new Error('No dashboard layout found in localStorage');
      }
      layout = JSON.parse(layoutJson);
    } else {
      layout = providedLayout;
    }

    // Validate layout
    if (typeof layout !== 'object') {
      throw new Error('Invalid layout format');
    }

    // Additional validation for layout format
    if (layout.lg && !Array.isArray(layout.lg)) {
      throw new Error('Invalid layout format');
    }

    const layoutJson = JSON.stringify(layout, null, 2);

    // Check for Node.js environment first
    if (typeof process !== 'undefined' && process.versions && process.versions.node) {
      const fs = require('fs');
      const path = require('path');
      const outputPath = path.join(process.cwd(), 'dashboard-layout.json');
      try {
        fs.writeFileSync(outputPath, layoutJson);
      } catch (err) {
        throw new Error('Write error');
      }
    } 
    // In browser environment
    else {
      // Create a Blob with the JSON data
      const blob = new Blob([layoutJson], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'dashboard-layout.json';
      document.body.appendChild(a);
      
      // Trigger the download
      a.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    }

    return layout;
  } catch (error) {
    throw error;
  }
}

// Alternative method to just display the layout in console
function showDashboardLayout() {
  try {
    // Check if we're in a browser environment
    if (typeof localStorage === 'undefined') {
      console.error('Not in a browser environment');
      return undefined;
    }

    const layoutJson = localStorage.getItem('dashboard-grid-layout');
    
    if (!layoutJson) {
      console.error('No dashboard layout found in localStorage');
      return undefined;
    }
    
    const layout = JSON.parse(layoutJson);
    console.log('Current dashboard layout:');
    console.log(JSON.stringify(layout, null, 2));
    
    return layout;
  } catch (error) {
    console.error('Failed to show dashboard layout:', error);
    return undefined;
  }
}

// Execute the export function if directly executed (not imported)
if (typeof module === 'undefined') {
  exportDashboardLayout();
  // Also show in console
  showDashboardLayout();
}

// Export for testing
if (typeof module !== 'undefined') {
  module.exports = {
    exportDashboardLayout,
    showDashboardLayout
  };
} 