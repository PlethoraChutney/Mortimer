<template>
<router-link
:to="{name: 'gridView', params: {session: session, grid: name}}"
>
    <div class="grid">
        <h2>Grid {{name}}</h2>
        <div class="top container">
            <div>
                <p>Box</p><p>{{grid['Box Name']}} {{grid['Box Position']}}</p>
            </div>
            <div>
                <p>Protein</p><p>{{grid['Protein']}} fraction {{grid['Fraction']}}, {{grid['Concentration']}} A<sub>280</sub></p>
            </div>
        </div>
        <div class="bottom container">
            <div>
                <p>Grid type</p><p>{{grid['Mesh']}} mesh {{grid['Grid Type']}}</p>
            </div>
            <div>
                <p>FOM</p><p>{{grid['FOM']}}</p>
            </div>
            <div v-if="grid['Notes']">
                <p>Notes</p>
                <p>{{grid['Notes']}}</p>
            </div>
        </div>
        <img :src="lowmag">
    </div>
</router-link>
</template>

<script>
import { store } from '@/store'

export default {
    name: 'SessionSummary',
    props: {
        'name': String,
        'session': String,
        'path': String,
        'grid': Object
    },
    data() {
        return {store};
    },
    computed: {
        lowmag() {
            return `/image${this.path}/grid${this.name}/lmm.png`
        }
    }
}
</script>

<style scoped>
div.grid {
    display: grid;
    border: 1px solid #2f2f2f;
    padding: 10px;
    min-height: 10rem;
    height: max-content;
    width: 90%;
    margin: 1.5rem auto;
    grid-template-columns: 20% 1fr 480px;
    grid-template-rows: 1fr 1fr;
    grid-template-areas: "name info1 lmm" "name info2 lmm";
    cursor: pointer;
}

div.grid > h2 {
    grid-area: name;
    margin: auto;
    font-size: 48pt;
}

div.grid p {
    margin-left: 2rem;
}
div.top {
    grid-area: info1;
}

div.container {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
}

div.container > div {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
}

div.container > div > p:first-child {
    font-weight: bold;
    border-bottom: 1px solid #2f2f2f;
}

div.bottom {
    grid-area: info2;
}

div.grid > img {
    grid-area: lmm;
    width: 480px;
}

p {
    padding: 0;
    margin: 0;
    font-size: 18pt;
}
</style>