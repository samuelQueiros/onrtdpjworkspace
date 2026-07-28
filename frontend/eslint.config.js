import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist/**'] },
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.flat.recommended.rules,
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // Regras novas do React Compiler exigem refatoração arquitetural; mantemos
      // exhaustive-deps e rules-of-hooks como a linha de base obrigatória.
      'react-hooks/set-state-in-effect': 'off',
      'react-hooks/refs': 'off',
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },
]
