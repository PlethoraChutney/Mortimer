<template>
<div class="grid">
    <h2>Grid {{name}}</h2>
    <div class="top">
        <p>Box: {{grid['Box Name']}} {{grid['Box Position']}}</p>
        <p>Protein: {{grid['Protein']}} fraction {{grid['Fraction']}}, {{grid['Concentration']}} A<sub>280</sub></p>
        <p>Grid type: {{grid['Mesh']}} mesh {{grid['Grid Type']}}</p>
        <p>FOM: {{grid['FOM']}}</p>
    </div>
    <div class="bottom">
        <p>Notes:</p>
        <p>{{grid['Notes']}}</p>
    </div>
    <img :src="lowmag">
</div>
</template>

<script>
import { store } from '@/store'

export default {
    name: 'SessionSummary',
    props: {
        'name': String,
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
    background-color: #3F3F3F;
    min-height: 10rem;
    height: max-content;
    width: 90%;
    margin: 1.5rem auto;
    grid-template-columns: 25% 1fr 480px;
    grid-template-rows: 1fr 1fr;
    grid-template-areas: "name info1 lmm" "name info2 lmm";
    cursor: pointer;
}

div.grid > h2 {
    grid-area: name;
    margin: auto;
}

div.grid p {
    margin-left: 2rem;
}
div.top {
    grid-area: info1;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
}

div.bottom {
    grid-area: info2;
}

div.grid > img {
    grid-area: lmm;
    width: 480px;
}
</style>