export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.parcel,
    section: row.carrier,
    amount: row.weight,
  }));
}
