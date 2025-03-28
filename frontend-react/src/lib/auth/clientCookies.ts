import Cookies from 'js-cookie';

export const clientCookieStorage = {
  getItem: (key: string): string | null => {
    return Cookies.get(key) ?? null;
  },
  
  setItem: (key: string, value: string): void => {
    Cookies.set(key, value, {
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict'
    });
  },
  
  removeItem: (key: string): void => {
    Cookies.remove(key);
  }
}; 