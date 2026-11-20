export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.vendor, row.quotations]));
  return after.filter(row => previous.get(row.vendor) !== row.quotations).map(row => row.vendor);
}
