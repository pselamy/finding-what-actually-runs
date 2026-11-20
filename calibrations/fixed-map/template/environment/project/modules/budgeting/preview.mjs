export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.envelope,
    section: row.group,
    amount: row.planned,
  }));
}
