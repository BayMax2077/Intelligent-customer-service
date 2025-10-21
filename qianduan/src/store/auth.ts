import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    authed: Boolean(localStorage.getItem('authed')),
    username: localStorage.getItem('username') || '',
  }),
  getters: {
    isAuthed: (state) => state.authed,
  },
  actions: {
    setAuthed(val: boolean, username?: string) {
      this.authed = val
      if (val) {
        localStorage.setItem('authed', '1')
        if (username) {
          this.username = username
          localStorage.setItem('username', username)
        }
      } else {
        localStorage.removeItem('authed')
        localStorage.removeItem('username')
        this.username = ''
      }
    },
  },
})


