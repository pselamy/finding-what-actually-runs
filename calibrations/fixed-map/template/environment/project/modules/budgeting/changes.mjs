export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.envelope, row.planned]));
  return after.filter(row => previous.get(row.envelope) !== row.planned).map(row => row.envelope);
}
