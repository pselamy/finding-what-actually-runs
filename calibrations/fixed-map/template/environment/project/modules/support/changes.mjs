export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.case, row.tickets]));
  return after.filter(row => previous.get(row.case) !== row.tickets).map(row => row.case);
}
