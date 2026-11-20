export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.forecast,
    section: row.scenario,
    amount: row.estimate,
  }));
}
