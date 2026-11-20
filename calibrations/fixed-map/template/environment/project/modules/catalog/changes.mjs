export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.sku, row.stock]));
  return after.filter(row => previous.get(row.sku) !== row.stock).map(row => row.sku);
}
