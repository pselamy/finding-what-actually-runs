export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.shipment, row.units]));
  return after.filter(row => previous.get(row.shipment) !== row.units).map(row => row.shipment);
}
