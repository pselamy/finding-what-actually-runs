export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.vendor,
    section: row.category,
    amount: row.quotations,
  }));
}
