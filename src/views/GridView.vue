<template>
  <div class="home">
    <MovieOverview
    :session="$route.params.session"
    :grid="$route.params.grid"
    />
  </div>
</template>

<script>
// @ is an alias to /src
import MovieOverview from '@/components/MovieOverview.vue'

export default {
  name: 'GridView',
  components: {
    MovieOverview
  }
}
</script>