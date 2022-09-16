export function convertDecimalTimeToHuman(time: number): string {
    const hours = Math.trunc(time)
    const minutes = Math.round((time - hours) * 60)
    return `${hours}h${
        minutes > 0 ? (minutes < 10 ? `0${minutes}` : minutes) : '00'
    }`
}
