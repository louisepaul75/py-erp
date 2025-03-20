'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { 
  Sun, 
  Moon, 
  Settings, 
  LogOut, 
  ChevronDown,
  User,
  Palette
} from 'lucide-react';
import { cn } from '@/lib/utils';
import useTheme from '@/hooks/useTheme';
import LanguageSelector from './LanguageSelector';
import { useLogout } from '@/lib/auth/authHooks';
import useAppTranslation from '@/hooks/useTranslationWrapper';
import { useIsAuthenticated } from '@/lib/auth/authHooks';
import { MobileMenu } from './MobileMenu';
import { useScreenSize } from '@/utils/responsive';

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [testMenuOpen, setTestMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { t } = useAppTranslation();
  const { user } = useIsAuthenticated();
  const logout = useLogout();
  const { isMobile, isTablet } = useScreenSize();

  // Toggle dropdown
  const toggleDropdown = () => setIsOpen(!isOpen);

  // Toggle test dropdown
  const toggleTestDropdown = () => setTestMenuOpen(!testMenuOpen);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const dropdown = document.getElementById('user-dropdown');
      const testDropdown = document.getElementById('test-dropdown');
      
      if (dropdown && !dropdown.contains(event.target as Node)) {
        setIsOpen(false);
      }
      
      if (testDropdown && !testDropdown.contains(event.target as Node)) {
        setTestMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    logout.mutate();
  };

  const navItems = [
    { label: t('navigation.home'), href: '/' },
    { label: t('navigation.products'), href: '/products' },
    { label: t('navigation.sales'), href: '/sales' },
    { label: t('navigation.production'), href: '/production' },
    { label: t('navigation.inventory'), href: '/inventory' },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-md fixed w-full z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <Link href="/">
              <Image 
                src="/wsz_logo_long.png" 
                alt="Wilhelm Schweizer Zinnmanufaktur" 
                width={200} 
                height={50} 
                className="h-10 w-auto"
              />
            </Link>
          </div>

          {/* Mobile menu */}
          <div className="flex items-center lg:hidden">
            <MobileMenu items={navItems} />
          </div>

          {/* Navigation Links - Desktop */}
          <div className="hidden lg:flex items-center justify-center flex-1">
            <div className="flex space-x-4">
              {navItems.map(item => (
                <NavLink key={item.href} href={item.href} label={item.label} />
              ))}
              
              {/* Test dropdown */}
              <div className="relative" id="test-dropdown">
                <button
                  onClick={toggleTestDropdown}
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                >
                  <span>Test</span>
                  <ChevronDown className="ml-1 h-4 w-4" />
                </button>
                
                {testMenuOpen && (
                  <div className="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                    <div className="py-1" role="menu" aria-orientation="vertical">
                      <DropdownItem href="/ui-components">
                        <Palette className="mr-3 h-5 w-5" />
                        UI Components / Style Guide
                      </DropdownItem>
                      <DropdownItem href="/test/feature1">
                        Feature 1
                      </DropdownItem>
                      <DropdownItem href="/test/feature2">
                        Feature 2
                      </DropdownItem>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* User Menu - Desktop */}
          <div className="hidden lg:flex items-center ml-auto">
            <div className="relative" id="user-dropdown">
              <div>
                <button
                  type="button"
                  className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 items-center"
                  id="user-menu"
                  onClick={toggleDropdown}
                >
                  <span className="sr-only">Open user menu</span>
                  <span className="mr-2 text-gray-700 dark:text-gray-200">{user?.username || 'Guest'}</span>
                  <User className="h-8 w-8 rounded-full p-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300" />
                  <ChevronDown className={`ml-1 h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </button>
              </div>

              {isOpen && (
                <div
                  className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu"
                >
                  <DropdownItem onClick={toggleTheme}>
                    {theme === 'dark' ? (
                      <Sun className="mr-3 h-5 w-5" />
                    ) : (
                      <Moon className="mr-3 h-5 w-5" />
                    )}
                    {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                  </DropdownItem>

                  <div className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">
                    <LanguageSelector />
                  </div>

                  <DropdownItem href="/settings">
                    <Settings className="mr-3 h-5 w-5" />
                    {user?.isAdmin ? t('navigation.admin_settings') : t('navigation.settings')}
                  </DropdownItem>

                  <DropdownItem onClick={handleLogout}>
                    <LogOut className="mr-3 h-5 w-5" />
                    Logout
                  </DropdownItem>
                </div>
              )}
            </div>
          </div>

          {/* Mobile user button - only shows icon to save space */}
          {(isMobile || isTablet) && (
            <div className="flex items-center">
              <div className="relative ml-3" id="mobile-user-dropdown">
                <button
                  type="button"
                  className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  onClick={toggleDropdown}
                >
                  <User className="h-8 w-8 rounded-full p-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300" />
                </button>

                {isOpen && (
                  <div
                    className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
                    role="menu"
                    aria-orientation="vertical"
                  >
                    <DropdownItem onClick={toggleTheme}>
                      {theme === 'dark' ? (
                        <Sun className="mr-3 h-5 w-5" />
                      ) : (
                        <Moon className="mr-3 h-5 w-5" />
                      )}
                      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                    </DropdownItem>

                    <div className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200">
                      <LanguageSelector />
                    </div>

                    <DropdownItem href="/settings">
                      <Settings className="mr-3 h-5 w-5" />
                      {t('navigation.settings')}
                    </DropdownItem>

                    <DropdownItem onClick={handleLogout}>
                      <LogOut className="mr-3 h-5 w-5" />
                      Logout
                    </DropdownItem>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
    >
      {label}
    </Link>
  );
}

function DropdownItem({ 
  children, 
  href, 
  onClick 
}: { 
  children: React.ReactNode; 
  href?: string; 
  onClick?: () => void;
}) {
  if (href) {
    return (
      <Link
        href={href}
        className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
        role="menuitem"
      >
        {children}
      </Link>
    );
  }
  
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left block px-4 py-2 text-sm text-gray-700 dark:text-gray-200",
        "hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
      )}
      role="menuitem"
    >
      {children}
    </button>
  );
}

export default Navbar; 