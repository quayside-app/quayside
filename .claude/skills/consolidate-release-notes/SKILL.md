---
name: consolidate-release-notes
description: Consolidate multiple draft GitHub releases into a single set of release notes
disable-model-invocation: true
allowed-tools: Bash(gh *)
---

# Consolidate Release Notes

Find any draft releases created since the last published release. Generate consolidated release notes by combining the individual draft notes and GitHub diffs across all drafts. The consolidated notes replace the per-version drafts with a single set of notes on the most recent draft, covering everything since the last published release.

Note: Each individual draft release already has AI-generated notes containing summary and technical sections. Your job is to consolidate across multiple drafts — deduplicating, grouping related changes, and producing a cohesive result.

## Output Structure

The notes must contain two sections, wrapped in HTML comment markers:

1. **Summary** (between `<!-- SUMMARY -->` and `<!-- /SUMMARY -->`): Brief, non-technical, user-facing notes. End users don't care about implementation details — focus on what changed from their perspective. Keep it as concise as possible.

2. **Technical Details** (between `<!-- TECHNICAL -->` and `<!-- /TECHNICAL -->`): More detailed notes for developers. Reference specific components, APIs, bug fixes, and behavioral changes. Still concise, but include enough detail to be useful for someone reviewing what shipped.

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
<b>Full Changelog:</b> <a href="https://github.com/{owner}/{repo}/compare/1.0.0...1.0.3">1.0.0...1.0.3</a>
<a href="https://github.com/{owner}/{repo}/releases/tag/1.0.3">View full release notes on GitHub</a>
<!-- /LINKS -->
```

## Formatting Requirements

The release notes body will be consumed by a chat integration. The notes must:

- Use valid HTML only — no markdown. Use tags like `<b>`, `<i>`, `<a href="...">`, `<br>`, `<code>`, and `<ul>`/`<li>` for structure.
- Be valid for embedding in a JSON string — the workflow will handle any necessary JSON escaping. Do not include literal newline characters inside HTML tag content; use `<br>` tags or HTML block elements (`<ul>`, `<li>`, `<p>`) for line breaks and structure instead. Newlines between HTML tags (for readability) are fine.
- Avoid any characters or sequences that would break JSON parsing (e.g., unescaped control characters, tabs).

## Steps

1. Use `gh release list` to identify the last published release and any draft releases created after it.
2. For each draft release, fetch its notes with `gh release view <tag> --json body`.
3. Get the diff between each consecutive pair of release tags using `gh api repos/{owner}/{repo}/compare/{base}...{head}` to understand what changed.
4. Synthesize all draft notes and diffs into a single consolidated set of release notes following the two-section structure above. Deduplicate and group related changes. When multiple patches address the same feature or fix (e.g., a feature is added in one release and then fixed/refined in subsequent patches), consolidate them into a single item describing the final state — users don't need to see the intermediate iterations.
5. Keep the summary language non-technical and concise — focus on what changed from the user's perspective, not implementation details. If a feature was added and then fixed across multiple releases, present it as a single working feature, not as "added X" followed by "fixed X".
6. Append a links section wrapped in `<!-- LINKS -->` / `<!-- /LINKS -->` comment markers containing a full changelog link and a release link in this exact format, where `{base}` is the last published release tag and `{head}` is the most recent draft release tag:
   ```
   <!-- LINKS -->
   <b>Full Changelog:</b> <a href="https://github.com/{owner}/{repo}/compare/{base}...{head}">{base}...{head}</a>
   <a href="https://github.com/{owner}/{repo}/releases/tag/{head}">View full release notes on GitHub</a>
   <!-- /LINKS -->
   ```
7. Present the consolidated notes for review. Show both a rendered markdown version (for readability) and the raw HTML version that will be published. Ask the user to approve or request changes before proceeding.
8. Once approved, update the most recent draft release with the consolidated notes using `gh release edit <tag> --notes <notes>`.
