export function preview(rows, limit) {
  return rows.slice(0, limit).map(row => ({
    key: row.coupon,
    section: row.campaign,
    amount: row.uses,
  }));
}
