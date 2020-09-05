<template>
  <v-app>
    <v-main>
      <v-container>

        <v-row class="text-center">
          <MontyLogo />
        </v-row>

        <v-row class="text-center">
          <v-tabs centered=true>

            <v-tab>Tasks</v-tab>
            <v-tab-item>
              <TaskPage />
            </v-tab-item>

            <v-tab>Analysis</v-tab>
            <v-tab-item>
              <StatsPage />
            </v-tab-item>

          </v-tabs>
        </v-row>
      </v-container>
      <notifications group="main" position="bottom right"/>
    </v-main>
  </v-app>
</template>

<script>
  import MontyLogo from './components/MontyLogo';
  import TaskPage from './components/TaskPage';
  import StatsPage from './components/StatsPage';
  import shared from './shared';

  export default {
    name: 'App',

    components: {
      TaskPage,
      MontyLogo,
      StatsPage
    },

    data: () => ({
      //
    }),
    beforeMount: function() {
      if (process.env.VUE_APP_DEVELOPMENT_MODE == "true") {
        shared.setDevToken()
      }
      shared.getAccessToken()
    }
  };
</script>

<style>

@import url('https://fonts.googleapis.com/css?family=Ubuntu&display=swap');

#app {
  font-family: 'Ubuntu', 'Avenir', Helvetica, Arial, sans-serif;
}

</style>