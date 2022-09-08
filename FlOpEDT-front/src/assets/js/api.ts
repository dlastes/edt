function getCookie (name) {
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

async function fetchData (url, params) {
  let providedParams = params

  params = Object.assign({
    method: 'GET',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
  }, params)

  params.headers = Object.assign({
    'X-CSRFToken': csrfToken,
    'Content-Type': 'application/json',
  }, params.headers)

  let args = ''

  if (providedParams) {
    args = Object.keys(providedParams).map((p) => p + '=' + providedParams[p]).join('&')
  }
  let finalUrl = `${import.meta.env.VITE_API_ENDPOINT}${url}/?${args}`

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
  rooms: 'fetch/idroom',
  weekdays: 'fetch/weekdays',
  timesettings: 'base/timesettings',
}

const fetcher = (url: string, params?: object) => fetchData(url, params)

function buildUrl (base: string, uri: string) {
  return `${base}/${uri}`
}

const api = {
  fetch: {
    all: {
      departments: () => fetcher(urls.departments),
      rooms: () => fetcher(urls.rooms),
      timesettings: () => fetcher(urls.timesettings),
    },
    target: {
      room: (id) => fetcher(buildUrl(urls.rooms, id)),
      weekdays: (week: number, year: number) => fetcher(urls.weekdays, {week: week, year: year}),
    }
  },
}
export { api }
