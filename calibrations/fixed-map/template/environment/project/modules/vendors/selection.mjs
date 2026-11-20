export function selectcategory(rows, section) {
  return rows.filter(row => row.category === section);
}
