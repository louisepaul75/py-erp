import { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { useScreenSize } from '@/utils/responsive';

type NavItem = {
  label: string;
  href: string;
  icon?: React.ElementType;
};

type MobileMenuProps = {
  items: NavItem[];
};

export function MobileMenu({ items }: MobileMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { isMobile, isTablet } = useScreenSize();
  const shouldShow = isMobile || isTablet;

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  if (!shouldShow) return null;

  return (
    <div className="lg:hidden">
      <button 
        onClick={toggleMenu}
        className="p-2 text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50"
        aria-label={isOpen ? "Close menu" : "Open menu"}
      >
        {isOpen ? (
          <X size={24} aria-hidden="true" />
        ) : (
          <Menu size={24} aria-hidden="true" />
        )}
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm">
          <div className="fixed inset-x-0 top-0 z-50 p-6 flex justify-between items-center">
            <div className="font-bold text-xl">pyERP</div>
            <button 
              onClick={toggleMenu}
              className="p-2 text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50"
              aria-label="Close menu"
            >
              <X size={24} aria-hidden="true" />
            </button>
          </div>
          <nav className="fixed inset-x-0 top-16 bottom-0 z-50 overflow-y-auto p-6">
            <ul className="space-y-4">
              {items.map((item) => (
                <li key={item.href}>
                  <Link 
                    href={item.href}
                    className="flex items-center py-2 px-4 text-lg font-medium hover:bg-secondary hover:text-secondary-foreground rounded-md transition-colors duration-200"
                    onClick={toggleMenu}
                  >
                    {item.icon && (
                      <item.icon className="h-5 w-5 mr-3" aria-hidden="true" />
                    )}
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      )}
    </div>
  );
} 