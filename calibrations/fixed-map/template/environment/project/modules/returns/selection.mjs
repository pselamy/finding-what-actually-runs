export function selectreason(rows, section) {
  return rows.filter(row => row.reason === section);
}
