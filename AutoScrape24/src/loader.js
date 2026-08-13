// Discover JSON files from `public/data` as URLs and fetch them at runtime.
// Using `{ as: 'url' }` keeps large JSON payloads out of the JS bundle.
const dataFileUrls = Object.values(
  import.meta.glob('../public/data/*.json', {
    eager: true,
    as: 'url',
  })
).sort();

let cachedListings = null;

async function fetchAllListings() {
  if (cachedListings) return cachedListings;

  const results = await Promise.all(
    dataFileUrls.map(async (url) => {
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
        return await res.json();
      } catch (err) {
        console.error(`Error loading ${url}:`, err);
        return [];
      }
    })
  );

  cachedListings = results.flat().filter((item) => item != null);
  return cachedListings;
}

function parseNumber(value) {
  if (value == null) return 0;
  const str = String(value).replace(/[^\d.-]/g, '');
  const num = Number(str);
  return Number.isFinite(num) ? num : 0;
}

function normalizeListing(listing) {
  const price = parseNumber(listing.price);
  const mileage = parseNumber(listing.mileage);
  const distance = parseNumber(listing.distance);
  const regAge = parseNumber(listing['reg-age']);

  return {
    ...listing,
    price,
    mileage,
    distance,
    'reg-age': regAge,
    transmission: listing.transmission || listing['transmission-type'] || '',
    fuel: listing.fuel || listing['fuel-type'] || '',
  };
}

export async function getAllListings() {
  const arr = await fetchAllListings();
  return arr.map(normalizeListing);
}

export async function getMakesAndModels() {
  const listings = await getAllListings();
  const tree = {};
  listings.forEach((l) => {
    const { make, model } = l;
    if (!make || !model) return;
    if (!tree[make]) tree[make] = new Set();
    tree[make].add(model);
  });
  // convert sets to arrays
  const result = {};
  Object.entries(tree).forEach(([make, set]) => {
    result[make] = Array.from(set).sort();
  });
  return result;
}
