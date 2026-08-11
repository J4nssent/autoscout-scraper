import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { getAllListings } from '../data/loader';

// scales will be updated later
const colorScale = d3.scaleSequential(d3.interpolateYlOrRd);
// reverse range so larger distance produces smaller circle; reduce max radius
const sizeScale = d3.scaleLinear().range([12, 4]);

function Graph({ selection, filters, enabledMakes, listingStatuses, onSelect, onFilterBoundsChange }) {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const [width, setWidth] = useState(0);
  const [height, setHeight] = useState(0);
  const [axisResetVersion, setAxisResetVersion] = useState(0);
  const domainRef = useRef(null); // persist zoom domains across renders
  const svgElementsRef = useRef(null); // persist SVG structure
  const currentDataRef = useRef([]); // track current data for click detection

  useEffect(() => {
    const cleanupFns = [];
    const render = async () => {
      const getTransmissionType = (listing) => {
        const directValue = (
          listing.transmission ||
          listing.gearbox ||
          ''
        ).toString().toLowerCase();

        const versionValue = (listing.version || '').toString().toLowerCase();
        const combined = `${directValue} ${versionValue}`;

        const automaticPatterns = [
          'automatic', 'automaat', 'aut.', 'aut ', 'geartronic', 'multitronic',
          'tiptronic', 'dsg', 'powershift', 'cvt', 'e-cvt', 's tronic', 'stronic'
        ];
        const manualPatterns = ['manual', 'manueel', 'manuel', 'stick shift'];

        if (automaticPatterns.some((pattern) => combined.includes(pattern))) return 'Automatic';
        if (manualPatterns.some((pattern) => combined.includes(pattern))) return 'Manual';
        return 'Other';
      };

      const getFuelType = (listing) => {
        const value = (listing.fuel || '').toString().toLowerCase();
        if (!value) return 'other';
        if (value.includes('diesel') && value.includes('hybrid')) return 'hybrid';
        if (value.includes('benzine') && value.includes('hybrid')) return 'hybrid';
        if (value.includes('elektrisch') && value.includes('benzine')) return 'plug-in-hybrid';
        if (value.includes('elektrisch') && value.includes('diesel')) return 'plug-in-hybrid';
        if (value.includes('hybrid')) return 'hybrid';
        if (value.includes('elektrisch') || value.includes('electric')) return 'electric';
        if (value.includes('diesel')) return 'diesel';
        if (value.includes('benzine') || value.includes('gasoline') || value.includes('petrol')) return 'gasoline';
        return 'other';
      };

      const getSellerType = (listing) => {
        const value = (listing['seller-type'] || '').toString().toLowerCase();
        if (value.includes('private')) return 'Private';
        if (value.includes('dealer')) return 'Dealer';
        return 'Other';
      };

      const svg = d3.select(svgRef.current);
      const margin = { top: 0, right: 0, bottom: 40, left: 50 };
      const plotPadding = { top: 10, right: 10 };
      const w = width - margin.left - margin.right;
      const h = height - margin.top - margin.bottom;

      if (w <= 0 || h <= 0) return;

      // filter listings based on props
      let data = [];
      const all = await getAllListings();
      data = all;
      if (selection) {
        // filter by make/model selection
        const keys = Object.entries(selection)
          .filter(([k, v]) => v)
          .map(([k]) => k);
        if (keys.length) {
          data = data.filter((l) => keys.includes(`${l.make}-${l.model}`));
        } else {
          data = [];
        }
      }
      // additionally respect enabledMakes prop
      if (enabledMakes) {
        data = data.filter((l) => enabledMakes[l.make] !== false);
      }
      // apply basic filters (new structure)
      if (filters) {
        if (filters.ageRange) {
          const [minA, maxA] = filters.ageRange;
          if (minA != null) data = data.filter(l => +l['reg-age'] >= minA * 365);
          if (maxA != null) data = data.filter(l => +l['reg-age'] <= maxA * 365);
        }
        // fuel type mapping
        if (filters.fuelTypes) {
          const selected = Object.entries(filters.fuelTypes).filter(([_, v]) => v).map(([k]) => k);
          if (selected.length) {
            data = data.filter(l => selected.includes(getFuelType(l)));
          }
        }
        if (filters.sellerTypes) {
          const sel = Object.entries(filters.sellerTypes).filter(([_, v]) => v).map(([k]) => k);
          if (sel.length) {
            data = data.filter(l => sel.includes(getSellerType(l)));
          }
        }
        if (filters.transmissionTypes) {
          const selectedTransmissionTypes = Object.entries(filters.transmissionTypes)
            .filter(([_, enabled]) => enabled)
            .map(([type]) => type);

          if (selectedTransmissionTypes.length) {
            data = data.filter((listing) => selectedTransmissionTypes.includes(getTransmissionType(listing)));
          }
        }
        // filter by body type
        if (filters.bodyTypes) {
          const selectedBodyTypes = Object.entries(filters.bodyTypes)
            .filter(([_, enabled]) => enabled)
            .map(([type]) => parseInt(type));

          if (selectedBodyTypes.length) {
            data = data.filter((listing) => selectedBodyTypes.includes(listing['body-type']));
          }
        }
        // filter by search term
        if (filters.searchKeywords && filters.searchKeywords.length > 0) {
          const enabledKeywords = filters.searchKeywords
            .filter(k => k.enabled)
            .map(k => k.term.toLowerCase());
          
          if (enabledKeywords.length > 0) {
            data = data.filter((listing) => {
              const searchableText = [
                listing.make,
                listing.model,
                listing.version,
                listing.transmission,
                listing.fuel
              ]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();
              return enabledKeywords.some(keyword => searchableText.includes(keyword));
            });
          }
        }
        // filter by like/dislike status
        if (filters.showLiked === true) {
          data = data.filter(l => listingStatuses?.[l.guid] === 'liked');
        }
        if (filters.hideDisliked === true) {
          data = data.filter(l => listingStatuses?.[l.guid] !== 'disliked');
        }
      }

      const maxPriceBound = d3.max(data, d => +d.price) || 0;
      const maxMileageBound = d3.max(data, d => +d.mileage) || 0;
      const maxDistanceBound = d3.max(data, d => +d.distance) || 0;

      onFilterBoundsChange?.({
        maxPrice: maxPriceBound,
        maxMileage: maxMileageBound,
        maxDistance: maxDistanceBound,
      });

      if (filters) {
        if (filters.maxPrice != null) data = data.filter(l => +l.price <= +filters.maxPrice);
        if (filters.maxMileage != null) data = data.filter(l => +l.mileage <= +filters.maxMileage);
        if (filters.maxDistance != null) data = data.filter(l => +l.distance <= +filters.maxDistance);
      }

      // compute global scales domain using all listings (ignore filters)
      // but use fixed mileage cap for axis
      const MAX_MILEAGE_LIMIT = 200000;
      const maxPriceAll = d3.max(all, d => +d.price) || 0;
      const maxDistance = d3.max(data, d => +d.distance) || 0; // still use filtered for size/color

      // color scale based on actual min/max age in filtered data
      const colorMinAge = d3.min(data, d => +d['reg-age']) || 0;
      const colorMaxAge = d3.max(data, d => +d['reg-age']) || 0;

      // initialize domains only once on first render
      // this preserves zoom/pan state across re-renders and resizes
      if (!domainRef.current) {
        domainRef.current = {
          x: [0, MAX_MILEAGE_LIMIT],
          y: [0, maxPriceAll]
        };
      }

      colorScale.domain([colorMinAge, colorMaxAge]);
      sizeScale.domain([0, maxDistance]);

      // clear previous content
      svg.selectAll('*').remove();

      // create main group with margin offset
      const g = svg
        .append('g')
        .attr('class', 'graph-root')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const plotTop = plotPadding.top;
      const plotRight = w - plotPadding.right;

      const topFrame = g
        .append('line')
        .attr('class', 'graph-frame graph-frame-top')
        .attr('x1', 0)
        .attr('x2', plotRight)
        .attr('y1', plotTop)
        .attr('y2', plotTop)
        .style('pointer-events', 'none');

      const topFrameMask = g
        .append('rect')
        .attr('class', 'graph-frame-mask graph-frame-mask-top')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', w)
        .attr('height', plotTop)
        .style('pointer-events', 'none');

      const rightFrame = g
        .append('line')
        .attr('class', 'graph-frame graph-frame-right')
        .attr('x1', plotRight)
        .attr('x2', plotRight)
        .attr('y1', plotTop)
        .attr('y2', h)
        .style('pointer-events', 'none');

      const rightFrameMask = g
        .append('rect')
        .attr('class', 'graph-frame-mask graph-frame-mask-right')
        .attr('x', plotRight)
        .attr('y', 0)
        .attr('width', w - plotRight)
        .attr('height', h)
        .style('pointer-events', 'none');

      const clampDomainMin = (domain, min = 0) => {
        const [d0, d1] = domain;
        if (d0 >= min) return [d0, d1];
        const shift = min - d0;
        return [d0 + shift, d1 + shift];
      };

      const getZoomFactor = (deltaY) => {
        const ZOOM_SENSITIVITY = 0.005;
        return Math.exp(deltaY * ZOOM_SENSITIVITY);
      };

      const createScales = () => {
        const x = d3.scaleLinear().domain(domainRef.current.x).range([0, plotRight]);
        const y = d3.scaleLinear().domain(domainRef.current.y).range([h, plotTop]);
        return { x, y };
      };

      const formatThousands = (value) => {
        const inThousands = value / 1000;
        if (Math.abs(inThousands) < 10) {
          return d3.format(',.1f')(inThousands);
        }
        return d3.format(',.0f')(inThousands);
      };

      function drawPlot() {
        // use raw domains; do not .nice() so dragging stays smooth
        const { x, y } = createScales();
        xAxis.call(d3.axisBottom(x).tickSizeOuter(0).tickFormat(formatThousands));
        yAxis.call(d3.axisLeft(y).tickSizeOuter(0).tickFormat(formatThousands));
        xAxis.selectAll('*').style('pointer-events', 'none');
        yAxis.selectAll('*').style('pointer-events', 'none');
        circles
          .attr('cx', d => x(d.mileage))
          .attr('cy', d => y(+d.price));
        
        // Position badge at upper right: center intersects main circle circumference
        const BADGE_RADIUS = 4;
        badges
          .attr('cx', d => {
            const cx = x(d.mileage);
            const r = filters?.dotSizing !== false ? sizeScale(+d.distance) : 5;
            return cx + (r * 0.75 + BADGE_RADIUS) * Math.cos(-Math.PI / 4);
          })
          .attr('cy', d => {
            const cy = y(+d.price);
            const r = filters?.dotSizing !== false ? sizeScale(+d.distance) : 5;
            return cy + (r * 0.75 + BADGE_RADIUS) * Math.sin(-Math.PI / 4);
          });

        topFrameMask.raise();
        rightFrameMask.raise();
        topFrame.raise();
        rightFrame.raise();
        yAxisMask.raise();
        xAxisMask.raise();
        xAxis.raise();
        yAxis.raise();
        xAxisLabel.raise();
        yAxisLabel.raise();
      }

      const circles = g
        .selectAll('circle.main-dot')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'main-dot')
        .attr('cx', d => 0)
        .attr('cy', d => 0)
        .attr('r', d => filters?.dotSizing !== false ? sizeScale(+d.distance) : 5)
        .attr('fill', d => filters?.ageColoring !== false ? colorScale(+d['reg-age']) : '#60a5fa')
        .attr('stroke', 'none')
        .style('pointer-events', 'none');

      const badges = g
        .selectAll('circle.status-badge')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'status-badge')
        .attr('r', 4)
        .attr('fill', d => {
          const status = listingStatuses?.[d.guid];
          switch (status) {
            case 'liked': return '#10b981'; // green
            case 'disliked': return '#ef4444'; // red
            case 'seen': return 'none';
            default: return '#9ca3af'; // grey for unseen
          }
        })
        .attr('stroke', d => {
          const status = listingStatuses?.[d.guid];
          return status === 'seen' ? 'none' : 'white';
        })
        .attr('stroke-width', 1)
        .style('opacity', d => {
          if (filters?.statusIcons === false) return 0;
          const status = listingStatuses?.[d.guid];
          return status === 'seen' ? 0 : 1;
        })
        .style('pointer-events', 'none');

      const AXIS_MASK_OVERLAP = 2;
      const yAxisMask = g
        .append('rect')
        .attr('class', 'graph-axis-mask graph-axis-mask-y')
        .attr('x', -margin.left)
        .attr('y', 0)
        .attr('width', margin.left + AXIS_MASK_OVERLAP)
        .attr('height', h)
        .style('pointer-events', 'none');
      const xAxisMask = g
        .append('rect')
        .attr('class', 'graph-axis-mask graph-axis-mask-x')
        .attr('x', 0)
        .attr('y', h - AXIS_MASK_OVERLAP)
        .attr('width', w)
        .attr('height', margin.bottom + AXIS_MASK_OVERLAP)
        .style('pointer-events', 'none');

      const xAxis = g
        .append('g')
        .attr('class', 'graph-axis graph-axis-x')
        .attr('transform', `translate(0,${h})`)
        .style('pointer-events', 'none');
      const yAxis = g
        .append('g')
        .attr('class', 'graph-axis graph-axis-y')
        .style('pointer-events', 'none');

      const xAxisLabel = g
        .append('text')
        .attr('class', 'graph-axis-label graph-axis-label-x')
        .attr('x', w / 2)
        .attr('y', h + margin.bottom - 8)
        .attr('text-anchor', 'middle')
        .style('pointer-events', 'none')
        .text('milage (k)');

      const yAxisLabel = g
        .append('text')
        .attr('class', 'graph-axis-label graph-axis-label-y')
        .attr('transform', `translate(${-margin.left + 14},${h / 2}) rotate(-90)`)
        .attr('text-anchor', 'middle')
        .style('pointer-events', 'none')
        .text('price (k)');

      const xAxisInteraction = g
        .append('rect')
        .attr('class', 'graph-axis-interaction graph-axis-interaction-x')
        .attr('x', 0)
        .attr('y', h)
        .attr('width', plotRight)
        .attr('height', margin.bottom)
        .attr('fill', 'transparent')
        .attr('pointer-events', 'all');

      const yAxisInteraction = g
        .append('rect')
        .attr('class', 'graph-axis-interaction graph-axis-interaction-y')
        .attr('x', -margin.left)
        .attr('y', plotTop)
        .attr('width', margin.left)
        .attr('height', h - plotTop)
        .attr('fill', 'transparent')
        .attr('pointer-events', 'all');

      // create overlay rect for interactions (added AFTER circles so it's on top)
      const overlay = g
        .append('rect')
        .attr('width', w)
        .attr('height', h)
        .attr('fill', 'none')
        .attr('pointer-events', 'all');

      // initial draw
      drawPlot();

      xAxisInteraction.raise();
      yAxisInteraction.raise();
      xAxisLabel.raise();
      yAxisLabel.raise();

      // zoom with wheel
      overlay.on('wheel', (event) => {
        event.preventDefault();
        const [mx, my] = d3.pointer(event);
        const { x: xScale, y: yScale } = createScales();
        const mxData = xScale.invert(mx);
        const myData = yScale.invert(my);
        const wheel = getZoomFactor(event.deltaY);
        // update domains
        domainRef.current.x = [
          mxData + (domainRef.current.x[0] - mxData) * wheel,
          mxData + (domainRef.current.x[1] - mxData) * wheel
        ];
        domainRef.current.y = [
          myData + (domainRef.current.y[0] - myData) * wheel,
          myData + (domainRef.current.y[1] - myData) * wheel
        ];
        domainRef.current.x = clampDomainMin(domainRef.current.x, 0);
        domainRef.current.y = clampDomainMin(domainRef.current.y, 0);
        drawPlot();
      });

      xAxisInteraction.on('wheel', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const [mx] = d3.pointer(event, g.node());
        const { x: xScale } = createScales();
        const mxData = xScale.invert(mx);
        const wheel = getZoomFactor(event.deltaY);
        domainRef.current.x = [
          mxData + (domainRef.current.x[0] - mxData) * wheel,
          mxData + (domainRef.current.x[1] - mxData) * wheel
        ];
        domainRef.current.x = clampDomainMin(domainRef.current.x, 0);
        drawPlot();
      });

      yAxisInteraction.on('wheel', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const [, my] = d3.pointer(event, g.node());
        const { y: yScale } = createScales();
        const myData = yScale.invert(my);
        const wheel = getZoomFactor(event.deltaY);
        domainRef.current.y = [
          myData + (domainRef.current.y[0] - myData) * wheel,
          myData + (domainRef.current.y[1] - myData) * wheel
        ];
        domainRef.current.y = clampDomainMin(domainRef.current.y, 0);
        drawPlot();
      });

      // pans
      let dragging = false;
      let start = null;
      let hasDragged = false;
      let axisDragging = null;
      overlay.on('mousedown', (event) => {
        event.preventDefault();
        dragging = true;
        hasDragged = false;
        start = d3.pointer(event);
      });

      xAxisInteraction.on('mousedown', (event) => {
        event.preventDefault();
        event.stopPropagation();
        axisDragging = 'x';
        start = d3.pointer(event, g.node());
      });

      yAxisInteraction.on('mousedown', (event) => {
        event.preventDefault();
        event.stopPropagation();
        axisDragging = 'y';
        start = d3.pointer(event, g.node());
      });

      const onMouseMoveWindow = (event) => {
        if (axisDragging === 'x') {
          const [cx] = d3.pointer(event, g.node());
          const dx = cx - start[0];
          const { x: xScale } = createScales();
          const dxData = xScale.invert(-dx) - xScale.invert(0);
          domainRef.current.x = [domainRef.current.x[0] + dxData, domainRef.current.x[1] + dxData];
          domainRef.current.x = clampDomainMin(domainRef.current.x, 0);
          drawPlot();
          start = [cx, start[1]];
          return;
        }

        if (axisDragging === 'y') {
          const [, cy] = d3.pointer(event, g.node());
          const dy = cy - start[1];
          const { y: yScale } = createScales();
          const dyData = yScale.invert(0) - yScale.invert(dy);
          domainRef.current.y = [domainRef.current.y[0] + dyData, domainRef.current.y[1] + dyData];
          domainRef.current.y = clampDomainMin(domainRef.current.y, 0);
          drawPlot();
          start = [start[0], cy];
          return;
        }

        if (!dragging) return;
        hasDragged = true;
        const [cx, cy] = d3.pointer(event, overlay.node());
        const dx = cx - start[0];
        const dy = cy - start[1];
        const { x: xScale, y: yScale } = createScales();
        const dxData = xScale.invert(-dx) - xScale.invert(0);
        // invert vertical movement because SVG y-axis is reversed
        const dyData = yScale.invert(0) - yScale.invert(dy);
        domainRef.current.x = [domainRef.current.x[0] + dxData, domainRef.current.x[1] + dxData];
        domainRef.current.y = [domainRef.current.y[0] + dyData, domainRef.current.y[1] + dyData];
        domainRef.current.x = clampDomainMin(domainRef.current.x, 0);
        domainRef.current.y = clampDomainMin(domainRef.current.y, 0);
        drawPlot();
        start = [cx, cy];
      };
      const onMouseUpWindow = (event) => {
        if (axisDragging) {
          axisDragging = null;
          return;
        }

        if (dragging && !hasDragged) {
          // This was a click, not a drag - find which circle was clicked
          const [mx, my] = d3.pointer(event, overlay.node());
          const { x: xScale, y: yScale } = createScales();
          
          // Check each circle to see if click was within its radius
          for (let i = 0; i < data.length; i++) {
            const d = data[i];
            const cx = xScale(d.mileage);
            const cy = yScale(+d.price);
            const r = filters?.dotSizing !== false ? sizeScale(+d.distance) : 5;
            const dist = Math.sqrt((mx - cx) ** 2 + (my - cy) ** 2);
            if (dist <= r) {
              if (onSelect) onSelect(d);
              break;
            }
          }
        }
        dragging = false;
      };
      window.addEventListener('mousemove', onMouseMoveWindow);
      window.addEventListener('mouseup', onMouseUpWindow);

      // cleanup listeners on re-render
      cleanupFns.push(() => {
        window.removeEventListener('mousemove', onMouseMoveWindow);
        window.removeEventListener('mouseup', onMouseUpWindow);
      });
    };

    render();
    return () => {
      cleanupFns.forEach(fn => fn());
    };
  }, [width, height, selection, filters, enabledMakes, listingStatuses, axisResetVersion]);

  useEffect(() => {
    // use ResizeObserver to watch container size (reacts to divider drags too)
    const target = containerRef.current;
    if (!target) return;
    const observer = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width: w, height: h } = entry.contentRect;
        setWidth(w);
        setHeight(h);
      }
    });
    observer.observe(target);
    // initial
    const rect = target.getBoundingClientRect();
    setWidth(rect.width);
    setHeight(rect.height);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={containerRef} className="graph-canvas" style={{ position: 'relative' }}>
      <button
        type="button"
        onClick={() => {
          domainRef.current = null;
          setAxisResetVersion((prev) => prev + 1);
        }}
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          zIndex: 10,
          fontSize: '11px',
          padding: '4px 8px'
        }}
      >
        Reset axis
      </button>
      <svg ref={svgRef} className="graph-svg" style={{ width: '100%', height: '100%' }} />
    </div>
  );
}

export default Graph;