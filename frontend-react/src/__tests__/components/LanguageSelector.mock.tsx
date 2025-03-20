/**
 * @jest-environment jsdom
 * @jest-skip - This is a mock component used in tests, not a test suite
 * 
 * This is a mock component for LanguageSelector used in tests.
 * It is not a test file itself.
 */

import React from 'react';

const LanguageSelector = () => {
  return (
    <div data-testid="language-selector-mock">
      <button>English</button>
      <button>German</button>
    </div>
  );
};

export default LanguageSelector; 