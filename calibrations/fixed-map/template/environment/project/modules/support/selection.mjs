export function selectqueue(rows, section) {
  return rows.filter(row => row.queue === section);
}
