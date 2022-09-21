export function convertDecimalTimeToHuman(time: number): string {
    const hours = Math.trunc(time)
    const minutes = Math.round((time - hours) * 60)
    return `${hours}:${toStringAtLeastTwoDigits(minutes)}`
}

/**
 * Takes a number and convert it to a string with a '0' prefix if there is only one digit.
 * @param {number} element The element to convert
 * @returns {string} The two-digits string
 */
export function toStringAtLeastTwoDigits(element: number) {
    return `${element < 10 ? `0${element}` : element}`
}
