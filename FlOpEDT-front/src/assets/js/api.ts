import type {
  Course,
  CourseType,
  Department,
  Room,
  RoomReservation,
  RoomReservationType,
  ScheduledCourse,
  TimeSettings,
  User,
  WeekDay,
} from '@/assets/js/types'

function getCookie (name: string) {
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

async function fetchData (url: string, params: { [k: string]: never }) {
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
  const finalUrl = `${import.meta.env.VITE_API_ENDPOINT}${url}/?${args}`
  console.log(`Fetching ${finalUrl}...`)

  const response = await fetch(finalUrl, params)
  const json = (await response.json()) || {}
  if (!response.ok) {
    const errorMessage = json.error || `${response.status}`
    throw new Error(errorMessage)
  }
  return json
}

async function sendData (
    method: string,
    url: string,
    data: unknown,
    optional: { id?: number; authToken?: string }
) {
  if (!(method === 'PUT' || method === 'POST')) {
    return Promise.reject('Method must be either PUT or POST')
  }

  // Setup headers
  const requestHeaders: HeadersInit = new Headers()
  requestHeaders.set('Content-Type', 'application/json')
  if (csrfToken) {
    requestHeaders.set('X-CSRFToken', csrfToken)
  }
  if (optional.authToken) {
    requestHeaders.set('Authorization', `Token ${optional.authToken}`)
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
    body: JSON.stringify(data),
  }

  // Create url
  let endUrl = '/'
  if (optional.id) {
    endUrl = `/${optional.id}/`
  }
  const finalUrl = `${import.meta.env.VITE_API_ENDPOINT}${url}${endUrl}`
  console.log(`Updating ${finalUrl}...`)

  // Wait for the response
  return await fetch(finalUrl, requestInit).then(response => {
    if (!response.ok) {
      throw Error(response.statusText)
    }
    return response
  }).then(response => {
    return response.json()
  }).catch(reason => {
    return Promise.reject(reason)
  })
}

async function putData (
    url: string,
    id: number,
    data: unknown,
    authToken?: string
) {
  const optional: { [key: string]: unknown } = {
    id: id,
  }
  if (authToken) {
    optional.authToken = authToken
  }
  return await sendData('PUT', url, data, optional)
}

async function postData (url: string, data: unknown, authToken?: string) {
  const optional: { [key: string]: unknown } = {}
  if (authToken) {
    optional.authToken = authToken
  }
  return await sendData('POST', url, data, optional)
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
  users: 'user/users',
  authToken: 'api-token-auth',
}

/**
 * Proxy function to fetch from the api.
 * @param {string} url The url to access the data
 * @param {object} params1 Manually given parameters
 * @param {object} params2 Object-format given parameters
 * @returns {Promise<any>}
 */
const fetcher = (url: string, params1?: object, params2?: object) =>
    fetchData(url, {...params1, ...params2})

function buildUrl (base: string, uri: string) {
  return `${base}/${uri}`
}

export interface FlopAPI {
  fetch: {
    all: {
      departments: () => Promise<Array<Department>>
      rooms: (department: string) => Promise<Array<Room>>
      timeSettings: () => Promise<Array<TimeSettings>>
      courseTypes: (department: string) => Promise<Array<CourseType>>
      roomReservationTypes: () => Promise<Array<RoomReservationType>>
      users: () => Promise<Array<User>>
    }
    target: {
      room: (id: number, additionalParams?: object) => Promise<Room>
      weekdays: (
          week: number,
          year: number,
          additionalParams?: object
      ) => Promise<Array<WeekDay>>
      roomReservations: (
          week: number,
          year: number,
          params: { roomId?: number },
          additionalParams?: object
      ) => Promise<Array<RoomReservation>>
      courses: (
          week: number,
          year: number,
          params: { department?: string },
          additionalParams?: object
      ) => Promise<Array<Course>>
      scheduledCourses: (
          week: number,
          year: number,
          department: string,
          additionalParams?: object
      ) => Promise<Array<ScheduledCourse>>
      token: (
          username: string,
          password: string
      ) => Promise<{ token: string }>
    }
  }
  put: {
    roomReservation: (
        value: RoomReservation,
        authToken?: string
    ) => Promise<unknown>
  }
}

const api: FlopAPI = {
  fetch: {
    all: {
      departments: () => fetcher(urls.departments),
      rooms: (department: string) =>
          fetcher(urls.rooms, {dept: department}),
      timeSettings: () => fetcher(urls.timesettings),
      courseTypes: (department: string) =>
          fetcher(urls.coursetypes, {dept: department}),
      roomReservationTypes: () => fetcher(urls.roomreservationtype),
      users: () => fetcher(urls.users),
    },
    target: {
      room: (id: number, additionalParams?: object) =>
          fetcher(buildUrl(urls.rooms, id.toString()), additionalParams),
      weekdays: (week: number, year: number, additionalParams?: object) =>
          fetcher(
              urls.weekdays,
              {
                week: week,
                year: year,
              },
              additionalParams
          ),
      roomReservations: (
          week: number,
          year: number,
          params: { roomId?: number },
          additionalParams?: object
      ) =>
          fetcher(
              urls.roomreservation,
              {
                ...{
                  week: week,
                  year: year,
                },
                ...{
                  ...(params.roomId && {room: params.roomId}),
                  ...(!params.roomId && {}),
                },
              },
              additionalParams
          ),
      courses: (
          week: number,
          year: number,
          params: { department?: string },
          additionalParams?: object
      ) =>
          fetcher(
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
          ),
      scheduledCourses: (
          week: number,
          year: number,
          department: string,
          additionalParams?: object
      ) =>
          fetcher(
              urls.scheduledcourses,
              {
                week: week,
                year: year,
                dept: department,
              },
              additionalParams
          ),
      token: (username: string, password: string) =>
          postData(urls.authToken, {
            username: username,
            password: password,
          }),
    },
  },
  put: {
    roomReservation: (value: RoomReservation, authToken?: string) =>
        putData(urls.roomreservation, value.id, value, authToken),
  },
}
export { api }
