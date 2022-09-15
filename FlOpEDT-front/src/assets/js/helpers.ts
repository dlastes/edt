export function convertDecimalTimeToHuman (time: number): string {
  let hours = Math.trunc(time)
  let minutes = Math.round((time - hours) * 60)
  return `${hours}h${minutes > 0 ? (minutes < 10 ? `0${minutes}` : minutes) : '00'}`
}
