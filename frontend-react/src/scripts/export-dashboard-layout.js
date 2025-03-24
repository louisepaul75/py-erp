/**
 * This script exports the dashboard layout from localStorage to a JSON file.
 * Run this in the browser console when you have your desired dashboard layout.
 */

// Function to export the dashboard layout
function exportDashboardLayout() {
  try {
    // Check if we're in a browser environment
    if (typeof localStorage === 'undefined' || typeof document === 'undefined') {
      console.error('Not in a browser environment');
      return false;
    }

    // Get the current layout from localStorage
    const layoutJson = localStorage.getItem('dashboard-grid-layout');
    
    if (!layoutJson) {
      console.error('No dashboard layout found in localStorage');
      return false;
    }
    
    // Parse to validate it's proper JSON
    const layout = JSON.parse(layoutJson);
    
    // Create a Blob with the JSON data
    const blob = new Blob([JSON.stringify(layout, null, 2)], { type: 'application/json' });
    
    // Create a download link
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
    
    console.log('Dashboard layout exported successfully!');
    return true;
  } catch (error) {
    console.error('Failed to export dashboard layout:', error);
    return false;
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