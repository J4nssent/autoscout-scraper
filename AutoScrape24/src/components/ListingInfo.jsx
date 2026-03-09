import React from 'react';

function ListingInfo({ listing, onLike, onDislike }) {
  if (!listing) return <div className="listing-info">Select a listing to see details</div>;

  const fuelLabel = listing.fuel || 'Unknown';

  // Calculate age in years from reg-age (days)
  const ageYears = listing['reg-age'] ? Math.floor(listing['reg-age'] / 365) : null;
  const registrationYear = ageYears !== null ? new Date().getFullYear() - ageYears : 'N/A';

  // Build the link
  const listingUrl = listing.url
    ? `https://www.autoscout24.be${listing.url}`
    : `https://www.autoscout24.be/nl/aanbod/${listing.guid}`;

  return (
    <div className="listing-info" style={{ padding: '16px', fontSize: '14px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header: Make & Model with Like/Dislike buttons */}
      <div style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
        <div>
          <div style={{ fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>
            {listing.make} {listing.model}
          </div>
          <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '4px', fontWeight: '500' }}>
            {listing.version}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
          <button
            onClick={() => onLike(listing.guid)}
            className="btn-success"
            style={{ fontSize: '12px', padding: '6px 10px' }}
          >
            👍
          </button>
          <button
            onClick={() => onDislike(listing.guid)}
            className="btn-danger"
            style={{ fontSize: '12px', padding: '6px 10px' }}
          >
            👎
          </button>
        </div>
      </div>

      {/* Two-column stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '4px' }}>Price</div>
            <div style={{ color: '#3b82f6', fontSize: '16px', fontWeight: '700' }}>€{listing.price}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '4px' }}>Fuel</div>
            <div style={{ color: '#1f2937', fontSize: '14px' }}>{fuelLabel}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '4px' }}>Mileage</div>
            <div style={{ color: '#1f2937', fontSize: '14px' }}>{listing.mileage} km</div>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '4px' }}>Year</div>
            <div style={{ color: '#1f2937', fontSize: '14px' }}>
              {ageYears !== null ? `${registrationYear} (${ageYears} years)` : 'N/A'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '4px' }}>Distance</div>
            <div style={{ color: '#1f2937', fontSize: '14px' }}>{listing.distance} km</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.3px', marginBottom: '4px' }}>Seller</div>
            <div style={{ color: '#1f2937', fontSize: '14px' }}>{listing['seller-type']}</div>
          </div>
        </div>
      </div>

      {/* Link */}
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '12px' }}>
        <a
          href={listingUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary"
          style={{ display: 'inline-flex', justifyContent: 'center', width: '100%' }}
        >
          View on AutoScout24 →
        </a>
      </div>
    </div>
  );
}

export default ListingInfo;