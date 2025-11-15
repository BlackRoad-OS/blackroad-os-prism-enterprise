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
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        ...nodeGlobals,
        describe: 'readonly',
        test: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
      },
    },
    rules: nodeRules,
  },
];
