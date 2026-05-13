import axios from 'axios'

/**
 * Читает значение cookie по имени.
 */
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() ?? null
  }
  return null
}

const api = axios.create({
  baseURL: '/',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем CSRF-токен к каждому небезопасному запросу
api.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken')
  if (csrfToken && config.headers) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

// При 401/403 перенаправляем на страницу входа
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      const isLoginPage = window.location.pathname === '/login'
      if (!isLoginPage) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
