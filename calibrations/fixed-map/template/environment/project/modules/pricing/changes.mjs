export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.tier, row.rate]));
  return after.filter(row => previous.get(row.tier) !== row.rate).map(row => row.tier);
}
