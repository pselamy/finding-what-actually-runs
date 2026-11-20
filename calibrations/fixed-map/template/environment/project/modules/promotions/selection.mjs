export function selectcampaign(rows, section) {
  return rows.filter(row => row.campaign === section);
}
