export function selectregion(rows, section) {
  return rows.filter(row => row.region === section);
}
