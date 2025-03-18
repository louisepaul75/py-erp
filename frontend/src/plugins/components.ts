import { App } from 'vue'
import * as components from '@/components/ui'

export default {
  install: (app: App) => {
    // Register all components globally
    Object.entries(components).forEach(([name, component]) => {
      app.component(name, component)
    })
  }
} 