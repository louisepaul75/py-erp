import { Box, BoxType, PaginatedResponse, fetchBoxes, fetchBoxTypes, fetchStorageLocations } from './api';
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

// Generate slot items based on box type
export const generateSlotItems = (boxType: string, slotCount: number = 6): SlotItem[] => {
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

// Transform a Box from API to ContainerItem for UI
export const transformBoxToContainer = (box: Box): ContainerItem => {
  // Generate proper slots based on box type
  const boxTypeCode = mapBoxType(box.box_type);
  const slotCount = box.available_slots;
  const slots = generateSlotItems(boxTypeCode, slotCount);
  const units = generateInitialUnits(slots);

  return {
    id: box.id.toString(),
    containerCode: box.code,
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

// Fetch boxes and transform them to UI format
export const fetchContainers = async (page = 1, pageSize = 20): Promise<{
  containers: ContainerItem[];
  totalCount: number;
  totalPages: number;
}> => {
  try {
    // Check if user is authenticated
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated. Please log in to view containers.');
    }

    const response: PaginatedResponse<Box> = await fetchBoxes(page, pageSize);
    
    const containers = response.results.map(transformBoxToContainer);
    
    return {
      containers,
      totalCount: response.total,
      totalPages: response.total_pages
    };
  } catch (error: any) { // Type assertion to handle axios error
    console.error('Error fetching containers:', error);

    // Handle network errors
    if (!error.response) {
      throw new Error('Network error or server not responding. Please check your connection and try again.');
    }

    // Handle authentication errors
    if (error.response?.status === 401) {
      try {
        const newToken = await authService.refreshToken();
        if (newToken) {
          // Retry the request with new token
          const response: PaginatedResponse<Box> = await fetchBoxes(page, pageSize);
          const containers = response.results.map(transformBoxToContainer);
          return {
            containers,
            totalCount: response.total,
            totalPages: response.total_pages
          };
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        authService.logout();
        window.location.href = '/login';
        throw new Error('Authentication failed. Please log in again.');
      }
    }

    // Handle other HTTP errors
    if (error.response?.status === 404) {
      throw new Error('The requested resource was not found.');
    } else if (error.response?.status === 403) {
      throw new Error('You do not have permission to access this resource.');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    }

    // Handle any other errors
    throw error;
  }
}; 