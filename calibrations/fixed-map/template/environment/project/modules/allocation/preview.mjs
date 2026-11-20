export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.center,
    section: row.department,
    amount: row.credit,
  }));
}
