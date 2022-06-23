<template>
<router-link :to="{name: 'sessionView', params: {session: name}}">
    <div class="session">
        <h3>{{name}}</h3>
        <p>{{session.path}}</p>
    </div>
</router-link>
</template>

<script>
export default {
    name: 'SessionSummary',
    props: {
        'name': String,
        'session': Object
    }
}
</script>

<style scoped>
div.session {
    display: grid;
    border: 1px solid #2f2f2f;
    padding: 10px;
    min-height: 10rem;
    height: max-content;
    width: 100%;
    grid-template-columns: 25% 75%;
    grid-template-rows: 1fr;
    grid-template-areas: "name info";
    cursor: pointer;
    margin-bottom: 3rem;
}

div.session > h3 {
    grid-area: name;
    margin: auto;
    font-size: 48pt;
}

div.session > p {
    grid-area: info;
    margin: auto;
    font-size: 18pt;
}
</style>