import axiosInstance from './axiosInstance'

export const getStatsSummary = (params) =>
  axiosInstance.get('/stats/summary', { params })
