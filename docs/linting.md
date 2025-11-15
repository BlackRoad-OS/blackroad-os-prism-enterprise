# Linting Workflow

The repository uses the [ESLint flat config](https://eslint.org/docs/latest/use/configure/configuration-files-new) that lives at
`eslint.config.mjs`. The config imports `@eslint/js` and `eslint-config-prettier`, so both packages (plus `eslint` itself) are
pinned in the root `package.json` under `devDependencies`.

## Installing the tooling

Most contributors will run one of the existing bootstrap helpers, which already handles dependency installation:

1. `bash ops/install.sh` — detects the API directory (where `server_full.js` and `package.json` live) and invokes
   `node tools/dep-scan.js --dir <api> --save` so the lint packages are hydrated together with runtime dependencies.
2. `node tools/dep-scan.js --dir <api> --save` — if you prefer to run the scanner manually, execute it from the API directory
   (the root of this repository for the current setup). This keeps the dependency workflow consistent with the hygiene policy.

If neither helper is available (for example in CI where dependencies are already vendored), you can still fall back to the
standard npm command:

```bash
npm install --save-dev eslint @eslint/js eslint-config-prettier
```

## Running lint checks

After the dependencies are installed, run the existing script:

```bash
npm run lint
```

The script uses `eslint . --ext .js,.jsx,.mjs,.cjs` to lint both the CommonJS API sources and the new ESM-based tooling files.
