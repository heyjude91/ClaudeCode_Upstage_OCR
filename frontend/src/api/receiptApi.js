import axiosInstance from './axiosInstance'

export const uploadReceipt = (file) => {
  const form = new FormData()
  form.append('file', file)
  return axiosInstance.post('/receipts/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}

export const getReceipts = (params) =>
  axiosInstance.get('/receipts', { params })

export const getReceipt = (id) =>
  axiosInstance.get(`/receipts/${id}`)

export const updateReceipt = (id, data) =>
  axiosInstance.put(`/receipts/${id}`, data)

export const deleteReceipt = (id) =>
  axiosInstance.delete(`/receipts/${id}`)
