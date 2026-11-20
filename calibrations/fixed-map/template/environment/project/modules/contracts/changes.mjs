export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.contract, row.seats]));
  return after.filter(row => previous.get(row.contract) !== row.seats).map(row => row.contract);
}
