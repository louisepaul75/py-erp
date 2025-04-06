import { instance as apiInstance } from "@/lib/api"

export interface GridLayoutItem {
  i: string
  x: number
  y: number
  w: number
  h: number
  minW?: number
  minH?: number
  maxW?: number
  maxH?: number
  static?: boolean
  isDraggable?: boolean
  isResizable?: boolean
  moved?: boolean
  title?: string | null
}

export interface GridLayouts {
  lg: GridLayoutItem[]
  md: GridLayoutItem[]
  sm: GridLayoutItem[]
  [key: string]: GridLayoutItem[]
}

export interface SavedLayout {
  id: string
  name: string
  grid_layout: GridLayouts
  created_at?: string
  updated_at?: string
}

export interface DashboardConfig {
  grid_layout: GridLayouts
  saved_layouts: SavedLayout[]
  active_layout_id: string | null
  dashboard_modules?: any[]  // Add proper typing if needed
}

export async function fetchDashboardConfig(): Promise<DashboardConfig> {
  try {
    if (!apiInstance) {
      console.error("API instance is not defined");
      // Return a default configuration if the API instance is missing
      return {
        grid_layout: {
          lg: [],
          md: [],
          sm: []
        },
        saved_layouts: [],
        active_layout_id: null
      };
    }

    const response = await apiInstance.get("v1/dashboard/summary/").json<DashboardConfig>();
    return {
      grid_layout: response.grid_layout || {
        lg: [],
        md: [],
        sm: []
      },
      saved_layouts: response.saved_layouts || [],
      active_layout_id: response.active_layout_id,
      dashboard_modules: response.dashboard_modules
    }
  } catch (error) {
    console.error("Error fetching dashboard config:", error);
    // Return a default configuration on error
    return {
      grid_layout: {
        lg: [],
        md: [],
        sm: []
      },
      saved_layouts: [],
      active_layout_id: null
    };
  }
}

export async function saveGridLayout(gridLayout: GridLayouts): Promise<GridLayouts> {
  try {
    if (!apiInstance) {
      console.error("API instance is not defined");
      return gridLayout;
    }

    const response = await apiInstance.patch("api/v1/dashboard/summary/", {
      json: {
        grid_layout: gridLayout,
      }
    }).json<{grid_layout: GridLayouts}>();
    return response.grid_layout || gridLayout;
  } catch (error) {
    console.error("Error saving grid layout:", error);
    return gridLayout; // Return the original grid layout on error
  }
}

export async function saveNewLayout(name: string, gridLayout: GridLayouts): Promise<DashboardConfig> {
  try {
    if (!apiInstance) {
      console.error("API instance is not defined");
      return {
        grid_layout: gridLayout,
        saved_layouts: [],
        active_layout_id: null
      };
    }

    const response = await apiInstance.patch("api/v1/dashboard/summary/", {
      json: {
        layout_action: "save",
        layout_name: name,
        grid_layout: gridLayout,
      }
    }).json<DashboardConfig>();
    return {
      grid_layout: response.grid_layout || gridLayout,
      saved_layouts: response.saved_layouts || [],
      active_layout_id: response.active_layout_id
    }
  } catch (error) {
    console.error("Error saving new layout:", error);
    return {
      grid_layout: gridLayout,
      saved_layouts: [],
      active_layout_id: null
    };
  }
}

export async function updateLayout(layoutId: string, name: string, gridLayout: GridLayouts): Promise<DashboardConfig> {
  try {
    if (!apiInstance) {
      console.error("API instance is not defined");
      return {
        grid_layout: gridLayout,
        saved_layouts: [],
        active_layout_id: layoutId
      };
    }

    const response = await apiInstance.patch("api/v1/dashboard/summary/", {
      json: {
        layout_action: "save",
        layout_id: layoutId,
        layout_name: name,
        grid_layout: gridLayout,
      }
    }).json<DashboardConfig>();
    return {
      grid_layout: response.grid_layout || gridLayout,
      saved_layouts: response.saved_layouts || [],
      active_layout_id: response.active_layout_id
    }
  } catch (error) {
    console.error("Error updating layout:", error);
    return {
      grid_layout: gridLayout,
      saved_layouts: [],
      active_layout_id: layoutId
    };
  }
}

export async function deleteLayout(layoutId: string): Promise<DashboardConfig> {
  try {
    if (!apiInstance) {
      console.error("API instance is not defined");
      return {
        grid_layout: {
          lg: [],
          md: [],
          sm: []
        },
        saved_layouts: [],
        active_layout_id: null
      };
    }

    const response = await apiInstance.patch("api/v1/dashboard/summary/", {
      json: {
        layout_action: "delete",
        layout_id: layoutId,
      }
    }).json<DashboardConfig>();
    return {
      grid_layout: response.grid_layout || {
        lg: [],
        md: [],
        sm: []
      },
      saved_layouts: response.saved_layouts || [],
      active_layout_id: response.active_layout_id
    }
  } catch (error) {
    console.error("Error deleting layout:", error);
    return {
      grid_layout: {
        lg: [],
        md: [],
        sm: []
      },
      saved_layouts: [],
      active_layout_id: null
    };
  }
}

export async function activateLayout(layoutId: string): Promise<DashboardConfig> {
  try {
    if (!apiInstance) {
      console.error("API instance is not defined");
      return {
        grid_layout: {
          lg: [],
          md: [],
          sm: []
        },
        saved_layouts: [],
        active_layout_id: layoutId
      };
    }

    const response = await apiInstance.patch("api/v1/dashboard/summary/", {
      json: {
        layout_action: "activate",
        layout_id: layoutId,
      }
    }).json<DashboardConfig>();
    return {
      grid_layout: response.grid_layout || {
        lg: [],
        md: [],
        sm: []
      },
      saved_layouts: response.saved_layouts || [],
      active_layout_id: response.active_layout_id
    }
  } catch (error) {
    console.error("Error activating layout:", error);
    return {
      grid_layout: {
        lg: [],
        md: [],
        sm: []
      },
      saved_layouts: [],
      active_layout_id: layoutId
    };
  }
} 