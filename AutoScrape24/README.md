# AutoScrape24

A React-based web application for visualizing car sale listings by mileage and price.

## Features

- Customizable scatter plot using D3.js (data loaded from `public/data` JSON files)
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
# 1) Build the app with the GitHub Pages base path
cd AutoScrape24
npm install
npm run build -- --base=/autoscout-scraper/
cd ..

# 2) Save your current branch and stash any uncommitted work
CURRENT_BRANCH=$(git branch --show-current)
STASHED=0
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
	git stash push --include-untracked -m "temp-pages-deploy"
	STASHED=1
fi

# 3) Switch to gh-pages and update branch
git checkout gh-pages
git pull --ff-only origin gh-pages

# 4) Publish dist output to gh-pages branch root
rm -rf assets data index.html
cp -R AutoScrape24/dist/assets assets
cp -R AutoScrape24/dist/data data
cp AutoScrape24/dist/index.html index.html

# 5) Commit and push
git add -A
git commit -m "Rebuild Pages bundle"
git push origin gh-pages

# 6) Return to your previous branch and restore work
git checkout "$CURRENT_BRANCH"
if [ "$STASHED" -eq 1 ]; then
	git stash pop
fi
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