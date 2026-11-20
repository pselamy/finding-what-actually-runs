export function changedKeys(before, after) {
  const previous = new Map(before.map(row => [row.parcel, row.weight]));
  return after.filter(row => previous.get(row.parcel) !== row.weight).map(row => row.parcel);
}
