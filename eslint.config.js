/* eslint-env node */
const js = require('@eslint/js');
const tsParser = require('@typescript-eslint/parser');

const sharedGlobals = {
  AbortController: 'readonly',
  Buffer: 'readonly',
  clearImmediate: 'readonly',
  clearInterval: 'readonly',
  clearTimeout: 'readonly',
  console: 'readonly',
  fetch: 'readonly',
  FormData: 'readonly',
  global: 'readonly',
  module: 'readonly',
  process: 'readonly',
  queueMicrotask: 'readonly',
  require: 'readonly',
  setImmediate: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
  URL: 'readonly',
  URLSearchParams: 'readonly',
};

const testGlobals = {
  ...sharedGlobals,
  after: 'readonly',
  afterAll: 'readonly',
  afterEach: 'readonly',
  before: 'readonly',
  beforeAll: 'readonly',
  beforeEach: 'readonly',
  describe: 'readonly',
  expect: 'readonly',
  it: 'readonly',
  jest: 'readonly',
  test: 'readonly',
  cy: 'readonly',
  Cypress: 'readonly',
};

module.exports = [
  js.configs.recommended,
  {
    ignores: [
      '.github/**',
      '.tools/**',
      'apps/**',
      'build/**',
      'design/**',
      'dist/**',
      'frontend/**',
      'modules/**',
      'node_modules/**',
      'packages/**',
      'public/vendor/**',
      'scripts/**',
      'services/**',
      'sites/**',
      'src/**',
      'tools/**',
      'var/**',
    ],
  },
  {
    files: ['srv/blackroad-api/**/*.js', 'eslint.config.js', 'os/**/*.js', 'scripts/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: sharedGlobals,
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'no-undef': 'warn',
    },
  },
  {
    files: ['tests/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: testGlobals,
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    },
  },
  {
    files: ['**/*.mjs'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: testGlobals,
    },
  },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: {
        ...sharedGlobals,
        document: 'readonly',
        window: 'readonly',
      },
    },
  },
];
