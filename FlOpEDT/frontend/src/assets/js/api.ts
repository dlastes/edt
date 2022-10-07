let API_ENDPOINT = ''

const dbDataElement = document.getElementById('json_data')
if (dbDataElement && dbDataElement.textContent) {
    const data = JSON.parse(dbDataElement.textContent)
    if ('api' in data) {
        API_ENDPOINT = data.api
    }
}

import type {
    BooleanRoomAttributeValue,
    Course,
    CourseType,
    Department,
    NumericRoomAttributeValue,
    ReservationPeriodicity,
    ReservationPeriodicityByMonth,
    ReservationPeriodicityByMonthXChoice,
    ReservationPeriodicityByWeek,
    ReservationPeriodicityEachMonthSameDate,
    ReservationPeriodicityType,
    Room,
    RoomAttribute,
    RoomReservation,
    RoomReservationType,
    ScheduledCourse,
    TimeSettings,
    User,
    WeekDay,
} from '@/assets/js/types'

function getCookie(name: string) {
    if (!document.cookie) {
        return null
    }

    const xsrfCookies = document.cookie
        .split(';')
        .map((c) => c.trim())
        .filter((c) => c.startsWith(name + '='))

    if (xsrfCookies.length === 0) {
        return null
    }
    return decodeURIComponent(xsrfCookies[0].split('=')[1])
}

const csrfToken = getCookie('csrftoken')

async function fetchData(url: string, params: { [k: string]: never }) {
    const providedParams = params

    params = Object.assign(
        {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
        },
        params
    )

    params.headers = Object.assign(
        {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        params.headers
    )

    let args = ''

    if (providedParams) {
        args = Object.keys(providedParams)
            .map((p) => p + '=' + providedParams[p])
            .join('&')
    }
    const finalUrl = `${API_ENDPOINT}${url}/?${args}`
    console.log(`Fetching ${finalUrl}...`)

    const response = await fetch(finalUrl, params)
    const json = (await response.json()) || {}
    if (!response.ok) {
        const errorMessage = json.error || `${response.status}`
        throw new Error(errorMessage)
    }
    return json
}

async function sendData<T>(method: string, url: string, optional: { data?: unknown; id?: number }): Promise<T | never> {
    if (!['PUT', 'POST', 'DELETE'].includes(method)) {
        return Promise.reject('Method must be either PUT, POST, or DELETE')
    }

    // Setup headers
    const requestHeaders: HeadersInit = new Headers()
    requestHeaders.set('Content-Type', 'application/json')

    if (csrfToken) {
        requestHeaders.set('X-CSRFToken', csrfToken)
    }

    // Setup request
    const requestInit: RequestInit = {
        method: method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: requestHeaders,
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    }
    if (optional.data) {
        requestInit.body = JSON.stringify(optional.data)
    }

    // Create url
    let endUrl = '/'
    if (optional.id) {
        endUrl = `/${optional.id}/`
    }
    const finalUrl = `${API_ENDPOINT}${url}${endUrl}`
    console.log(`Updating ${finalUrl}...`)

    // Wait for the response
    return await fetch(finalUrl, requestInit)
        .then(async (response) => {
            const data = await response.json()
            if (!response.ok) {
                const error = data || `Error ${response.status}: ${response.statusText}`
                return Promise.reject(error)
            }
            return data
        })
        .catch((reason) => {
            return Promise.reject(reason)
        })
}

async function putData<T>(url: string, id: number, data: unknown): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        id: id,
        data: data,
    }
    return await sendData('PUT', url, optional)
}

async function postData<T>(url: string, data: unknown): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        data: data,
    }
    return await sendData('POST', url, optional)
}

function deleteData(url: string, id: number) {
    const optional: { [key: string]: unknown } = {
        id: id,
    }
    return sendData('DELETE', url, optional)
}

