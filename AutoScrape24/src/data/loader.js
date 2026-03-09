const modules = import.meta.glob('./*.json', { eager: true });

function flattenModules(mods) {
  let arr = [];
  for (const key in mods) {
    const mod = mods[key];
    const data = mod?.default ?? mod;
    if (Array.isArray(data)) {
      arr = arr.concat(data);
    }
  }
  return arr;
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
  const arr = flattenModules(modules);
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
