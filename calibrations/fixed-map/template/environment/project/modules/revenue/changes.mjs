export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.receipt, row.cash]));
  return after.filter(row => previous.get(row.receipt) !== row.cash).map(row => row.receipt);
}
