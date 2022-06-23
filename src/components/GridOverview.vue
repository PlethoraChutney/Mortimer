<template>
  <div class="page-view">
    <div class="header">
      <h1>{{session}}</h1>
    </div>
    <div class="grids">
      <GridSummary
      v-for="(index, grid) in grids"
      :key="index"
      :name="grid"
      :grid="grids[grid]"
      :path="path"
      />
    </div>
  </div>
</template>

<script>
import GridSummary from '@/components/GridSummary.vue'
import { store } from '@/store'

export default {
    name: "GridOverview",
    props: {
        "session": String
    },
    data() {
        return {
          store,
          grids: {},
          path: ''
        };
    },
    created() {
      try {
        this.grids = this.store['sessions'][this.session]['grid_info'];
        this.path = this.store['sessions'][this.session]['path'];
      } catch(err) {
        console.log('Not loaded yet');
      }
    },
    watch: {
      store: {
        handler(newValue) {
          this.grids = newValue['sessions'][this.session]['grid_info'];
          this.path = newValue['sessions'][this.session]['path'];
        },
        deep: true
      }
    },
    components: { GridSummary }
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
  grid-template-areas: "header" "grids";
}

.header {
  grid-area: header;
}

.grids {
  grid-area: grids;
}

h1 {
  font-size: 72pt;
  margin: 0;
}

</style>
