import React, { useState, useRef, useEffect } from 'react';
import DirectoryTree from './components/DirectoryTree';
import Filters from './components/Filters';
import Graph from './components/Graph';
import ListingImages from './components/ListingImages';
import ListingInfo from './components/ListingInfo';
import './App.css';

const MIN_FILTER_BOUNDS = {
  maxPrice: 50000,
  maxMileage: 200000,
  maxDistance: 150,
};

function App() {
  const containerRef = useRef(null);
  const [leftWidth, setLeftWidth] = useState(null); // px
  const [rightWidth, setRightWidth] = useState(null);
  const [topHeightLeft, setTopHeightLeft] = useState(null);
  const [topHeightRight, setTopHeightRight] = useState(null);

  // listing-related state
  const [selection, setSelection] = useState({});
  const [filters, setFilters] = useState({});
  const [filterBounds, setFilterBounds] = useState({
    maxPrice: MIN_FILTER_BOUNDS.maxPrice,
    maxMileage: MIN_FILTER_BOUNDS.maxMileage,
    maxDistance: MIN_FILTER_BOUNDS.maxDistance,
  });
  const [enabledMakes, setEnabledMakes] = useState({});
  const [selectedListing, setSelectedListing] = useState(null);
  const [listingStatuses, setListingStatuses] = useState({}); // { guid: 'liked'|'disliked'|'seen'|null }

  const handleSelectionChange = (sel) => {
    setSelection(sel);
  };
  const handleFilterChange = (f) => {
    setFilters(f);
  };
  const handleFilterBoundsChange = (bounds) => {
    setFilterBounds((prev) => {
      const next = {
        maxPrice: Math.max(MIN_FILTER_BOUNDS.maxPrice, prev.maxPrice, Number(bounds?.maxPrice ?? 0)),
        maxMileage: Math.max(MIN_FILTER_BOUNDS.maxMileage, prev.maxMileage, Number(bounds?.maxMileage ?? 0)),
        maxDistance: Math.max(MIN_FILTER_BOUNDS.maxDistance, prev.maxDistance, Number(bounds?.maxDistance ?? 0)),
      };

      if (
        prev.maxPrice === next.maxPrice &&
        prev.maxMileage === next.maxMileage &&
        prev.maxDistance === next.maxDistance
      ) {
        return prev;
      }
      return next;
    });
  };
  const handleEnableChange = (e) => {
    setEnabledMakes(e);
  };
  const handleListingSelect = (listing) => {
    setSelectedListing(listing);
    // Mark as seen when selected (unless already liked/disliked)
    if (listing && !listingStatuses[listing.guid]) {
      setListingStatuses(prev => ({ ...prev, [listing.guid]: 'seen' }));
    }
  };
  const handleLike = (guid) => {
    setListingStatuses(prev => ({ ...prev, [guid]: 'liked' }));
  };
  const handleDislike = (guid) => {
    setListingStatuses(prev => ({ ...prev, [guid]: 'disliked' }));
  };

  // restore or set initial dimensions
  useEffect(() => {
    const stored = localStorage.getItem('autoscrape24-layout');
    if (stored) {
      try {
        const obj = JSON.parse(stored);
        if (obj.leftWidth) setLeftWidth(obj.leftWidth);
        if (obj.rightWidth) setRightWidth(obj.rightWidth);
        if (obj.topHeightLeft) setTopHeightLeft(obj.topHeightLeft);
        if (obj.topHeightRight) setTopHeightRight(obj.topHeightRight);
      } catch {}
    } else if (containerRef.current) {
      const w = containerRef.current.clientWidth;
      setLeftWidth(w / 3);
      setRightWidth(w / 3);
      setTopHeightLeft(200);
      setTopHeightRight(200);
    }
  }, []);

  // save layout when sizes change
  useEffect(() => {
    if (leftWidth !== null && rightWidth !== null) {
      const obj = { leftWidth, rightWidth, topHeightLeft, topHeightRight };
      localStorage.setItem('autoscrape24-layout', JSON.stringify(obj));
    }
  }, [leftWidth, rightWidth, topHeightLeft, topHeightRight]);

  const startDrag = (e, type) => {
    // ensure initial widths set to numeric
    if (leftWidth === null || rightWidth === null) {
      const w = containerRef.current?.clientWidth || 0;
      setLeftWidth(w / 3);
      setRightWidth(w / 3);
    }
    e.preventDefault();
    let lastX = e.clientX;
    let lastY = e.clientY;

    const onMouseMove = (ev) => {
      const dx = ev.clientX - lastX;
      const dy = ev.clientY - lastY;
      lastX = ev.clientX;
      lastY = ev.clientY;

      if (type === 'vertical-left') {
        setLeftWidth((w) => Math.max(100, w + dx));
      } else if (type === 'vertical-right') {
        setRightWidth((w) => Math.max(100, w - dx));
      } else if (type === 'horizontal-left') {
        setTopHeightLeft((h) => Math.max(50, h + dy));
      } else if (type === 'horizontal-right') {
        setTopHeightRight((h) => Math.max(50, h + dy));
      }
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="app-header">
        <h1>AutoScrape24</h1>
      </header>
      <div className="app-container" ref={containerRef}>
        <div
          className="column left-column"
          style={{ width: `${leftWidth}px` }}
        >
        <div className="pane top-pane" style={{ height: `${topHeightLeft}px` }}>
          <div className="pane-header">Makes & Models</div>
          <DirectoryTree onSelectionChange={handleSelectionChange} onEnableChange={handleEnableChange} />
        </div>
        <div
          className="divider horizontal"
          onMouseDown={(e) => startDrag(e, 'horizontal-left')}
        />
        <div className="pane bottom-pane">
          <div className="pane-header">Filters</div>
          <Filters value={filters} bounds={filterBounds} onChange={handleFilterChange} />
        </div>
      </div>

      <div
        className="divider vertical"
        onMouseDown={(e) => startDrag(e, 'vertical-left')}
      />

      <div className="column center-column">
        <div className="pane graph-pane">
          <div className="pane-header">Plot</div>
          <Graph selection={selection} filters={filters} enabledMakes={enabledMakes} listingStatuses={listingStatuses} onSelect={handleListingSelect} onFilterBoundsChange={handleFilterBoundsChange} />
        </div>
      </div>

      <div
        className="divider vertical"
        onMouseDown={(e) => startDrag(e, 'vertical-right')}
      />

      <div
        className="column right-column"
        style={{ width: `${rightWidth}px` }}
      >
        <div className="pane top-pane" style={{ height: `${topHeightRight}px` }}>
          <div className="pane-header">Images</div>
          <ListingImages listing={selectedListing} />
        </div>
        <div
          className="divider horizontal"
          onMouseDown={(e) => startDrag(e, 'horizontal-right')}
        />
        <div className="pane bottom-pane">
          <div className="pane-header">Details</div>
          <ListingInfo listing={selectedListing} onLike={handleLike} onDislike={handleDislike} />
        </div>
      </div>
      </div>
    </div>
  );
}

export default App;
