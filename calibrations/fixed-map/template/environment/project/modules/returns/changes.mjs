export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.return, row.quantity]));
  return after.filter(row => previous.get(row.return) !== row.quantity).map(row => row.return);
}
