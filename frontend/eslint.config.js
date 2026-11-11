import js from '@eslint/js'
import reactHooks from 'eslint-plugin-react-hooks'
export default [
  { ignores: ['dist/**', 'public/**', 'node_modules/**'] },
  {
    files: ['**/*.{js,jsx}'], ...js.configs.recommended,
    languageOptions: {
      ecmaVersion: 'latest', sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { Event: 'readonly', fetch: 'readonly', FormData: 'readonly', AbortController: 'readonly', ResizeObserver: 'readonly', setTimeout: 'readonly', clearTimeout: 'readonly', crypto: 'readonly', window: 'readonly', document: 'readonly', navigator: 'readonly', process: 'readonly', console: 'readonly' },
    },
    plugins: { 'react-hooks': reactHooks },
    rules: {
      ...js.configs.recommended.rules,
      'react-hooks/rules-of-hooks': 'error', 'react-hooks/exhaustive-deps': 'error',
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]', argsIgnorePattern: '^_' }],
    },
  },
]
