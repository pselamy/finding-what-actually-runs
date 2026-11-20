export function selectscenario(rows, section) {
  return rows.filter(row => row.scenario === section);
}
