---
name: screenshot-pr
description: Take Playwright screenshots of key UI pages and attach them to the current PR as a comment
---

# Screenshot PR

Take screenshots of the running app using Playwright and post them as a comment on the current open PR for this branch.

## Steps

1. **Authenticate** — navigate to `http://localhost:8000/dev-login/?next=/` to set the session cookie.

2. **Identify pages to screenshot** — use the pages provided as arguments (e.g. `/screenshot-pr /projects/123`). If no pages are given, screenshot the following defaults:
   - `/` — home / dashboard
   - Any page that is directly relevant to the current branch's changes (infer from the branch name or recent commits)

3. **Take screenshots** — for each page:
   - Navigate to `http://localhost:8000{path}`
   - Take a full-page screenshot and save it to `.playwright-mcp/`
   - Note the filename

4. **Upload images to the PR** — GitHub PR comments don't accept file attachments via `gh` CLI directly. Instead:
   - Use `gh pr view --json number` to get the PR number
   - For each screenshot, encode it as a base64 data URI or upload it using the GitHub API:
     ```
     gh api repos/{owner}/{repo}/issues/{pr_number}/comments \
       --method POST \
       --field body="## UI Screenshots\n\n![screenshot]({image_url})"
     ```
   - Since GitHub doesn't host arbitrary images via the API, the practical approach is to upload each image as a file to the PR's associated commit using the GitHub API, or post the raw screenshots inline by uploading them to the repo temporarily.

   **Preferred approach:** Use `gh pr comment` with the screenshots embedded as markdown image references. Because GitHub auto-hosts images dragged into comments but not via CLI, instead:
   - Post a PR comment with the screenshots using the GitHub CLI:
     ```
     gh pr comment --body "$(cat <<'EOF'
     ## UI Screenshots
     <!-- screenshots attached below -->
     EOF
     )"
     ```
   - Then upload each screenshot file to the GitHub PR using the API to create a gist, or attach via the issue comment upload endpoint.

   **Simplest working approach:**
   - Upload each image to a new GitHub Gist (public), get the raw URL, and embed in the PR comment.
     ```
     gh gist create --public .playwright-mcp/{filename}.png --desc "UI screenshot for PR"
     ```
   - Get the raw gist URL and embed it in the PR comment body.

5. **Post the PR comment** with all screenshots embedded as markdown images:
   ```
   gh pr comment --body "## UI Screenshots\n\n**Home page:**\n![home](https://...)"
   ```

6. **Show the screenshots** to the user inline in the conversation so they can see them without leaving the terminal.

## Notes

- The dev server must be running at `http://localhost:8000` for this to work.
- The `devLogin` endpoint only works when `DEBUG=True`.
- Screenshots are saved locally to `.playwright-mcp/` regardless of whether the PR upload succeeds.
- If no PR exists for the current branch yet, say so and show the screenshots in the conversation only.
