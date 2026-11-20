export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.center, row.credit]));
  return after.filter(row => previous.get(row.center) !== row.credit).map(row => row.center);
}
