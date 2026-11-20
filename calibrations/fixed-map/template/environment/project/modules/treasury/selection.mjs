export function selectcurrency(rows, section) {
  return rows.filter(row => row.currency === section);
}
