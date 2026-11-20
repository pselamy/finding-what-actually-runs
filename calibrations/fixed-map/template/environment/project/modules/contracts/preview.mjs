export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.contract,
    section: row.customer,
    amount: row.seats,
  }));
}
