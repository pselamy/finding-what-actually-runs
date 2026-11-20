export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.forecast, row.estimate]));
  return after.filter(row => previous.get(row.forecast) !== row.estimate).map(row => row.forecast);
}
