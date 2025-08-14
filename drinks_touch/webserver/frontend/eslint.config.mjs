// @ts-check

import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended'

import withNuxt from './.nuxt/eslint.config.mjs'

const prettierConfiguration = eslintPluginPrettierRecommended

export default withNuxt([prettierConfiguration])
