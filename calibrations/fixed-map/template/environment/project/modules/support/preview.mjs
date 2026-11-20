export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.case,
    section: row.queue,
    amount: row.tickets,
  }));
}
