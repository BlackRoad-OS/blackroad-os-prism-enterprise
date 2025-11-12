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
];
