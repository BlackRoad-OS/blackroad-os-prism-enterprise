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
    rules: nodeRules,
  },
];
