export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.position, row.principal]));
  return after.filter(row => previous.get(row.position) !== row.principal).map(row => row.position);
}
