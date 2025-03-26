import { fetchBoxTypes } from '../inventory/api';
import type { BoxType } from '../inventory/api';
import type { ContainerType } from '../stores/container-type-store';

// Convert BoxType from API to ContainerType for the store
function convertBoxTypeToContainerType(boxType: BoxType): ContainerType {
  return {
    id: boxType.id.toString(),
    name: boxType.name,
    manufacturer: boxType.description?.split(' ')[0] || '', // Assuming first word of description is manufacturer
    articleNumber: '', // Not available in API
    length: boxType.length || 0,
    width: boxType.width || 0,
    height: boxType.height || 0,
    boxWeight: boxType.weight_capacity || 0,
    dividerWeight: 0, // Not available in API
    standardSlots: boxType.slot_count,
    images: [] // Not available in API
  };
}

// Fetch container types from the API
export async function fetchContainerTypes(): Promise<ContainerType[]> {
  try {
    const boxTypes = await fetchBoxTypes();
    return boxTypes.map(convertBoxTypeToContainerType);
  } catch (error) {
    console.error('Error fetching container types:', error);
    throw error;
  }
} 