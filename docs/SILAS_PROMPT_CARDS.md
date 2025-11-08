# Silas Prompt Cards

A lightweight viewer for the Silas prompt cards that ship with this repository.

## Run the preview

```bash
npm --prefix ui/prompt_cards run preview
```

The static server listens on <http://localhost:5173>. It serves the compiled `index.html` alongside
`cards.json` so you can inspect the content locally without any external dependencies.

## Files

- `ui/prompt_cards/index.html` – renders the cards and colourises the token chips.
- `ui/prompt_cards/cards.json` – structured data describing each prompt card.
- `ui/prompt_cards/preview.js` – zero-dependency Node preview server.
- `ui/prompt_cards/package.json` – npm script entry point.

The dataset intentionally avoids build tooling so the viewer works in any environment with Node 18+
installed.
