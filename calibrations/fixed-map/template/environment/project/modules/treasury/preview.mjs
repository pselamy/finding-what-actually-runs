export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.position,
    section: row.currency,
    amount: row.principal,
  }));
}
