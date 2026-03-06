# Google Sites Setup (for this game website)

Google Sites cannot directly host full custom HTML/JS game files as native pages.
Use this flow:

1. Host this folder publicly (recommended: GitHub Pages).
2. In Google Sites, add buttons or embeds pointing to the hosted URLs.

## Recommended file URLs after hosting
- Home: `https://YOUR_USERNAME.github.io/YOUR_REPO/`
- Geometry Dash Lite: `https://YOUR_USERNAME.github.io/YOUR_REPO/geometry-dash-lite.html`
- Rocket Goal: `https://YOUR_USERNAME.github.io/YOUR_REPO/rocket-goal.html`

## Quick GitHub Pages steps
1. Create a public GitHub repo and upload all files from this folder.
2. In GitHub repo settings, open `Pages`.
3. Set source to `Deploy from a branch`.
4. Choose branch `main` and folder `/ (root)`.
5. Save and wait for the site URL.

## Add to Google Sites
Option A (best):
- Insert -> Button
- Link each button to the game URLs above

Option B:
- Insert -> Embed -> By URL
- Paste the home URL
- If embed is blocked by browser/security headers, use buttons (Option A)
