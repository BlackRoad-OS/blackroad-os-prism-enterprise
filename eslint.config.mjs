/* eslint-env node */
import js from '@eslint/js';
import tsParser from '@typescript-eslint/parser';

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
const ignoredPaths = [
  '.github/**',
  '.tools/**',
  'build/**',
  'coverage/**',
  'dist/**',
  'node_modules/**',
  'public/vendor/**',
  'var/**',
  'connectors.js'
];

export default [
  js.configs.recommended,
  { ignores: ignoredPaths },
  {
    files: ['srv/blackroad-api/server_full.js', 'tests/api_health.test.js', 'tests/git_api.test.js', 'tests/helpers/auth.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        require: 'readonly',
        module: 'readonly',
        __dirname: 'readonly',
        process: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        Buffer: 'readonly',
        setTimeout: 'readonly',
        setInterval: 'readonly'
      }
    },
    rules: {
      'no-unused-vars': 'off',
      'no-empty': 'off'
    }
  },
  {
    files: ['tests/**/*.test.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        require: 'readonly',
        module: 'readonly',
        describe: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly'
      }
    },
    rules: {}
  },
  {
    files: ['packages/flags/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        require: 'readonly',
        module: 'readonly',
        process: 'readonly'
      }
    },
    rules: {}
  },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: sharedGlobals
    },
    rules: sharedRules
  },
  {
    files: ['**/*.cjs'],
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
    files: ['**/*.mjs', '**/postcss.config.js', '**/tailwind.config.js'],
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
    rules: sharedRules
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true }
      },
      globals: {
        ...sharedGlobals,
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        fetch: 'readonly',
        Request: 'readonly',
        Response: 'readonly',
        process: 'readonly',
        require: 'readonly'
      }
    },
    rules: {}
  }
];
