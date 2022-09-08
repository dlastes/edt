import type { Department, Room, RoomReservation, TimeSettings } from '@/assets/js/types'

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
  roomreservation: 'roomreservations/reservation'
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
    },
    target: {
      room: (id: number, additionalParams?: object) => Promise<Room>,
      weekdays: (week: number, year: number, additionalParams?: object) => Promise<any>,
      roomReservations: (id: number, additionalParams?: object) => Promise<RoomReservation>,
    },
  },
}

const api: FlopAPI = {
  fetch: {
    all: {
      departments: () => fetcher(urls.departments),
      rooms: (department: string) => fetcher(urls.rooms, {dept: department}),
      timeSettings: () => fetcher(urls.timesettings),
    },
    target: {
      room: (id: number, additionalParams?: object) => fetcher(buildUrl(urls.rooms, id.toString()), additionalParams),
      weekdays: (week: number, year: number, additionalParams?: object) => fetcher(urls.weekdays, {
        week: week,
        year: year
      }, additionalParams),
      roomReservations: (idRoom: number, additionalParams?: object) => fetcher(urls.roomreservation, {room_id: idRoom}, additionalParams)
    }
  },
}
export { api }
