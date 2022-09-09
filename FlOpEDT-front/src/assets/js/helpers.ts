export function convertDecimalTimeToHuman (time: number): string {
  let hours = Math.trunc(time)
  let minutes = Math.trunc((time - hours) * 60)
  return `${hours}h${minutes > 0 ? minutes : '00'}`
}
