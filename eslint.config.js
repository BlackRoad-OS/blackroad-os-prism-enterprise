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

module.exports = [
  js.configs.recommended,
  {
    files: [
      'srv/blackroad-api/server_full.js',
      'tests/api_health.test.js',
      'tests/git_api.test.js',
      'tests/helpers/auth.js',
    ],
    files: ['eslint.config.js', 'jest.config.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: nodeGlobals,
    },
    rules: nodeRules,
  },
  {
    files: ['srv/blackroad-api/**/*.js', 'tests/**/*.test.js'],
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
    rules: {},
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      ".github/**",
      "public/vendor/**",
      "var/**",
      "backend/**",
      "frontend/**",
      "sites/**",
      "src/**",
      "srv/**",
      "apps/**",
      "packages/**",
      ".tools/**",
      "modules/**",
      "scripts/**",
      "services/**",
      "design/**",
      "connectors.js"
    ]
    rules: nodeRules,
  },
];
