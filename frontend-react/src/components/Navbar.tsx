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
  Menu,
  X,
  Palette
} from 'lucide-react';
import { cn } from '@/lib/utils';
import useTheme from '@/hooks/useTheme';
import useLanguage from '@/hooks/useLanguage';
import LanguageSelector from './LanguageSelector';

// Mock user data - replace with actual auth implementation
const mockUser = {
  name: 'John Doe',
  isAdmin: true
};

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [testMenuOpen, setTestMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { language } = useLanguage();
  const [user, setUser] = useState(mockUser);

  // Toggle dropdown
  const toggleDropdown = () => setIsOpen(!isOpen);

  // Toggle test dropdown
  const toggleTestDropdown = () => setTestMenuOpen(!testMenuOpen);

  // Toggle mobile menu
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);

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

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-md fixed w-full z-10">
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

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
              aria-controls="mobile-menu"
              aria-expanded="false"
              onClick={toggleMobileMenu}
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>

          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex items-center justify-center flex-1">
            <div className="flex space-x-4">
              <NavLink href="/" label="Home" />
              <NavLink href="/products" label="Products" />
              <NavLink href="/sales" label="Sales" />
              <NavLink href="/production" label="Production" />
              <NavLink href="/inventory" label="Inventory" />
              
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
                  <div className="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 focus:outline-none z-20">
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
          <div className="hidden md:flex items-center">
            <div className="ml-3 relative" id="user-dropdown">
              <div>
                <button
                  type="button"
                  className="flex items-center max-w-xs rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  id="user-menu"
                  aria-expanded="false"
                  aria-haspopup="true"
                  onClick={toggleDropdown}
                >
                  <span className="sr-only">Open user menu</span>
                  <div className="flex items-center gap-2">
                    <User className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                    <span className="text-gray-700 dark:text-gray-200">{user.name}</span>
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                  </div>
                </button>
              </div>

              {/* Dropdown menu */}
              {isOpen && (
                <div
                  className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 focus:outline-none"
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
                    {user.isAdmin ? 'Admin Settings' : 'Settings'}
                  </DropdownItem>

                  <DropdownItem href="/logout">
                    <LogOut className="mr-3 h-5 w-5" />
                    Logout
                  </DropdownItem>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu, show/hide based on menu state */}
      {mobileMenuOpen && (
        <div className="md:hidden" id="mobile-menu">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <MobileNavLink href="/" label="Home" />
            <MobileNavLink href="/products" label="Products" />
            <MobileNavLink href="/sales" label="Sales" />
            <MobileNavLink href="/production" label="Production" />
            <MobileNavLink href="/inventory" label="Inventory" />
            
            {/* Mobile Test Dropdown */}
            <div className="relative py-2">
              <button
                onClick={toggleTestDropdown}
                className="w-full flex items-center justify-between px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <span>Test</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${testMenuOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {testMenuOpen && (
                <div className="mt-2 space-y-1 px-3">
                  <MobileDropdownItem href="/ui-components">
                    <Palette className="mr-3 h-5 w-5" />
                    UI Components / Style Guide
                  </MobileDropdownItem>
                  <MobileDropdownItem href="/test/feature1">
                    Feature 1
                  </MobileDropdownItem>
                  <MobileDropdownItem href="/test/feature2">
                    Feature 2
                  </MobileDropdownItem>
                </div>
              )}
            </div>
          </div>
          <div className="pt-4 pb-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center px-5">
              <div className="flex-shrink-0">
                <User className="h-10 w-10 rounded-full text-gray-600 dark:text-gray-300" />
              </div>
              <div className="ml-3">
                <div className="text-base font-medium text-gray-800 dark:text-white">{user.name}</div>
              </div>
            </div>
            <div className="mt-3 px-2 space-y-1">
              <MobileDropdownItem onClick={toggleTheme}>
                {theme === 'dark' ? (
                  <Sun className="mr-3 h-5 w-5" />
                ) : (
                  <Moon className="mr-3 h-5 w-5" />
                )}
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </MobileDropdownItem>
              
              <div className="px-4 py-2 text-base font-medium text-gray-700 dark:text-gray-200">
                <LanguageSelector />
              </div>
              
              <MobileDropdownItem href="/settings">
                <Settings className="mr-3 h-5 w-5" />
                {user.isAdmin ? 'Admin Settings' : 'Settings'}
              </MobileDropdownItem>
              
              <MobileDropdownItem href="/logout">
                <LogOut className="mr-3 h-5 w-5" />
                Logout
              </MobileDropdownItem>
            </div>
          </div>
        </div>
      )}
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

function MobileNavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
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
      className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
      onClick={onClick}
      role="menuitem"
    >
      {children}
    </button>
  );
}

function MobileDropdownItem({ 
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
        className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
      >
        {children}
      </Link>
    );
  }
  
  return (
    <button
      className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export default Navbar; 