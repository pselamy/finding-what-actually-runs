export function selectsegment(rows, section) {
  return rows.filter(row => row.segment === section);
}
