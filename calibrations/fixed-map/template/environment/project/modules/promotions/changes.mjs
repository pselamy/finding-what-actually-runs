export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.coupon, row.uses]));
  return after.filter(row => previous.get(row.coupon) !== row.uses).map(row => row.coupon);
}
