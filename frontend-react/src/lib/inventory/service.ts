import { Box, BoxType, PaginatedResponse, fetchBoxes, fetchBoxTypes, fetchStorageLocations } from './api';
import { ContainerItem, SlotItem, UnitItem } from '@/types/warehouse-types';

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

// Map box type from API to UI type
const mapBoxType = (boxType: BoxType | { id: number; name: string }): string => {
  // Extract the first two letters from the box type name as the code
  if (!boxType.name) return 'AR'; // Default type
  
  const typeCode = boxType.name.substring(0, 2).toUpperCase();
  return typeCode;
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

// Generate slot items for a box based on box type
export const generateSlotItems = (boxType: string, slotCount: number = 6): SlotItem[] => {
  const slots: SlotItem[] = [];
  
  // Determine slot color based on box type
  let colorClass = 'bg-blue-500';
  switch (boxType) {
    case 'AR':
      colorClass = 'bg-blue-500';
      break;
    case 'KC':
      colorClass = 'bg-green-500';
      break;
    case 'PT':
      colorClass = 'bg-yellow-500';
      break;
    case 'OD':
      colorClass = 'bg-red-500';
      break;
    case 'JK':
      colorClass = 'bg-purple-500';
      break;
    case 'HF':
      colorClass = 'bg-gray-500';
      break;
    default:
      colorClass = 'bg-blue-500';
  }
  
  // Generate slot codes based on pattern (A1, A2, B1, B2, etc.)
  const columns = ['A', 'B', 'C', 'D', 'E', 'F'];
  const rows = ['1', '2', '3', '4', '5', '6'];
  
  for (let i = 0; i < slotCount; i++) {
    const col = Math.floor(i / rows.length);
    const row = i % rows.length;
    
    const code = `${columns[col] || 'X'}${rows[row] || '0'}`;
    
    slots.push({
      id: `slot-${i + 1}`,
      code: {
        code,
        color: colorClass
      }
    });
  }
  
  return slots;
};

// Generate initial units from slots
export const generateInitialUnits = (slots: SlotItem[]): UnitItem[] => {
  // Create one unit with all slots
  const unit: UnitItem = {
    id: `unit-1`,
    unitNumber: 1,
    slots: slots.map(slot => slot.id),
    articleNumber: '',
    oldArticleNumber: '',
    description: '',
    stock: 0
  };
  
  return [unit];
};

// Transform a Box from API to ContainerItem for UI
export const transformBoxToContainer = (box: Box): ContainerItem => {
  // Generate a 5-6 character random code for UI display
  const generateRandomCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    let result = '';
    for (let i = 0; i < 3; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    for (let i = 0; i < 3; i++) {
      result += numbers.charAt(Math.floor(Math.random() * numbers.length));
    }
    return result;
  };

  // Generate proper slots based on box type
  const boxTypeCode = mapBoxType(box.box_type);
  const slotCount = box.box_type.slot_count || 6;
  const slots = generateSlotItems(boxTypeCode, slotCount);
  const units = generateInitialUnits(slots);

  return {
    id: box.id.toString(),
    containerCode: box.code,
    displayCode: generateRandomCode(),
    type: boxTypeCode,
    description: box.notes || '',
    status: mapBoxStatus(box.status),
    purpose: mapBoxPurpose(box.purpose),
    location: box.storage_location ? box.storage_location.name : '',
    shelf: Math.floor(Math.random() * 10) + 1, // Placeholder
    compartment: Math.floor(Math.random() * 10) + 1, // Placeholder
    floor: Math.floor(Math.random() * 3) + 1, // Placeholder
    stock: 0,
    articleNumber: '',
    oldArticleNumber: '',
    lastPrintDate: null,
    slots,
    units
  };
};

// Fetch boxes and transform them to UI format
export const fetchContainers = async (page = 1, pageSize = 10): Promise<{
  containers: ContainerItem[];
  totalCount: number;
  totalPages: number;
}> => {
  try {
    const response: PaginatedResponse<Box> = await fetchBoxes(page, pageSize);
    
    const containers = response.results.map(transformBoxToContainer);
    
    return {
      containers,
      totalCount: response.total,
      totalPages: response.total_pages
    };
  } catch (error) {
    console.error('Error fetching containers:', error);
    throw error;
  }
}; 