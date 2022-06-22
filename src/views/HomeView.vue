<template>
  <div class="home">
    <SessionOverview
    :sessions="store.sessions"
    />
  </div>
</template>

<script>
// @ is an alias to /src
import SessionOverview from '@/components/SessionOverview.vue'
import { store } from '@/store'

function sendRequest(body, dest = '/api') {
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

export default {
  name: 'HomeView',
  components: {
    SessionOverview
  },
  data() {
    return {
      store
    }
  },
  created() {
    this.getSessions();
  },
  methods: {
    getSessions() {
      sendRequest({'action': 'get_sessions'}).then(
      request => request.json()).then(
        data => {
          this.store.sessions = data.sessions;
        }
      )
    }
  }
}
</script>
