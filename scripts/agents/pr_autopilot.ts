import { execSync } from 'node:child_process';

const autopilotUser = (process.env.AUTOPILOT_USER || 'blackboxprogramming').trim();
const prNumber = (process.env.PR_NUMBER || '').trim();
const commentAuthor = (process.env.COMMENT_AUTHOR || '').trim();
const actor = (process.env.GITHUB_ACTOR || '').trim();

if (!prNumber) {
  console.log('No pull request number supplied; skipping autopilot.');
  process.exit(0);
}

const triggeredByComment = commentAuthor.length > 0;
if (triggeredByComment) {
  if (commentAuthor === autopilotUser || commentAuthor === 'github-actions[bot]') {
    console.log(
      `Ignoring comment from automation user (${commentAuthor}); avoiding feedback loop.`,
    );
    process.exit(0);
  }

  console.log(
    `Autopilot triggered by comment from ${commentAuthor} on PR #${prNumber}.`,
  );
} else if (actor) {
  console.log(`Autopilot manually dispatched by ${actor} for PR #${prNumber}.`);
} else {
  console.log(`Autopilot triggered for PR #${prNumber}.`);
}

const autopilotMessage = [
  '@codex @copilot @blackboxprogramming @dependabot @asana @linear',
  'review and test the feature branch, set up CI and preview deploy,',
  'run security and dependency scans, and apply comment fixes',
  '',
  '@codex fix comments              # auto-fixes code review comments',
  '@codex apply .github/prompts/codex-fix-comments.md',
  '@codex patch                     # applies code diffs',
  '@codex run tests                 # triggers test suite',
  '@codex ship when green           # queues auto-merge',
  '',
  'And if it receives more comments it does this again and again and again until the open pull requests turns to merged period',
  '',
  'No more user in working copy',
  '',
  '@codex @copilot @blackboxprogramming @dependabot @asana @linear',
  'review and test the feature branch, set up CI and preview deploy,',
  'run security and dependency scans, and apply comment fixes',
  '',
  '@codex fix comments              # auto-fixes code review comments',
  '@codex apply .github/prompts/codex-fix-comments.md',
  '@codex patch                     # applies code diffs',
  '@codex run tests                 # triggers test suite',
  '@codex ship when green           # queues auto-merge',
].join('\n');

const runGh = (command: string, allowFailure = false) => {
  try {
    execSync(command, { stdio: 'inherit' });
    return true;
  } catch (error) {
    if (!allowFailure) {
      console.error(`Command failed: ${command}`);
      console.error(error instanceof Error ? error.message : error);
      process.exit(1);
    }

    console.warn(`Command failed (continuing): ${command}`);
    console.warn(error instanceof Error ? error.message : error);
    return false;
  }
};

runGh(`gh pr comment ${prNumber} --body ${JSON.stringify(autopilotMessage)}`);

// Best-effort: ensure automerge label is present so merge queues once checks pass.
runGh(`gh pr edit ${prNumber} --add-label automerge`, true);

console.log('Autopilot sequence dispatched successfully.');
