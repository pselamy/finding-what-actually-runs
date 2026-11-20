export function selectcollection(rows, section) {
  return rows.filter(row => row.collection === section);
}
