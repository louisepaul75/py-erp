import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head />
      <script dangerouslySetInnerHTML={{
        __html: `
          (function() {
            // Patch Node.prototype.textContent to catch errors
            try {
              // Store original descriptor
              var originalDescriptor = Object.getOwnPropertyDescriptor(Node.prototype, 'textContent');
              
              if (originalDescriptor && originalDescriptor.get) {
                var originalGetter = originalDescriptor.get;
                
                // Replace with safe getter
                Object.defineProperty(Node.prototype, 'textContent', {
                  get: function() {
                    try {
                      return originalGetter.call(this);
                    } catch (e) {
                      console.warn('Prevented textContent error:', e);
                      return '';
                    }
                  },
                  set: originalDescriptor.set,
                  configurable: true,
                  enumerable: true
                });
                
                console.log('Node.prototype.textContent patched successfully');
              }
            } catch (e) {
              console.error('Failed to patch textContent:', e);
            }
          })();
        `
      }} />
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
} 