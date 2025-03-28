'use server';

import { cookies } from 'next/headers';

export async function getServerCookie(key: string): Promise<string | null> {
  const cookieStore = cookies();
  return cookieStore.get(key)?.value ?? null;
}

export async function setServerCookie(key: string, value: string): Promise<void> {
  const cookieStore = cookies();
  cookieStore.set(key, value);
}

export async function deleteServerCookie(key: string): Promise<void> {
  const cookieStore = cookies();
  cookieStore.delete(key);
}

export async function getAllServerCookies(): Promise<Map<string, string>> {
  const cookieStore = cookies();
  const cookieMap = new Map();
  
  for (const cookie of cookieStore.getAll()) {
    cookieMap.set(cookie.name, cookie.value);
  }
  
  return cookieMap;
} 