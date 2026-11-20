export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.return,
    section: row.reason,
    amount: row.quantity,
  }));
}
