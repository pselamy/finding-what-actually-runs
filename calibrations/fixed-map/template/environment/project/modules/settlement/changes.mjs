export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.batch, row.net]));
  return after.filter(row => previous.get(row.batch) !== row.net).map(row => row.batch);
}
