<template>
  <div class="home">
    <GridOverview
    :session="$route.params.session"
    />
  </div>
</template>

<script>
// @ is an alias to /src
import GridOverview from '@/components/GridOverview.vue'

export default {
  name: 'SessionView',
  components: {
    GridOverview
  }
}
</script>