const urls = {
    departments: 'fetch/alldepts',
    rooms: 'rooms/room',
    weekdays: 'fetch/weekdays',
    timesettings: 'base/timesettings',
    roomreservation: 'roomreservations/reservation',
    roomreservationtype: 'roomreservations/reservationtype',
    reservationperiodicity: 'roomreservations/reservationperiodicity',
    reservationperiodicitytype: 'roomreservations/reservationperiodicitytype',
    reservationperiodicitybyweek: 'roomreservations/reservationperiodicitybyweek',
    reservationperiodicityeachmonthsamedate: 'roomreservations/reservationperiodicityeachmonthsamedate',
    reservationperiodicitybymonth: 'roomreservations/reservationperiodicitybymonth',
    reservationperiodicitybymonthxchoice: 'roomreservations/reservationperiodicitybymonthxchoice',
    courses: 'courses/courses',
    scheduledcourses: 'fetch/scheduledcourses',
    coursetypes: 'courses/type',
    users: 'user/users',
    booleanroomattributes: 'rooms/booleanattributes',
    numericroomattributes: 'rooms/numericattributes',
    booleanroomattributevalues: 'rooms/booleanattributevalues',
    numericroomattributevalues: 'rooms/numericattributevalues',
}

/**
 * Proxy function to fetch from the api.
 * @param {string} url The url to access the data
 * @param {object} params1 Manually given parameters
 * @param {object} params2 Object-format given parameters
 * @returns {Promise<any>}
 */
const fetcher = (url: string, params1?: object, params2?: object) => fetchData(url, { ...params1, ...params2 })

function buildUrl(base: string, uri: string) {
    return `${base}/${uri}`
}

export interface FlopAPI {
    fetch: {
        all: {
            departments(): Promise<Array<Department>>
            rooms(department: string): Promise<Array<Room>>
            timeSettings(): Promise<Array<TimeSettings>>
            courseTypes(department: string): Promise<Array<CourseType>>
            roomReservationTypes(): Promise<Array<RoomReservationType>>
            reservationPeriodicities(): Promise<Array<ReservationPeriodicity>>
            reservationPeriodicityTypes(): Promise<Array<ReservationPeriodicityType>>
            reservationPeriodicityByMonthXChoices(): Promise<Array<ReservationPeriodicityByMonthXChoice>>
            users(): Promise<Array<User>>
            booleanRoomAttributes(): Promise<Array<RoomAttribute>>
            numericRoomAttributes(): Promise<Array<RoomAttribute>>
            booleanRoomAttributeValues(): Promise<Array<BooleanRoomAttributeValue>>
            numericRoomAttributeValues(): Promise<Array<NumericRoomAttributeValue>>
        }
        target: {
            room(id: number, additionalParams?: object): Promise<Room>
            weekdays(week: number, year: number, additionalParams?: object): Promise<Array<WeekDay>>
            roomReservations(
                week: number,
                year: number,
                params: { roomId?: number },
                additionalParams?: object
            ): Promise<Array<RoomReservation>>
            reservationPeriodicity(reservationId: number): Promise<ReservationPeriodicity>
            courses(
                week: number,
                year: number,
                params: { department?: string },
                additionalParams?: object
            ): Promise<Array<Course>>
            scheduledCourses(
                week: number,
                year: number,
                department: string,
                additionalParams?: object
            ): Promise<Array<ScheduledCourse>>
        }
    }
    put: {
        roomReservation(value: RoomReservation): Promise<RoomReservation>
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth): Promise<ReservationPeriodicityByMonth>
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek): Promise<ReservationPeriodicityByWeek>
        reservationPeriodicityEachMonthSameDate(
            value: ReservationPeriodicityEachMonthSameDate
        ): Promise<ReservationPeriodicityEachMonthSameDate>
    }
    post: {
        roomReservation(value: RoomReservation): Promise<RoomReservation>
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth): Promise<ReservationPeriodicityByMonth>
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek): Promise<ReservationPeriodicityByWeek>
        reservationPeriodicityEachMonthSameDate(
            value: ReservationPeriodicityEachMonthSameDate
        ): Promise<ReservationPeriodicityEachMonthSameDate>
    }
    delete: {
        roomReservation(id: number): Promise<unknown>
    }
}

