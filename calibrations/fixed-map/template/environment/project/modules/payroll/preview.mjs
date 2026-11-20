export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.payment,
    section: row.paygroup,
    amount: row.hours,
  }));
}
