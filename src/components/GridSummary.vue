<template>
<router-link
:to="{name: 'gridView', params: {session: session, grid: name}}"
>
    <div class="grid">
        <div id="grid-name">
            <h2>Grid {{name}}</h2>
            <div
            v-if="grid['State']"
            class="state"
            :class="grid['State']"
            >
                {{this.grid['State']}}
            </div>
        </div>
        <div class="container">
            <div>
                <p>Box</p><p>{{grid['Box Name']}} {{grid['Box Position']}}</p>
            </div>
            <div>
                <p>Protein</p><p>{{grid['Protein']}} fraction {{grid['Fraction']}}, {{grid['Concentration']}} A<sub>280</sub></p>
            </div>
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
            <div
            v-if="grid['Moved To']">
                <p>Moved To</p>
                <p>{{grid['Moved To']}}</p>
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
            return `/mortimer/image${this.path}/grid${this.name}/lmm.png`
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
    grid-template-rows: 1fr;
    grid-template-areas: "name info1 lmm" "name info2 lmm";
    cursor: pointer;
}

#grid-name {
    grid-area: name;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: auto;
    height: max-content;
}

#grid-name > h2 {
    font-size: 48pt;
}

div.grid p {
    margin: 0;
}

div.container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
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

div.grid > img {
    grid-area: lmm;
    width: 480px;
}

p {
    padding: 0;
    margin: 0;
    font-size: 18pt;
}

div.state {
    padding: 10px;
    width: max-content;
    margin: auto;
    border: 1px solid white;
}

div.state.Collect {
    background-color: #E0C960;
    color: black;
}

div.state.Keep {
    background-color: #6063E0;
}

div.state.Toss {
    background-color: black;
}
</style>