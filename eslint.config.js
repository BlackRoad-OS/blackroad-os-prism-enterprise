/* eslint-env node */
const js = require('@eslint/js');

module.exports = [
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
        require: 'readonly',
        module: 'readonly',
        __dirname: 'readonly',
        process: 'readonly',
        global: 'readonly',
        describe: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        it: 'readonly',
        jest: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        Buffer: 'readonly',
        setInterval: 'readonly',
      },
    },
    rules: {},
  },
];
