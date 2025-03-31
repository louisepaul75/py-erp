/**
 * Validate a mold number to ensure it follows the format F1xxxx
 * where xxxx is a 4-digit number
 */
export function validateMoldNumber(moldNumber: string): boolean {
  const regex = /^F1\d{4}$/
  return regex.test(moldNumber)
}

