import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { store } from '@/store'

function sendRequest(body, dest = '/mortimer/api') {
    return fetch(dest, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(body)
    })
}

sendRequest({'action': 'get_sessions'}).then(
    request => request.json()).then(
      data => {
        store.sessions = data.sessions;
      }
)

createApp(App).use(router).mount('#app')
