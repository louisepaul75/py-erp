import createMiddleware from 'next-intl/middleware';
import {locales, defaultLocale} from './src/i18n';

export default createMiddleware({
  // A list of all locales that are supported
  locales,

  // If this locale is matched, pathnames work without a prefix (e.g. `/about`)
  defaultLocale,

  // The default locale to use if the user's locale is not supported
  localePrefix: 'as-needed'
});

export const config = {
  // Skip all paths that should not be internationalized
  matcher: ['/((?!api|_next|.*\\..*).*)']
}; 