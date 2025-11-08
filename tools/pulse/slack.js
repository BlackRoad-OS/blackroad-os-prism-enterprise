// tools/pulse/slack.js
// Usage: node tools/pulse/slack.js pulses/SYS-PERF-YYYY-WW.md "$SLACK_WEBHOOK_URL"
import fs from "node:fs";

const file = process.argv[2];
const url = process.argv[3];
if (!file || !url) {
  console.error("Usage: node tools/pulse/slack.js <pulse.md> <SLACK_WEBHOOK_URL>");
  process.exit(2);
}
const text = fs.readFileSync(file, "utf8").slice(0, 3000); // Slack limit-ish
const payload = { text: `*${file}*\n${text}` };

const res = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});
if (!res.ok) {
  console.error("Slack post failed:", res.status, await res.text());
  process.exit(1);
}
console.log("Posted to Slack:", file);