const api: FlopAPI = {
    fetch: {
        all: {
            departments() {
                return fetcher(urls.departments)
            },
            rooms(department: string) {
                return fetcher(urls.rooms, { dept: department })
            },
            timeSettings() {
                return fetcher(urls.timesettings)
            },
            courseTypes(department: string) {
                return fetcher(urls.coursetypes, { dept: department })
            },
            roomReservationTypes() {
                return fetcher(urls.roomreservationtype)
            },
            reservationPeriodicities() {
                return fetcher(urls.reservationperiodicity)
            },
            reservationPeriodicityTypes() {
                return fetcher(urls.reservationperiodicitytype)
            },
            reservationPeriodicityByMonthXChoices() {
                return fetcher(urls.reservationperiodicitybymonthxchoice)
            },
            users() {
                return fetcher(urls.users)
            },
            booleanRoomAttributes() {
                return fetcher(urls.booleanroomattributes)
            },
            numericRoomAttributes() {
                return fetcher(urls.numericroomattributes)
            },
            booleanRoomAttributeValues() {
                return fetcher(urls.booleanroomattributevalues)
            },
            numericRoomAttributeValues() {
                return fetcher(urls.numericroomattributevalues)
            },
        },
        target: {
            room(id: number, additionalParams?: object) {
                return fetcher(buildUrl(urls.rooms, id.toString()), additionalParams)
            },
            weekdays(week: number, year: number, additionalParams?: object) {
                return fetcher(
                    urls.weekdays,
                    {
                        week: week,
                        year: year,
                    },
                    additionalParams
                )
            },
            roomReservations(week: number, year: number, params: { roomId?: number }, additionalParams?: object) {
                return fetcher(
                    urls.roomreservation,
                    {
                        ...{
                            week: week,
                            year: year,
                        },
                        ...{
                            ...(params.roomId && { room: params.roomId }),
                            ...(!params.roomId && {}),
                        },
                    },
                    additionalParams
                )
            },
            reservationPeriodicity(periodicityId: number): Promise<ReservationPeriodicity> {
                return fetcher(urls.reservationperiodicity, { id: periodicityId })
            },
            courses(week: number, year: number, params: { department?: string }, additionalParams?: object) {
                return fetcher(
                    urls.courses,
                    {
                        ...{
                            week: week,
                            year: year,
                        },
                        ...{
                            ...(params.department && {
                                dept: params.department,
                            }),
                            ...(!params.department && {}),
                        },
                    },
                    additionalParams
                )
            },
            scheduledCourses(week: number, year: number, department: string, additionalParams?: object) {
                return fetcher(
                    urls.scheduledcourses,
                    {
                        week: week,
                        year: year,
                        dept: department,
                    },
                    additionalParams
                )
            },
        },
    },
    put: {
        roomReservation(value: RoomReservation) {
            return putData<RoomReservation>(urls.roomreservation, value.id, value)
        },
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth) {
            return putData<ReservationPeriodicityByMonth>(urls.reservationperiodicitybymonth, value.id, value)
        },
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek) {
            return putData<ReservationPeriodicityByWeek>(urls.reservationperiodicitybyweek, value.id, value)
        },
        reservationPeriodicityEachMonthSameDate(value: ReservationPeriodicityEachMonthSameDate) {
            return putData<ReservationPeriodicityEachMonthSameDate>(
                urls.reservationperiodicityeachmonthsamedate,
                value.id,
                value
            )
        },
    },
    post: {
        roomReservation(value: RoomReservation) {
            return postData(urls.roomreservation, value)
        },
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth) {
            return postData<ReservationPeriodicityByMonth>(urls.reservationperiodicitybymonth, value)
        },
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek) {
            return postData<ReservationPeriodicityByWeek>(urls.reservationperiodicitybyweek, value)
        },
        reservationPeriodicityEachMonthSameDate(value: ReservationPeriodicityEachMonthSameDate) {
            return postData<ReservationPeriodicityEachMonthSameDate>(
                urls.reservationperiodicityeachmonthsamedate,
                value
            )
        },
    },
    delete: {
        roomReservation(id: number): Promise<unknown> {
            return deleteData(urls.roomreservation, id)
        },
    },
}
export { api }
