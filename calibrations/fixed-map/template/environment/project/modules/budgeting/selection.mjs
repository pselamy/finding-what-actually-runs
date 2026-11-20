export function selectgroup(rows, section) {
  return rows.filter(row => row.group === section);
}
