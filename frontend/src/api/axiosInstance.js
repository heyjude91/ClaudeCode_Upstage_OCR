import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 오류 인터셉터 — 전역 오류 형식 정규화
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.error?.message ||
      error.response?.data?.detail ||
      error.message ||
      '알 수 없는 오류가 발생했습니다.'
    return Promise.reject(new Error(message))
  }
)

export default axiosInstance
