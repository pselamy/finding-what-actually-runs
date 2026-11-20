export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.service,
    section: row.region,
    amount: row.samples,
  }));
}
