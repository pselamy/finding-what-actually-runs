export function selectwarehouse(rows, section) {
  return rows.filter(row => row.warehouse === section);
}
