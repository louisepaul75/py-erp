'use client';

import { useState } from 'react';
import { Globe } from 'lucide-react';
import useLanguage from '@/hooks/useLanguage';

type LanguageOption = {
  code: 'en' | 'de' | 'fr' | 'es';
  name: string;
  flag: string;
};

const languages: LanguageOption[] = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
];

export function LanguageSelector() {
  const { language, changeLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleLanguageChange = (code: 'en' | 'de' | 'fr' | 'es') => {
    changeLanguage(code);
    setIsOpen(false);
  };

  const currentLanguage = languages.find(lang => lang.code === language) || languages[0];

  return (
    <div className="relative">
      <div 
        className="flex items-center cursor-pointer" 
        onClick={toggleDropdown}
      >
        <Globe className="mr-3 h-5 w-5" />
        <span>{currentLanguage.flag} {currentLanguage.name}</span>
      </div>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
          {languages.map((lang) => (
            <div
              key={lang.code}
              className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
              onClick={() => handleLanguageChange(lang.code)}
            >
              <span className="mr-2">{lang.flag}</span>
              <span>{lang.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default LanguageSelector; 