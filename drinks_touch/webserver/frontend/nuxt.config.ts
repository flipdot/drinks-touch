import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  css: ['~/assets/css/app.css'],
  devtools: { enabled: true },
  modules: ['@nuxt/eslint', '@nuxt/fonts'],
  vite: {
    optimizeDeps: {
      include: ['d3'],
    },
    plugins: [tailwindcss()],
  },

  // modules
  eslint: {
    config: {
      typescript: true,
    },
  },
})
