/* eslint-env node */
const js = require('@eslint/js');

const nodeGlobals = {
  require: 'readonly',
  module: 'readonly',
  __dirname: 'readonly',
  process: 'readonly',
  console: 'readonly',
  Buffer: 'readonly',
  fetch: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
};

const nodeRules = {
  'no-empty': ['error', { allowEmptyCatch: true }],
};

const repoIgnores = [
  'node_modules',
  '_trash',
  '.github/**',
  'apps/**',
  'backend/**',
  'build/**',
  'connectors.js',
  'design/**',
  'dist/**',
  'frontend/**',
  'modules/**',
  'packages/**',
  'public/vendor/**',
  'scripts/**',
  'services/**',
  'sites/**',
  'tools/**',
  'var/**',
];

module.exports = [
  { ignores: repoIgnores },
  js.configs.recommended,
  {
    files: [
      'eslint.config.js',
      'jest.config.js',
      'srv/blackroad-api/server_full.js',
      'srv/blackroad-api/routes/git.js',
      'tests/api_health.test.js',
      'tests/git_api.test.js',
      'tests/helpers/auth.js',
    ],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: nodeGlobals,
    },
    rules: nodeRules,
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
      "services/**",
      "sites/**",
      "src/**",
      "srv/**",
      "tools/**",
      "var/**"
    ]
  },
  {
    files: ['srv/blackroad-api/**/*.js', 'tests/**/*.js'],
    files: ['srv/blackroad-api/**/*.js', 'tests/**/*.test.js'],
  {
    ignores: ['node_modules/**', '_trash/**'],
  },
  js.configs.recommended,
  {
    files: [
      'srv/blackroad-api/**/*.js',
      'backend/**/*.js',
      'tests/**/*.js',
      'jest.config.js',
      'eslint.config.js',
    ],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        ...nodeGlobals,
        require: 'readonly',
        module: 'readonly',
        __dirname: 'readonly',
        process: 'readonly',
        global: 'readonly',
        describe: 'readonly',
        test: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        Buffer: 'readonly',
      },
    },
    rules: {
      'no-empty': ['error', { allowEmptyCatch: true }],
    },
  },
  {
    files: ['*.config.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        require: 'readonly',
        module: 'readonly',
      },
    },
    rules: nodeRules,
  },
module.exports = [
  {
    ignores: ["node_modules/", "dist/", "build/", ".github/", "public/vendor/"]
  },
  {
    files: ["**/*.{js,jsx,mjs,cjs}", "**/*.ts", "**/*.tsx"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "commonjs"
    },
    rules: {
      "no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }
      ],
      "no-undef": "warn"
    }
  }
const commonGlobals = {
  console: "readonly",
  setTimeout: "readonly",
  clearTimeout: "readonly",
  setInterval: "readonly",
  clearInterval: "readonly",
  fetch: "readonly",
  Headers: "readonly",
  Request: "readonly",
  Response: "readonly",
};

const browserGlobals = {
  window: "readonly",
  document: "readonly",
  navigator: "readonly",
  location: "readonly",
};

const nodeGlobals = {
  require: "readonly",
  module: "readonly",
  exports: "readonly",
  __dirname: "readonly",
  __filename: "readonly",
  process: "readonly",
  Buffer: "readonly",
};

const testGlobals = {
  describe: "readonly",
  it: "readonly",
  test: "readonly",
  expect: "readonly",
  beforeAll: "readonly",
  afterAll: "readonly",
  beforeEach: "readonly",
  afterEach: "readonly",
  jest: "readonly",
};

module.exports = [
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      "coverage/**",
      "public/**",
      "var/**",
      "srv/**",
      "apps/**",
      "frontend/**",
      "sites/**",
      "design/**",
      "src/**",
      "tests/**",
      "modules/**",
      "prism-web/**",
      "services/**",
      "scripts/**",
      ".cache/**",
      "**/*.min.js",
    ],
  },
  {
    files: ["**/*.{js,jsx,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...commonGlobals,
        ...browserGlobals,
        ...testGlobals,
      },
    },
    rules: {
      "no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrors: "none",
        },
      ],
    },
  },
  {
    files: [
      "backend/**/*.js",
      "agents/**/*.js",
      "connectors.js",
  ],
    languageOptions: {
      sourceType: "commonjs",
      globals: {
        ...commonGlobals,
        ...nodeGlobals,
        ...testGlobals,
        it: 'readonly',
        jest: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        Buffer: 'readonly',
        setInterval: 'readonly',
      },
    },
  },
];
