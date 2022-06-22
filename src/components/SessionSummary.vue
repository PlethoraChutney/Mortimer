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
    background-color: #3F3F3F;
    min-height: 10rem;
    height: max-content;
    width: 100%;
    grid-template-columns: 25% 75%;
    grid-template-rows: 1fr;
    grid-template-areas: "name info";
    cursor: pointer;
}

div.session > h3 {
    grid-area: name;
    margin: auto;
}

div.session > p {
    grid-area: info;
    margin: auto;
}
</style>