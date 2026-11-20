export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.receipt,
    section: row.segment,
    amount: row.cash,
  }));
}
