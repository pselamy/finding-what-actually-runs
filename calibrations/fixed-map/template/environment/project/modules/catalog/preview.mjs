export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.sku,
    section: row.collection,
    amount: row.stock,
  }));
}
