import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { liveDesigner } from '@pinegrow/vite-plugin';
import os from 'node:os';

// Function to get the local IP address
function getLocalIpAddress() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Skip over non-IPv4 and internal (loopback) addresses
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost'; // Fallback to localhost
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '');

  // Get the local IP address
  const localIpAddress = getLocalIpAddress();
  const isSpecificIP = localIpAddress === '192.168.73.65';

  // Determine if we're running in a local development environment
  const isLocalDev = process.env.NODE_ENV === 'development' &&
                    (!process.env.VITE_API_HOST || process.env.VITE_API_HOST === 'localhost');

  // Get API URL based on the detected IP
  let apiUrl;
  if (isSpecificIP) {
    apiUrl = 'http://192.168.73.65:8050';
  } else if (isLocalDev) {
    apiUrl = 'http://localhost:8050';
  } else {
    apiUrl = env.VITE_API_NETWORK_URL || env.VITE_API_BASE_URL || 'http://localhost:8050';
  }

  const apiBaseUrl = apiUrl && apiUrl.endsWith('/api') ? apiUrl.slice(0, -4) : apiUrl;

  console.log('Mode:', mode);
  console.log('Environment:', process.env.NODE_ENV);
  console.log('Local IP Address:', localIpAddress);
  console.log('Is Specific IP (192.168.73.65):', isSpecificIP);
  console.log('API Base URL:', apiBaseUrl);
  console.log('Is Local Development:', isLocalDev);

  return {
    plugins: [
      liveDesigner({
        // Customize plugin options as needed
      }),
      vue()
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      // Output directory for production build
      outDir: 'dist',
      // Generate manifest.json in the output directory
      manifest: true,
      // Clean output directory before build
      emptyOutDir: true,
      rollupOptions: {
        // Use index.html as the entry point
        input: fileURLToPath(new URL('./index.html', import.meta.url)),
        output: {
          // Configure output filenames
          entryFileNames: 'js/[name].[hash].js',
          chunkFileNames: 'js/[name].[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.');
            const ext = info[info.length - 1];
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name)) {
              return `img/[name].[hash].[ext]`;
            }
            if (/\.(css)$/.test(assetInfo.name)) {
              return `css/[name].[hash].[ext]`;
            }
            if (/\.(woff|woff2|eot|ttf|otf)$/.test(assetInfo.name)) {
              return `fonts/[name].[hash].[ext]`;
            }
            return `[name].[hash].[ext]`;
          }
        }
      }
    },
    server: {
      // Development server configuration
      host: '0.0.0.0',
      port: 3000,
      // Proxy API requests to Django server
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true
        },
        '/v1': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/v1/, '/api/v1')
        },
        '/products': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/products/, '/api/products')
        },
        '/sales': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/sales/, '/api/sales')
        },
        '/token': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/token/, '/api/token')
        }
      }
    }
  };
});
