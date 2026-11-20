export function selectcarrier(rows, section) {
  return rows.filter(row => row.carrier === section);
}
