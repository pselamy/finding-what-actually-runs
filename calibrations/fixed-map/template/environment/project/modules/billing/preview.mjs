export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.invoice,
    section: row.account,
    amount: row.charge,
  }));
}
