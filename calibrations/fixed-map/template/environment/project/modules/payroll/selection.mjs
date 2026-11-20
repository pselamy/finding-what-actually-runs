export function selectpaygroup(rows, section) {
  return rows.filter(row => row.paygroup === section);
}
