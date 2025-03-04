import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { liveDesigner } from '@pinegrow/vite-plugin';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '');
  
  // Get API URL from environment variables or use default
  const apiUrl = env.VITE_API_BASE_URL || 'http://localhost:8050/api';
  const apiBaseUrl = apiUrl.replace('/api', '');
  
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
      outDir: '../static/vue',
      // Generate manifest.json in the output directory
      manifest: true,
      // Clean output directory before build
      emptyOutDir: true,
      rollupOptions: {
        // Specify entry points
        input: {
          main: fileURLToPath(new URL('./src/main.ts', import.meta.url))
        },
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
        }
      }
    }
  };
}); 