<template>
    <div class="page-view">
        <div class="header">
            <router-link
            :to="{name: 'sessionView', params: {session: this.$route.params.session}}"
            >&larr;</router-link>
            <h2>{{this.$route.params.session}} - Grid {{this.$route.params.grid}}</h2>
        </div>

        <img :src="lowmag" alt="" class="lmm">
    </div>
</template>

<script>
import { store } from '@/store'

export default {
    name: 'MovieOverview',
    data() {
        return {
            store,
            path: '',
            lowmag: ''
        }
    },
    created() {
        try {
            this.path = this.store['sessions'][this.$route.params.session]['path'];
            this.lowmag = `/image${this.path}/grid${this.$route.params.grid}/lmm.png`;
        } catch (err) {
            console.log('Not loaded yet');
        }
    },
    watch: {
        store: {
            handler(newValue) {
                this.path = newValue['sessions'][this.$route.params.session]['path'];
                this.lowmag = `/image${this.path}/grid${this.$route.params.grid}/lmm.png`;
            },
            deep: true
        }
    }
}
</script>

<style scoped>
div.page-view {
  height: 100%;
  width: 100%;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 4fr 1fr;
  grid-template-rows: max-content auto auto;
  grid-template-areas: "header header" "lmm info" "movies info";
}

.header {
  grid-area: header;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
}

.header > h2 {
    font-size: 34pt;
}

.header > a {
  font-size: 24pt;
  padding-right: 1rem;
  color: #6063E0;
}

img.lmm {
    grid-area: lmm;
}
</style>