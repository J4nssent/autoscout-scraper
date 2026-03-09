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