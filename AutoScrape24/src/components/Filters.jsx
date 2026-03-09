import React, { useState, useEffect } from 'react';

const BODY_TYPE_LABELS = {
  1: 'Compact',
  2: 'Convertible',
  3: 'Coupe',
  4: 'SUV/Pickup',
  5: 'Station wagon',
  6: 'Sedan',
  7: 'Other',
  12: 'Van/Minibus',
  13: 'Transporter',
};

function Filters({ value = {}, bounds = {}, onChange }) {
  const [inputSearch, setInputSearch] = useState('');
  const [searchKeywords, setSearchKeywords] = useState(value.searchKeywords || []);
  const [maxPrice, setMaxPrice] = useState(value.maxPrice ?? 25000);
  const [maxMileage, setMaxMileage] = useState(value.maxMileage ?? 100000);
  const [ageRange, setAgeRange] = useState(value.ageRange || [0, 30]);
  const [fuelTypes, setFuelTypes] = useState(value.fuelTypes || {
    gasoline: false,
    diesel: false,
    hybrid: false,
    'plug-in-hybrid': false,
    electric: false,
    other: false,
  });
  const [sellerTypes, setSellerTypes] = useState(value.sellerTypes || {
    Dealer: false,
    Private: false,
  });
  const [transmissionTypes, setTransmissionTypes] = useState(value.transmissionTypes || {
    Automatic: false,
    Manual: false,
    Other: false,
  });
  const [bodyTypes, setBodyTypes] = useState(value.bodyTypes || {
    1: false,
    2: false,
    3: false,
    4: false,
    5: false,
    6: false,
    7: false,
    12: false,
    13: false,
  });
  const [maxDistance, setMaxDistance] = useState(value.maxDistance ?? 150);
  const [dotSizing, setDotSizing] = useState(value.dotSizing !== false); // enabled by default
  const [ageColoring, setAgeColoring] = useState(value.ageColoring !== false); // enabled by default
  const [statusIcons, setStatusIcons] = useState(value.statusIcons !== false); // enabled by default
  const [showLiked, setShowLiked] = useState(value.showLiked === true); // off by default
  const [hideDisliked, setHideDisliked] = useState(value.hideDisliked !== false); // hide disliked by default
  const [ageMode, setAgeMode] = useState('age'); // 'age' or 'year'
  const [expandedSections, setExpandedSections] = useState({
    fuelTypes: false,
    sellerTypes: false,
    transmissionTypes: false,
    bodyTypes: false,
    status: false,
  });

  const maxPriceLimit = Math.max(0, Number(bounds.maxPrice ?? 100000));
  const maxMileageLimit = Math.max(0, Number(bounds.maxMileage ?? 300000));
  const maxDistanceLimit = Math.max(0, Number(bounds.maxDistance ?? 500));

  useEffect(() => {
    if (maxPrice > maxPriceLimit) {
      setMaxPrice(maxPriceLimit);
    }
  }, [maxPrice, maxPriceLimit]);

  useEffect(() => {
    if (maxMileage > maxMileageLimit) {
      setMaxMileage(maxMileageLimit);
    }
  }, [maxMileage, maxMileageLimit]);

  useEffect(() => {
    if (maxDistance > maxDistanceLimit) {
      setMaxDistance(maxDistanceLimit);
    }
  }, [maxDistance, maxDistanceLimit]);

  useEffect(() => {
    if (onChange) {
      onChange({ searchKeywords, maxPrice, maxMileage, ageRange, fuelTypes, sellerTypes, transmissionTypes, bodyTypes, maxDistance, dotSizing, ageColoring, statusIcons, showLiked, hideDisliked });
    }
  }, [searchKeywords, maxPrice, maxMileage, ageRange, fuelTypes, sellerTypes, transmissionTypes, bodyTypes, maxDistance, dotSizing, ageColoring, statusIcons, showLiked, hideDisliked]);

  const handleFuel = (type) => {
    setFuelTypes((prev) => ({ ...prev, [type]: !prev[type] }));
  };
  const handleSeller = (type) => {
    setSellerTypes((prev) => ({ ...prev, [type]: !prev[type] }));
  };
  const handleTransmission = (type) => {
    setTransmissionTypes((prev) => ({ ...prev, [type]: !prev[type] }));
  };
  const handleBodyType = (type) => {
    setBodyTypes((prev) => ({ ...prev, [type]: !prev[type] }));
  };
  const handleAddSearchKeyword = () => {
    const trimmedSearch = inputSearch.trim();
    if (trimmedSearch && !searchKeywords.some(k => k.term.toLowerCase() === trimmedSearch.toLowerCase())) {
      setSearchKeywords((prev) => [...prev, { id: Date.now(), term: trimmedSearch, enabled: true }]);
      setInputSearch('');
    }
  };
  const handleToggleKeyword = (id) => {
    setSearchKeywords((prev) => prev.map(k => k.id === id ? { ...k, enabled: !k.enabled } : k));
  };
  const handleDeleteKeyword = (id) => {
    setSearchKeywords((prev) => prev.filter(k => k.id !== id));
  };
  const toggleSection = (section) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };
  const toggleAgeMode = () => {
    setAgeMode((prev) => (prev === 'age' ? 'year' : 'age'));
  };
  
  // Get display values (convert age to year if in year mode)
  const getDisplayValues = () => {
    const currentYear = new Date().getFullYear();
    if (ageMode === 'year') {
      return [currentYear - ageRange[1], currentYear - ageRange[0]];
    }
    return ageRange;
  };
  
  // Set age values from input (convert year to age if in year mode)
  const setAgeValue = (index, value) => {
    const currentYear = new Date().getFullYear();
    if (ageMode === 'year') {
      // Convert year input to age (inverse relationship)
      if (index === 0) {
        // Setting min year = setting max age
        setAgeRange((prev) => [prev[0], currentYear - value]);
      } else {
        // Setting max year = setting min age
        setAgeRange((prev) => [currentYear - value, prev[1]]);
      }
    } else {
      setAgeRange((prev) => index === 0 ? [value, prev[1]] : [prev[0], value]);
    }
  };
  
  const [displayMin, displayMax] = getDisplayValues();

  return (
    <div className="filters" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div>
        <label style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>Search</label>
        <div style={{ display: 'flex', gap: '4px', marginBottom: '6px' }}>
          <input
            type="text"
            placeholder="e.g. roadster"
            value={inputSearch}
            onChange={(e) => setInputSearch(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddSearchKeyword()}
            style={{ flex: 1, fontSize: '12px', padding: '6px', boxSizing: 'border-box' }}
          />
          <button
            onClick={handleAddSearchKeyword}
            style={{
              fontSize: '14px',
              padding: '4px 8px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              minWidth: '30px',
              lineHeight: '1'
            }}
          >
            +
          </button>
        </div>
        {searchKeywords.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {[...searchKeywords].sort((a, b) => a.term.localeCompare(b.term)).map((keyword) => (
              <div key={keyword.id} style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#f3f4f6', padding: '4px 6px', borderRadius: '3px' }}>
                <input
                  type="checkbox"
                  checked={keyword.enabled}
                  onChange={() => handleToggleKeyword(keyword.id)}
                  style={{ width: '14px', height: '14px', cursor: 'pointer' }}
                />
                <span style={{ fontSize: '12px', flex: 1, color: keyword.enabled ? '#000' : '#9ca3af' }}>
                  {keyword.term}
                </span>
                <button
                  onClick={() => handleDeleteKeyword(keyword.id)}
                  style={{
                    fontSize: '8px',
                    width: '14px',
                    height: '14px',
                    padding: '0',
                    backgroundColor: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    fontWeight: 'bold',
                    lineHeight: '1'
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
          <label style={{ fontSize: '12px' }}>Price</label>
          <span style={{ fontSize: '11px', color: '#6b7280', fontWeight: '500' }}>€{maxPrice}</span>
        </div>
        <input
          type="range"
          min="0"
          max={maxPriceLimit}
          step="500"
          value={maxPrice}
          onChange={(e) => setMaxPrice(+e.target.value)}
        />
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
          <label style={{ fontSize: '12px' }}>Mileage</label>
          <span style={{ fontSize: '11px', color: '#6b7280', fontWeight: '500' }}>{maxMileage} km</span>
        </div>
        <input
          type="range"
          min="0"
          max={maxMileageLimit}
          step="1000"
          value={maxMileage}
          onChange={(e) => setMaxMileage(+e.target.value)}
        />
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <label style={{ fontSize: '12px' }}>Age</label>
          <button
            onClick={() => setAgeColoring((prev) => !prev)}
            className={ageColoring ? 'btn-success' : 'btn-secondary'}
            style={{ fontSize: '10px', padding: '3px 6px', height: '22px', width: '32px', lineHeight: '1', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            {ageColoring ? 'ON' : 'OFF'}
          </button>
        </div>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <div 
            onClick={toggleAgeMode}
            style={{ 
              position: 'relative',
              width: '120px',
              height: '30px',
              backgroundColor: '#e5e7eb',
              borderRadius: '4px',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              overflow: 'hidden',
              flexShrink: 0,
              marginRight: '6px'
            }}
          >
            <div 
              style={{
                position: 'absolute',
                top: '2px',
                left: ageMode === 'age' ? '2px' : 'calc(50% - 2px)',
                width: 'calc(50% + 2px)',
                height: 'calc(100% - 4px)',
                backgroundColor: '#3b82f6',
                borderRadius: '3px',
                transition: 'left 0.2s ease'
              }}
            />
            <div style={{ 
              position: 'relative', 
              display: 'flex', 
              height: '100%',
              zIndex: 1 
            }}>
              <div style={{ 
                flex: 1, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                fontSize: '11px',
                fontWeight: '500',
                color: ageMode === 'age' ? 'white' : '#6b7280'
              }}>
                age
              </div>
              <div style={{ 
                flex: 1, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                fontSize: '11px',
                fontWeight: '500',
                color: ageMode === 'year' ? 'white' : '#6b7280'
              }}>
                year
              </div>
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <input
              type="number"
              min={ageMode === 'age' ? 0 : 1900}
              max={ageMode === 'age' ? 100 : new Date().getFullYear()}
              value={displayMin}
              onChange={(e) => setAgeValue(0, +e.target.value)}
              placeholder={ageMode === 'age' ? 'Min Age' : 'Min Year'}
              style={{ width: '100%', fontSize: '12px', padding: '4px' }}
            />
          </div>
          <span style={{ color: '#d1d5db', fontSize: '12px' }}>–</span>
          <div style={{ flex: 1 }}>
            <input
              type="number"
              min={ageMode === 'age' ? 0 : 1900}
              max={ageMode === 'age' ? 100 : new Date().getFullYear()}
              value={displayMax}
              onChange={(e) => setAgeValue(1, +e.target.value)}
              placeholder={ageMode === 'age' ? 'Max Age' : 'Max Year'}
              style={{ width: '100%', fontSize: '12px', padding: '4px' }}
            />
          </div>
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer' }} onClick={() => toggleSection('fuelTypes')}>
          <label style={{ fontSize: '12px', cursor: 'pointer' }}>Fuel Type</label>
          <span className={`caret ${expandedSections.fuelTypes ? 'expanded' : ''}`} style={{ marginLeft: '4px' }}>›</span>
        </div>
        {expandedSections.fuelTypes && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {Object.keys(fuelTypes).map((ft) => (
              <label key={ft} style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
                <input
                  type="checkbox"
                  checked={fuelTypes[ft]}
                  onChange={() => handleFuel(ft)}
                  style={{ width: '14px', height: '14px' }}
                />
                <span style={{ marginLeft: '6px', fontSize: '12px' }}>{ft}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer' }} onClick={() => toggleSection('sellerTypes')}>
          <label style={{ fontSize: '12px', cursor: 'pointer' }}>Seller Type</label>
          <span className={`caret ${expandedSections.sellerTypes ? 'expanded' : ''}`} style={{ marginLeft: '4px' }}>›</span>
        </div>
        {expandedSections.sellerTypes && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {Object.keys(sellerTypes).map((st) => (
              <label key={st} style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
                <input
                  type="checkbox"
                  checked={sellerTypes[st]}
                  onChange={() => handleSeller(st)}
                  style={{ width: '14px', height: '14px' }}
                />
                <span style={{ marginLeft: '6px', fontSize: '12px' }}>{st}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer' }} onClick={() => toggleSection('transmissionTypes')}>
          <label style={{ fontSize: '12px', cursor: 'pointer' }}>Transmission Type</label>
          <span className={`caret ${expandedSections.transmissionTypes ? 'expanded' : ''}`} style={{ marginLeft: '4px' }}>›</span>
        </div>
        {expandedSections.transmissionTypes && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {Object.keys(transmissionTypes).map((tt) => (
              <label key={tt} style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
                <input
                  type="checkbox"
                  checked={transmissionTypes[tt]}
                  onChange={() => handleTransmission(tt)}
                  style={{ width: '14px', height: '14px' }}
                />
                <span style={{ marginLeft: '6px', fontSize: '12px' }}>{tt}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px', cursor: 'pointer' }} onClick={() => toggleSection('bodyTypes')}>
          <label style={{ fontSize: '12px', cursor: 'pointer' }}>Body Type</label>
          <span className={`caret ${expandedSections.bodyTypes ? 'expanded' : ''}`} style={{ marginLeft: '4px' }}>›</span>
        </div>
        {expandedSections.bodyTypes && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {Object.keys(bodyTypes).map((bt) => (
              <label key={bt} style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
                <input
                  type="checkbox"
                  checked={bodyTypes[bt]}
                  onChange={() => handleBodyType(bt)}
                  style={{ width: '14px', height: '14px' }}
                />
                <span style={{ marginLeft: '6px', fontSize: '12px' }}>{BODY_TYPE_LABELS[bt]}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
          <label style={{ fontSize: '12px' }}>Distance</label>
          <button
            onClick={() => setDotSizing((prev) => !prev)}
            className={dotSizing ? 'btn-success' : 'btn-secondary'}
            style={{ fontSize: '10px', padding: '3px 6px', height: '22px', width: '32px', lineHeight: '1', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            {dotSizing ? 'ON' : 'OFF'}
          </button>
        </div>
        <input
          type="range"
          min="0"
          max={maxDistanceLimit}
          step="10"
          value={maxDistance}
          onChange={(e) => setMaxDistance(+e.target.value)}
        />
        <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '3px' }}>{maxDistance} km</div>
      </div>

      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => toggleSection('status')}>
            <label style={{ fontSize: '12px', cursor: 'pointer' }}>Status</label>
            <span className={`caret ${expandedSections.status ? 'expanded' : ''}`} style={{ marginLeft: '4px' }}>›</span>
          </div>
          <button
            onClick={() => setStatusIcons((prev) => !prev)}
            className={statusIcons ? 'btn-success' : 'btn-secondary'}
            style={{ fontSize: '10px', padding: '3px 6px', height: '22px', width: '32px', lineHeight: '1', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            {statusIcons ? 'ON' : 'OFF'}
          </button>
        </div>
        {expandedSections.status && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
              <input
                type="checkbox"
                checked={showLiked}
                onChange={() => setShowLiked((prev) => !prev)}
                style={{ width: '14px', height: '14px' }}
              />
              <span style={{ marginLeft: '6px', fontSize: '12px' }}>Show liked only</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', margin: 0 }}>
              <input
                type="checkbox"
                checked={hideDisliked}
                onChange={() => setHideDisliked((prev) => !prev)}
                style={{ width: '14px', height: '14px' }}
              />
              <span style={{ marginLeft: '6px', fontSize: '12px' }}>Hide disliked</span>
            </label>
          </div>
        )}
      </div>
    </div>
  );
}

export default Filters;
