# AutoScrape24

A React-based web application for visualizing car sale listings by mileage and price.

## Features

- Customizable scatter plot using D3.js (data loaded from the workspace `listings-json` directory via Vite imports)
- Independent zoom/drag on X/Y axes
- Resizable layout with draggable dividers separating panes (columns & rows)
- Directory tree for makes/models
- Filters for price, mileage, age range, fuel type, seller, and distance (slider/checkbox UI)
- Light-mode JetBrains-style UI

## Getting Started

```sh
cd AutoScrape24
npm install
npm run dev
```

The app will open in your browser.

This is a starting point. You can hook the graph up to real listing data and expand components as needed.

## Deployment (GitHub Pages)

This repository serves GitHub Pages from the `gh-pages` branch root (not from source files in `AutoScrape24/src`).

When app code or data changes, rebuild and publish the generated static files to `gh-pages`.

### Standard deployment flow

From the repository root:

```sh
# 1) Ensure gh-pages worktree exists
git worktree prune
git worktree add .gh-pages gh-pages

# 2) Build in the gh-pages worktree with the repo base path
cd .gh-pages/AutoScrape24
npm install
npm run build -- --base=/autoscout-scraper/

# 3) Publish dist output to gh-pages branch root
cd ..
rm -rf assets data index.html
cp -R AutoScrape24/dist/assets ./assets
cp -R AutoScrape24/dist/data ./data
cp AutoScrape24/dist/index.html ./index.html

# 4) Commit and push
git add -A
git commit -m "Rebuild Pages bundle"
git push origin gh-pages
```

### If push fails with HTTP 400 or sideband disconnect

Retry push with safer HTTP settings:

```sh
git -c http.version=HTTP/1.1 \
	-c http.postBuffer=524288000 \
	-c http.lowSpeedLimit=0 \
	-c http.lowSpeedTime=999999 \
	push origin gh-pages
```

### Verify deployment

1. Check that `origin/gh-pages` moved to your latest commit.
2. Confirm the GitHub Action named "pages build and deployment" completes successfully.
3. Hard refresh the site after deployment to avoid stale cached assets.