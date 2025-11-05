<<<<<<< main
/* eslint-env node */
const js = require('@eslint/js');
const tsParser = require('@typescript-eslint/parser');

module.exports = [
  js.configs.recommended,
  {
    files: ['srv/blackroad-api/server_full.js', 'eslint.config.js'],
    files: [
      'srv/blackroad-api/server_full.js',
      'tests/api_health.test.js',
      'tests/git_api.test.js',
      'tests/helpers/auth.js',
    ],
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
        setInterval: 'readonly',
      },
    },
    rules: {
      'no-unused-vars': 'off',
      'no-empty': 'off',
    },
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
        afterAll: 'readonly',
      },
    },
    rules: {},
  },
  {
    files: ['packages/flags/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        require: 'readonly',
        module: 'readonly',
        process: 'readonly',
      },
    },
    rules: {},
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        console: 'readonly',
        window: 'readonly',
        document: 'readonly',
        fetch: 'readonly',
        Request: 'readonly',
        Response: 'readonly',
        process: 'readonly',
        require: 'readonly',
      },
    },
    rules: {},
  },
module.exports = [
  {
    ignores: [
      ".github/**",
      ".tools/**",
      "apps/**",
      "backend/**",
      "build/**",
      "connectors.js",
      "design/**",
      "dist/**",
      "frontend/**",
      "modules/**",
      "node_modules/**",
      "packages/**",
      "public/vendor/**",
      "scripts/**",
      "server_full.js",
      "services/**",
      "sites/**",
      "src/**",
      "srv/**",
      "tests/**",
      "tools/**",
      "var/**"
    ]
  },
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        AbortController: "readonly",
        Buffer: "readonly",
        clearImmediate: "readonly",
        clearInterval: "readonly",
        clearTimeout: "readonly",
        console: "readonly",
        fetch: "readonly",
        FormData: "readonly",
        global: "readonly",
        module: "readonly",
        process: "readonly",
        queueMicrotask: "readonly",
        require: "readonly",
        setImmediate: "readonly",
        setInterval: "readonly",
        setTimeout: "readonly",
        URL: "readonly",
        URLSearchParams: "readonly"
      }
    },
    rules: {
      "no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }
      ],
      "no-undef": "warn"
    }
  }
=======
const sharedGlobals = {
  require: 'readonly',
  module: 'readonly',
  exports: 'readonly',
  __dirname: 'readonly',
  __filename: 'readonly',
  process: 'readonly',
  Buffer: 'readonly',
  console: 'readonly',
  global: 'readonly',
  setTimeout: 'readonly',
  clearTimeout: 'readonly',
  setInterval: 'readonly',
  clearInterval: 'readonly',
  window: 'readonly',
  document: 'readonly',
  navigator: 'readonly',
  fetch: 'readonly',
  FormData: 'readonly',
  Headers: 'readonly',
  Request: 'readonly',
  Response: 'readonly',
  URL: 'readonly',
  AbortController: 'readonly',
  PerformanceObserver: 'readonly',
  TextEncoder: 'readonly',
  TextDecoder: 'readonly',
  localStorage: 'readonly',
  indexedDB: 'readonly',
  WebAssembly: 'readonly',
  WebSocket: 'readonly',
  describe: 'readonly',
  it: 'readonly',
  test: 'readonly',
  expect: 'readonly',
  before: 'readonly',
  after: 'readonly',
  beforeAll: 'readonly',
  afterAll: 'readonly',
  beforeEach: 'readonly',
  afterEach: 'readonly',
  jest: 'readonly',
  cy: 'readonly',
  Cypress: 'readonly',
  alert: 'readonly'
};

const sharedRules = {
  'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
  'no-undef': 'warn'
};

module.exports = [
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      'coverage/**',
      '.github/**',
      '.tools/**',
      'public/vendor/**',
      'var/**',
      'apps/**',
      'backend/**',
      'design/**',
      'frontend/**',
      'modules/**',
      'scripts/**',
      'services/**',
      'sites/**',
      'src/**',
      'srv/**',
      'tests/**',
      'tools/**',
      'connectors.js'
    ]
  },
  {
    files: ['**/*.{js,cjs,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: sharedGlobals
    },
    rules: sharedRules
  },
  {
    files: [
      '**/*.mjs',
      '**/postcss.config.js',
      '**/tailwind.config.js'
    ],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: sharedGlobals
    },
    rules: sharedRules
  }
>>>>>>> origin/codex/fix-all-issues
];
