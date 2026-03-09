import React, { useState, useEffect } from 'react';

function ListingImages({ listing }) {
  const [index, setIndex] = useState(0);
  const thumbUrls = Array.isArray(listing?.images)
    ? listing.images
    : (listing?.images ? listing.images.split(' ') : []);

  // Transform thumbnail URLs to full-size by replacing 250x188.webp with 1280x960.webp
  const urls = thumbUrls.map(url => url.replace(/250x188\.webp$/, '1280x960.webp'));

  useEffect(() => {
    setIndex(0);
  }, [listing]);

  if (!listing) return <div className="listing-images">Select a listing to see images</div>;
  if (urls.length === 0) return <div className="listing-images">No images available</div>;

  const prev = () => setIndex((i) => (i - 1 + urls.length) % urls.length);
  const next = () => setIndex((i) => (i + 1) % urls.length);

  return (
    <div className="listing-images" style={{ position: 'relative', textAlign: 'center', display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
      <img src={urls[index]} alt="" style={{ flex: 1, objectFit: 'contain', width: '100%', minHeight: 0 }} />
      {urls.length > 1 && (
        <>
          <button
            className="img-nav left"
            onClick={prev}
            style={{ position: 'absolute', left: '4px', top: '50%', transform: 'translateY(-50%)' }}
          >
            ◀
          </button>
          <button
            className="img-nav right"
            onClick={next}
            style={{ position: 'absolute', right: '4px', top: '50%', transform: 'translateY(-50%)' }}
          >
            ▶
          </button>
          <div className="dots" style={{ marginTop: '4px' }}>
            {urls.map((u, i) => (
              <span
                key={i}
                onClick={() => setIndex(i)}
                style={{
                  display: 'inline-block',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: i === index ? '#333' : '#ccc',
                  margin: '0 2px',
                  cursor: 'pointer',
                }}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default ListingImages;