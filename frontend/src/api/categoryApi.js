import axiosInstance from './axiosInstance'

export const getCategories = () =>
  axiosInstance.get('/categories')
