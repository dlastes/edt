import type {
  Course,
  CourseType,
  Department,
  Room,
  RoomReservation,
  RoomReservationType,
  ScheduledCourse,
  TimeSettings
} from '@/assets/js/types'

function getCookie (name: string) {
  if (!document.cookie) {
    return null
  }

  const xsrfCookies = document.cookie.split(';')
  .map(c => c.trim())
  .filter(c => c.startsWith(name + '='))

  if (xsrfCookies.length === 0) {
    return null
  }
  return decodeURIComponent(xsrfCookies[0].split('=')[1])
}

const csrfToken = getCookie('csrftoken')

async function fetchData (url: string, params: { [k: string]: any }) {
  let providedParams = params

  params = Object.assign({
    method: 'GET',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
  }, params)

  params.headers = {}
  params.headers = Object.assign({
    'X-CSRFToken': csrfToken,
    'Content-Type': 'application/json',
  }, params.headers)

  let args = ''

  if (providedParams) {
    args = Object.keys(providedParams).map((p) => p + '=' + providedParams[p]).join('&')
  }
  let finalUrl = `${import.meta.env.VITE_API_ENDPOINT}${url}/?${args}`
  console.log(`Fetching ${finalUrl}...`)

  let response = await fetch(finalUrl, params)
  let json = await response.json() || {}
  if (!response.ok) {
    let errorMessage = json.error || `${response.status}`
    throw new Error(errorMessage)
  }
  return json
}

const urls = {
  departments: 'fetch/alldepts',
  rooms: 'rooms/room',
  weekdays: 'fetch/weekdays',
  timesettings: 'base/timesettings',
  roomreservation: 'roomreservations/reservation',
  roomreservationtype: 'roomreservations/reservationtype',
  courses: 'courses/courses',
  scheduledcourses: 'fetch/scheduledcourses',
  coursetypes: 'courses/type',
}

/**
 * Proxy function to fetch from the api.
 * @param {string} url The url to access the data
 * @param {object} params1 Manually given parameters
 * @param {object} params2 Object-format given parameters
 * @returns {Promise<any>}
 */
const fetcher = (url: string, params1?: object, params2?: object) => fetchData(url, {...params1, ...params2})

function buildUrl (base: string, uri: string) {
  return `${base}/${uri}`
}

export interface FlopAPI {
  fetch: {
    all: {
      departments: () => Promise<Array<Department>>,
      rooms: (department: string) => Promise<Array<Room>>,
      timeSettings: () => Promise<Array<TimeSettings>>,
      coursetypes: (department: string) => Promise<Array<CourseType>>,
      roomReservationTypes: () => Promise<Array<RoomReservationType>>
    },
    target: {
      room: (id: number, additionalParams?: object) => Promise<Room>,
      weekdays: (week: number, year: number, additionalParams?: object) => Promise<any>,
      roomReservations: (week: number, year: number, params: { roomId?: number }, additionalParams?: object) => Promise<Array<RoomReservation>>,
      courses: (week: number, year: number, params: { department?: string }, additionalParams?: object) => Promise<Array<Course>>,
      scheduledCourses: (week: number, year: number, department: string, additionalParams?: object) => Promise<Array<ScheduledCourse>>,
    },
  },
}

const api: FlopAPI = {
  fetch: {
    all: {
      departments: () => fetcher(urls.departments),
      rooms: (department: string) => fetcher(urls.rooms, {dept: department}),
      timeSettings: () => fetcher(urls.timesettings),
      coursetypes: (department: string) => fetcher(urls.coursetypes, {dept: department}),
      roomReservationTypes: () => fetcher(urls.roomreservationtype),
    },
    target: {
      room: (id: number, additionalParams?: object) => fetcher(buildUrl(urls.rooms, id.toString()), additionalParams),
      weekdays: (week: number, year: number, additionalParams?: object) => fetcher(urls.weekdays, {
        week: week,
        year: year
      }, additionalParams),
      roomReservations: (week: number, year: number, params: { roomId?: number }, additionalParams?: object) => fetcher(urls.roomreservation, {
        ...{
          week: week,
          year: year
        }, ...{...(params.roomId && {room: params.roomId}), ...(!params.roomId && {})}
      }, additionalParams),
      courses: (week: number, year: number, params: { department?: string }, additionalParams?: object) => fetcher(urls.courses, {
        ...{
          week: week,
          year: year,
        }, ...{...(params.department && {dept: params.department}), ...(!params.department && {})}
      }, additionalParams),
      scheduledCourses: (week: number, year: number, department: string, additionalParams?: object) => fetcher(urls.scheduledcourses, {
        week: week,
        year: year,
        dept: department
      }, additionalParams),
    }
  },
}
export { api }
