# One-shot Orchestrator Superprompt Quickstart

## Overview
The "chef's kiss" orchestrator block introduces a speed-focused, single-call workflow. By sending a single message that includes your candidate seed, SnapIns JSON, and the raw job description (JD), the orchestrator returns an entire application enablement pack as JSON.

## Repository Assets
Use the following source files when validating the flow or onboarding another
teammate:

- [`OneShot_Orchestrator_Superprompt.txt`](./assets/orchestrator/one-shot/OneShot_Orchestrator_Superprompt.txt)
  – Copy/paste this entire prompt into the LLM that will run the chain.
- [`Dummy_JD_Remote_US.txt`](./assets/orchestrator/one-shot/Dummy_JD_Remote_US.txt)
  – Synthetic requisition for dry runs (safe to share internally).
- [`Sample_Output_Pack.json`](./assets/orchestrator/one-shot/Sample_Output_Pack.json)
  – Reference payload showing every field the orchestrator returns:
    - 55-word summary
    - Six tailored bullets (JSON array)
    - Cover letter micro-note
    - Application Q&A (JSON)
    - Identified gaps
    - Resume template variables (JSON)

Keep the sample output handy so you can validate field names and shapes when
wiring downstream automations.

## Running the Flow
1. **Prime the model:** Paste the entire contents of the
   `OneShot_Orchestrator_Superprompt.txt` file into your LLM chat window or API
   call. Do not add extra narration.
2. **Send the three input blocks:** Immediately follow the prompt with the
   candidate seed, SnapIns JSON, and job description. Separate each block with a
   unique delimiter, for example:

   ```text
   <<<CANDIDATE_SEED
   ...persona yaml...
   <<<SNAPINS_JSON
   {...}
   <<<JOB_DESCRIPTION
   ...full JD text...
   ```

   Use the provided dummy JD when you need a safe test input.
3. **Review the response:** The orchestrator returns a single JSON object. Confirm
   the payload matches the structure in `Sample_Output_Pack.json` and that all
   SnapIn identifiers are preserved.
4. **Push to automations:** Feed the JSON into Google Docs, Airtable, or other
   downstream modules. No field renaming should be required.

## Live JD Runs
Ready to test on a live JD? Drop the requisition into the orchestrator to receive
the full pack instantly. For automation walkthroughs, request the Make or Zapier
module configurations to get step-by-step wiring instructions.

## Operational Tips
- When you have a new JD to process, reply with `next` to keep the model in the
  same conversational session.
- Save each output JSON in version control or a shared workspace so you can
  diff changes and track automation quality.
- Sanitize any candidate data before sharing outside the core team.
