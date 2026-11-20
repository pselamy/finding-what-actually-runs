export function selectdepartment(rows, section) {
  return rows.filter(row => row.department === section);
}
