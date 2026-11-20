export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.invoice, row.charge]));
  return after.filter(row => previous.get(row.invoice) !== row.charge).map(row => row.invoice);
}
