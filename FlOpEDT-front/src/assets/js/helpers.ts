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

export function parseReason(
    reason: unknown,
    onAlert?: (level: string, message: string) => void
) {
    // Reason can be either a response body or a thrown error
    if (reason instanceof Object && !(reason instanceof Error)) {
        // Reason is a response body, display each message separately
        const reasonObj = reason as { [key: string]: string }
        Object.keys(reasonObj).forEach((key) => {
            onAlert?.('danger', `${key}: ${reasonObj[key]}`)
        })
    } else {
        onAlert?.('danger', `${reason}. Please contact an administrator.`)
    }
}
