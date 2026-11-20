export function selectcustomer(rows, section) {
  return rows.filter(row => row.customer === section);
}
