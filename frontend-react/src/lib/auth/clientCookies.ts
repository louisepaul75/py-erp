import Cookies from 'js-cookie';

export const clientCookieStorage = {
  getItem: (key: string): string | null => {
    return Cookies.get(key) ?? null;
  },
  
  setItem: (key: string, value: string): void => {
    Cookies.set(key, value, {
      secure: true,
      sameSite: 'strict',
      path: '/',
      expires: 7
    });
  },
  
  removeItem: (key: string): void => {
    Cookies.remove(key, {
      path: '/',
      secure: true,
      sameSite: 'strict'
    });
  }
}; 