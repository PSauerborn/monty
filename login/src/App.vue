<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row align="center" justify="center">
          <Login/>
        </v-row>
      </v-container>
      <notifications group="main" position="bottom right"/>
    </v-main>
  </v-app>
</template>

<script>
import Login from './components/Login';

export default {
  name: 'App',

  components: {
    Login,
  },

  data: () => ({
    //
  }),
};
</script>

<style>

@import url('https://fonts.googleapis.com/css?family=Ubuntu&display=swap');

#app {
  font-family: 'Ubuntu', 'Avenir', Helvetica, Arial, sans-serif;
}

</style>