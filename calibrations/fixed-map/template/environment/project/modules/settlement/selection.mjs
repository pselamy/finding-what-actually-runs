export function selectprocessor(rows, section) {
  return rows.filter(row => row.processor === section);
}
