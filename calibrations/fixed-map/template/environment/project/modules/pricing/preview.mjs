export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.tier,
    section: row.channel,
    amount: row.rate,
  }));
}
