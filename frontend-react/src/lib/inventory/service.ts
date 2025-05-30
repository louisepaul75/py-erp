import { Box, BoxType, PaginatedResponse, fetchBoxes, fetchBoxTypes, fetchStorageLocations, BoxWithSlots } from './api';
import { ContainerItem, SlotItem, UnitItem } from '@/types/warehouse-types';
import { authService } from '../auth/authService';

// Map box status to UI status
const mapBoxStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    'AVAILABLE': 'Verfügbar',
    'IN_USE': 'In Verwendung',
    'RESERVED': 'Reserviert',
    'DAMAGED': 'Beschädigt',
    'RETIRED': 'Ausgemustert'
  };
  
  return statusMap[status] || status;
};

// Map box purpose to UI purpose
const mapBoxPurpose = (purpose: string): string => {
  const purposeMap: Record<string, string> = {
    'STORAGE': 'Lager',
    'PICKING': 'Picken',
    'TRANSPORT': 'Transport',
    'WORKSHOP': 'Werkstatt'
  };
  
  return purposeMap[purpose] || purpose;
};

// Map box type to UI type code
const mapBoxType = (boxType: { id: number; name: string }): string => {
  const typeMap: Record<string, string> = {
    'Karton': 'KA',
    'Behälter': 'BE',
    'Palette': 'PA',
    'Gitterbox': 'GI'
  };
  
  return typeMap[boxType.name] || 'KA';
};

// Format date to match UI format (DD.MM.YYYY)
const formatDate = (date: string | Date): string => {
  if (!date) return '';
  
  const d = new Date(date);
  return d.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

// Format time to match UI format (HH:MM)
const formatTime = (date: string | Date): string => {
  if (!date) return '';
  
  const d = new Date(date);
  return d.toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Cache for box types and their slot configurations
const boxTypeCache = new Map<string, SlotItem[]>();

// Generate slot items based on box type with caching
export const generateSlotItems = (boxType: string, slotCount: number = 6): SlotItem[] => {
  const cacheKey = `${boxType}-${slotCount}`;
  
  if (boxTypeCache.has(cacheKey)) {
    return boxTypeCache.get(cacheKey)!;
  }
  
  const slots: SlotItem[] = [];
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500'];
  
  for (let i = 0; i < slotCount; i++) {
    slots.push({
      id: `${i + 1}`,
      code: {
        code: String.fromCharCode(65 + i),
        color: colors[i % colors.length]
      }
    });
  }
  
  boxTypeCache.set(cacheKey, slots);
  return slots;
};

// Generate initial units for slots
export const generateInitialUnits = (slots: SlotItem[]): UnitItem[] => {
  return [{
    id: '1',
    unitNumber: 1,
    slots: slots.map(slot => slot.id),
    articleNumber: '',
    oldArticleNumber: '',
    description: '',
    stock: 0
  }];
};

// Transform BoxSlot to SlotItem
const transformBoxSlotToSlotItem = (boxSlot: any): SlotItem => {
  return {
    id: boxSlot.id.toString(),
    code: {
      code: boxSlot.slot_code,
      color: boxSlot.occupied ? 'bg-red-200' : 'bg-green-200'
    }
  };
};

// Transform a Box from API to ContainerItem for UI with minimal transformations
export const transformBoxToContainer = (box: Box): ContainerItem => {
  const boxTypeCode = mapBoxType(box.box_type);
  
  // Only generate slots if needed
  let slots: SlotItem[];
  if ((box as BoxWithSlots).slots) {
    // Transform BoxSlot[] to SlotItem[]
    slots = (box as BoxWithSlots).slots.map(transformBoxSlotToSlotItem);
  } else {
    slots = generateSlotItems(boxTypeCode, box.available_slots);
  }
  const units = generateInitialUnits(slots);

  return {
    id: box.id.toString(),
    containerCode: box.containerCode,
    type: boxTypeCode,
    description: box.notes,
    status: mapBoxStatus(box.status),
    purpose: mapBoxPurpose(box.purpose),
    location: box.storage_location ? box.storage_location.name : '',
    slots,
    units,
    stock: 0,
    articleNumber: '',
    oldArticleNumber: '',
    lastPrintDate: null
  };
};

// Fetch boxes with optimized error handling and caching
export const fetchContainers = async (page = 1, pageSize = 20): Promise<{
  containers: ContainerItem[];
  totalCount: number;
  totalPages: number;
}> => {
  try {
    console.log('[DEBUG SERVICE] Starting fetchContainers, page:', page, 'pageSize:', pageSize);
    
    // Get the token first
    const token = await authService.getToken();
    if (!token) {
      window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
      throw new Error('Authentication required. Please log in to view containers.');
    }

    console.log('[DEBUG SERVICE] Token found, calling fetchBoxes');
    const response = await fetchBoxes(page, pageSize);
    console.log('[DEBUG SERVICE] fetchBoxes response received:', response);
    console.log('[DEBUG SERVICE] Number of boxes returned:', response.results ? response.results.length : 0);
    
    // Log complete structure of first box
    if (response.results && response.results.length > 0) {
      console.log('[DEBUG SERVICE] Full first box structure:', JSON.stringify(response.results[0], null, 2));
      console.log('[DEBUG SERVICE] Box properties:', Object.keys(response.results[0]));
    }
    
    const containers = response.results.map(transformBoxToContainer);
    console.log('[DEBUG SERVICE] Transformed containers:', containers.length);
    
    // Log first container to see structure
    if (response.results.length > 0) {
      console.log('[DEBUG SERVICE] First box raw data:', response.results[0]);
      console.log('[DEBUG SERVICE] Box code check:', response.results[0].code);
    }
    
    // Log first transformed container
    if (containers.length > 0) {
      console.log('[DEBUG SERVICE] First transformed container:', containers[0]);
      console.log('[DEBUG SERVICE] Container code check:', containers[0].containerCode);
    }
    
    return {
      containers,
      totalCount: response.total,
      totalPages: response.total_pages
    };
  } catch (error: any) {
    console.error('[DEBUG SERVICE] Error in fetchContainers:', error);
    
    if (error.response?.status === 401) {
      // Try to refresh the token
      const refreshSuccess = await authService.refreshToken();
      if (refreshSuccess) {
        // Retry the request
        return fetchContainers(page, pageSize);
      } else {
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        throw new Error('Your session has expired. Please log in again.');
      }
    }
    
    // Handle other types of errors
    if (error.code === 'ECONNABORTED') {
      throw new Error('The request timed out. Please try again.');
    } else if (!error.response) {
      throw new Error('Could not connect to the server. Please check your internet connection.');
    } else if (error.response.status >= 500) {
      throw new Error('Server error. Please try again later.');
    } else {
      throw new Error(error.message || 'An unexpected error occurred.');
    }
  }
}; 