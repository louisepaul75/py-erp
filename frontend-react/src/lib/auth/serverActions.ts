'use server';

import { cookies } from 'next/headers';
import { AUTH_CONFIG } from '../config';

export async function getAuthHeaders(request: Request) {
  const cookieStore = cookies();
  const token = cookieStore.get(AUTH_CONFIG.tokenStorage.accessToken)?.value;
  
  if (token) {
    request.headers.set('Authorization', `Bearer ${token}`);
  }
  
  return request;
} 