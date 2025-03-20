/**
 * This script exports the dashboard layout from localStorage to a JSON file.
 * Run this in the browser console when you have your desired dashboard layout.
 */

// Function to export the dashboard layout
function exportDashboardLayout() {
  try {
    // Get the current layout from localStorage
    const layoutJson = localStorage.getItem('dashboard-grid-layout');
    
    if (!layoutJson) {
      console.error('No dashboard layout found in localStorage');
      return;
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
  } catch (error) {
    console.error('Failed to export dashboard layout:', error);
  }
}

// Alternative method to just display the layout in console
function showDashboardLayout() {
  try {
    const layoutJson = localStorage.getItem('dashboard-grid-layout');
    
    if (!layoutJson) {
      console.error('No dashboard layout found in localStorage');
      return;
    }
    
    const layout = JSON.parse(layoutJson);
    console.log('Current dashboard layout:');
    console.log(JSON.stringify(layout, null, 2));
    
    return layout;
  } catch (error) {
    console.error('Failed to show dashboard layout:', error);
  }
}

// Execute the export function
exportDashboardLayout();

// Also show in console
showDashboardLayout(); 