import axios from 'axios'

// 在开发模式下使用 Vite 代理（baseURL 空字符串）；
// 在生产/预览模式下，若未配置 VITE_API_BASE，则默认指向本机后端 5002，且主机名与前端保持一致以避免 SameSite 问题。
const defaultHost = (typeof window !== 'undefined' ? window.location.hostname : 'localhost')
const baseURL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_BASE || `http://${defaultHost}:5002`)

export const http = axios.create({
  baseURL,
  withCredentials: true,
  timeout: 15000,
})

export default http


