export function selectchannel(rows, section) {
  return rows.filter(row => row.channel === section);
}
