export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.service, row.samples]));
  return after.filter(row => previous.get(row.service) !== row.samples).map(row => row.service);
}
