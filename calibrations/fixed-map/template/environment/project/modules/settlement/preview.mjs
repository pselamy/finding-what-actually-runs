export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.batch,
    section: row.processor,
    amount: row.net,
  }));
}
