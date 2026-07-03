import axios from 'axios'

const api = axios.create({ baseURL: '' })

export const getPlans = (params) => api.get('/api/plans', { params })
export const getCompare = () => api.get('/api/plans/compare')
export const getChanges = (params) => api.get('/api/changes', { params })
export const getPositioning = () => api.get('/api/reports/positioning')
export const getChangesSummary = () => api.get('/api/changes/summary')