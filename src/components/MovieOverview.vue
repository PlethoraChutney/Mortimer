<template>
    <div class="page-view">
        <div class="header">
            <router-link
            :to="{name: 'sessionView', params: {session: this.$route.params.session}}"
            >&larr;</router-link>
            <h2>{{this.$route.params.session}} - Grid {{this.$route.params.grid}}</h2>
            <div 
            class="button"
            @click="markGrid('Collect')"
            :class="{'greyed-out': ['Keep', 'Toss'].includes(this.info['State'])}"
            style="background-color: #E0C960; color: black;"
            >Collect</div>
            <div 
            class="button"
            @click="markGrid('Keep')"
            :class="{'greyed-out': ['Collect', 'Toss'].includes(this.info['State'])}"
            style="background-color: #6063E0;"
            >Keep</div>
            <div 
            class="button"
            @click="markGrid('Toss')"
            :class="{'greyed-out': ['Collect', 'Keep'].includes(this.info['State'])}"
            style="background-color: black;"
            >Toss</div>
        </div>

        <img :src="lowmag" alt="" class="lmm">

        <div class="grid-info">
            <div
            v-for="(key, param) in this.info"
            :key="key"
            >
                <p>{{param}}</p>
                <p>{{this.info[param]}}</p>
            </div>
            <div>
                <div
                class="button"
                @click="moveGrid()"
                >
                    Move Grid
                </div>
            </div>
        </div>

        <div class="movies">
            <img
            v-for="(movie, key) in this.imagePaths"
            :key="key"
            :src="movie" alt="">
        </div>
    </div>
</template>

<script>
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

export default {
    name: 'MovieOverview',
    data() {
        return {
            store,
            path: '',
            lowmag: '',
            info: {},
            imagePaths: []
        }
    },
    created() {
        try {
            this.path = this.store['sessions'][this.$route.params.session]['path'];
            this.lowmag = `/mortimer/image${this.path}/grid${this.$route.params.grid}/lmm.png`;
            this.info = this.store['sessions'][this.$route.params.session]['grid_info'][this.$route.params.grid];
        } catch (err) {
            this.path = '';
        }

        this.getNewImages();
    },
    watch: {
        store: {
            handler(newValue) {
                this.path = newValue['sessions'][this.$route.params.session]['path'];
                this.lowmag = `/mortimer/image${this.path}/grid${this.$route.params.grid}/lmm.png`;
                this.info = newValue['sessions'][this.$route.params.session]['grid_info'][this.$route.params.grid];
                this.getNewImages();
            },
            deep: true
        }
    },
    methods: {
        getNewImages() {
            sendRequest({
                'action': 'check_images',
                'path': this.path,
                'grid': this.$route.params.grid
            }).then(
                request => request.json()
            ).then(
                data => {
                    this.imagePaths = data.image_paths;
                }
            )
        },
        markGrid(newState) {
            sendRequest({
                'action': 'mark_grid',
                'session': this.$route.params.session,
                'grid': this.$route.params.grid,
                'state': newState
            })

            this.store.sessions[this.$route.params.session]['grid_info'][this.$route.params.grid]['State'] = newState;
        },
        moveGrid() {
            const newLocation = prompt('Move grid where?');
            sendRequest({
                'action': 'move_grid',
                'session': this.$route.params.session,
                'grid': this.$route.params.grid,
                'location': newLocation
            })

            this.store.sessions[this.$route.params.session]['grid_info'][this.$route.params.grid]['Moved To'] = newLocation;
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
  border-bottom: 1px solid #2f2f2f;
}

div.button {
    padding: 10px;
    margin-left: 20px;
    border: 1px solid white;
    cursor: pointer;
}

div.button.greyed-out {
    opacity: 0.25;
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
    max-width: 100%;
    max-height: 80vh;
    margin: auto;
}

div.grid-info {
    grid-area: info;
    display: grid;
    grid-template-columns: 1fr 1fr;
    border-left: 1px solid #2f2f2f;
}

div.grid-info > div {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
}

div.grid-info > div > p:first-child {
    font-weight: bold;
    border-bottom: 1px solid #2f2f2f;
}

div.movies {
    grid-area: movies;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    overflow-x: scroll;
}

div.movies > img {
    max-width: 720px;
    margin: 20px 10px;
}
</style>