---
name: gen-release-notes
description: Generate release notes for a specific release tag
disable-model-invocation: true
allowed-tools: Bash(gh *)
---

# Generate Release Notes

Generate release notes for the release tag provided as the argument (e.g. `/gen-release-notes 1.2.3`).

If no argument is provided, ask the user which release tag to generate notes for.

## Constraints

- ONLY look at the commit messages between the target tag and the immediately preceding tag.
  Do NOT read any other files, releases, or documentation.
- Keep notes short and proportional to the actual changes. A patch
  with one small fix should produce a few lines, not paragraphs.
- Do NOT escape HTML comment markers. Write `<!--` not `\<!--`.
- Do NOT use HTML entities for quotes. Write `'` not `&#39;`.

## Output Structure

The notes must contain two sections, wrapped in HTML comment markers:

1. **Summary** (between `<!-- SUMMARY -->` and `<!-- /SUMMARY -->`):
   Brief, non-technical, user-facing notes. End users don't care about
   implementation details — focus on what changed from their perspective.
   Keep it as concise as possible.

2. **Technical Details** (between `<!-- TECHNICAL -->` and `<!-- /TECHNICAL -->`):
   More detailed notes for developers. Reference specific components,
   APIs, bug fixes, and behavioral changes. Still concise, but include
   enough detail to be useful for someone reviewing what shipped.

After both sections, append a links section wrapped in `<!-- LINKS -->` / `<!-- /LINKS -->` comment markers.

Example structure:
```
<!-- SUMMARY -->
<b>What's New:</b>
<ul>
<li>Fixed an issue where data could appear duplicated</li>
<li>Improved loading speed of the overview page</li>
</ul>
<!-- /SUMMARY -->
<!-- TECHNICAL -->
<b>Technical Details:</b>
<ul>
<li>Fixed duplicate record processing by deduplicating on unique key</li>
<li>Added database index on <code>table.timestamp</code> to improve query performance</li>
</ul>
<!-- /TECHNICAL -->
<!-- LINKS -->
<b>Full Changelog:</b> <a href="https://github.com/{owner}/{repo}/compare/1.0.0...1.0.1">1.0.0...1.0.1</a>
<a href="https://github.com/{owner}/{repo}/releases/tag/1.0.1">View full release notes on GitHub</a>
<!-- /LINKS -->
```

## Formatting Requirements

The notes will be consumed by a chat integration. They must:

- Use valid HTML only — no markdown. Use tags like `<b>`, `<i>`, `<a href="...">`, `<br>`, `<code>`, and `<ul>`/`<li>` for structure.
- Be valid for embedding in a JSON string — the workflow will handle any necessary JSON escaping. Do not include literal newline characters inside HTML tag content; use `<br>` tags or HTML block elements (`<ul>`, `<li>`, `<p>`) for line breaks and structure instead. Newlines between HTML tags (for readability) are fine.
- Avoid any characters or sequences that would break JSON parsing (e.g., unescaped control characters, tabs).

## Steps

1. Find the tag immediately before the target tag by running:
   `gh release list --json tagName --limit 20 --jq '.[].tagName'`
   and picking the entry right after the target tag in that list.
2. Get the commit messages between the two tags:
   `gh api repos/{owner}/{repo}/compare/{previous_tag}...{target_tag} --jq '.commits[].commit.message'`
   This is your ONLY source of truth for what changed.
3. Write the two-section release notes based on those commit messages.
4. Append a links section wrapped in `<!-- LINKS -->` / `<!-- /LINKS -->` comment markers containing a full changelog link and a release link in this exact format:
   ```
   <!-- LINKS -->
   <b>Full Changelog:</b> <a href="https://github.com/{owner}/{repo}/compare/{previous_tag}...{target_tag}">{previous_tag}...{target_tag}</a>
   <a href="https://github.com/{owner}/{repo}/releases/tag/{target_tag}">View full release notes on GitHub</a>
   <!-- /LINKS -->
   ```
5. Present the notes for review. Show both the raw HTML and a summary. Ask the user to approve or request changes before publishing.
6. Once approved, update the release with:
   `gh release edit {target_tag} --notes <notes>`
