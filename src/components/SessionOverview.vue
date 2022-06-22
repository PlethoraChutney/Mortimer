<template>
  <div class="page-view">
    <div class="header">
      <h1>Mortimer</h1>
      <p>A screening assistant</p>
    </div>
    <div class="sessions">
      <SessionSummary
      v-for="(index, session) in sessions"
      :key="index"
      :name="session"
      :session="sessions[session]"
      />
    </div>
  </div>
</template>

<script>
import SessionSummary from '@/components/SessionSummary.vue'

export default {
    name: "SessionOverview",
    props: {
        "sessions": Object
    },
    components: { SessionSummary }
}
</script>

<style scoped>
div.page-view {
  height: 100%;
  width: 100%;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: max-content auto;
  grid-template-areas: "header" "sessions";
}

.header {
  grid-area: header;
}

.sessions {
  grid-area: sessions;
}

h1 {
  font-size: 72pt;
  margin: 0;
}

</style>
