import React, { useState, useEffect } from 'react';
import { getMakesAndModels } from '../loader';

function DirectoryTree({ onSelectionChange, onEnableChange }) {
  const [data, setData] = useState({});
  const [expanded, setExpanded] = useState({});
  const [checked, setChecked] = useState({});
  const [enabledMakes, setEnabledMakes] = useState({});

  useEffect(() => {
    (async () => {
      const tree = await getMakesAndModels();
      console.log('DirectoryTree loaded makes/models:', tree);
      setData(tree);
      // initialize toggles off and models checked on
      const enables = {};
      const checks = {};
      Object.entries(tree).forEach(([make, models]) => {
        enables[make] = false; // toggle off
        models.forEach((m) => {
          checks[`${make}-${m}`] = true; // model selected
        });
      });
      setEnabledMakes(enables);
      setChecked(checks);
      if (onEnableChange) onEnableChange(enables);
      if (onSelectionChange) onSelectionChange(checks);
    })();
  }, []);

  const toggleFolder = (make) => {
    setExpanded((prev) => ({ ...prev, [make]: !prev[make] }));
  };

  const toggleMakeEnabled = (make) => {
    setEnabledMakes((prev) => {
      const updated = { ...prev, [make]: !prev[make] };
      if (onEnableChange) onEnableChange(updated);
      return updated;
    });
  };

  const setMakeChecked = (make, value, models) => {
    setChecked((prev) => {
      const updated = { ...prev };
      models.forEach((m) => {
        updated[`${make}-${m}`] = value;
      });
      if (onSelectionChange) onSelectionChange(updated);
      return updated;
    });
  };

  const toggleModel = (make, model) => {
    const key = `${make}-${model}`;
    setChecked((prev) => {
      const updated = { ...prev, [key]: !prev[key] };
      if (onSelectionChange) {
        onSelectionChange(updated);
      }
      return updated;
    });
  };

  const handleBrandClick = (e, make, models) => {
    if (e.ctrlKey || e.metaKey) {
      // Ctrl+Click: toggle all models for this brand
      e.stopPropagation();
      const total = models.length;
      let checkedCount = 0;
      models.forEach((m) => {
        if (checked[`${make}-${m}`]) checkedCount += 1;
      });
      const allChecked = checkedCount === total && total > 0;
      setMakeChecked(make, !allChecked, models);
    } else {
      // Normal click: toggle folder expand/collapse
      toggleFolder(make);
    }
  };

  return (
    <div className="directory-tree">
      {Object.keys(data).length === 0 && <div>No makes/models available</div>}
      {Object.entries(data).map(([make, models]) => {
        const total = models.length;
        let checkedCount = 0;
        models.forEach((m) => {
          if (checked[`${make}-${m}`]) checkedCount += 1;
        });
        const allChecked = checkedCount === total && total > 0;
        const someChecked = checkedCount > 0 && checkedCount < total;
        const isEnabled = enabledMakes[make];
        return (
          <div key={make}>
            <div
              className="folder"
              style={{ display: 'flex', alignItems: 'center' }}
            >
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={isEnabled}
                  onChange={() => toggleMakeEnabled(make)}
                />
                <div className="switch-slider"></div>
              </label>
              <span 
                className={`caret ${expanded[make] ? 'expanded' : ''}`}
                onClick={() => toggleFolder(make)}
              >
                ›
              </span>
              <span style={{ fontWeight: 'bold', cursor: 'pointer' }} onClick={(e) => handleBrandClick(e, make, models)}>
                {make}
              </span>
            </div>
            {expanded[make] && (
              <div className="models" style={{ paddingLeft: '1em', opacity: isEnabled ? 1 : 0.5 }}>
                {models.map((m) => (
                  <label key={m} style={{ display: 'block' }}>
                    <input
                      type="checkbox"
                      checked={checked[`${make}-${m}`] || false}
                      onChange={() => toggleModel(make, m)}
                      disabled={!isEnabled}
                    />{' '}
                    {m}
                  </label>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default DirectoryTree;
