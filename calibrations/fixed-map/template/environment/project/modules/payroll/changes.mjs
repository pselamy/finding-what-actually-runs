export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.payment, row.hours]));
  return after.filter(row => previous.get(row.payment) !== row.hours).map(row => row.payment);
}
