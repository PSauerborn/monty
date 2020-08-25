<template>
    <v-container id="stats-page-container">
        <v-row v-if="Object.keys(results).length < 1" class="text-center">
            <v-col cols=12 style="font-weight:bold">
                analyse performance and results of task optimization simulations
            </v-col>
        </v-row>
        <v-row v-if="Object.keys(results).length < 1" class="text-center">
            <v-col cols=12>
                <v-icon :size="72" @click="runSimulation">mdi-motion-play-outline</v-icon>
            </v-col>
        </v-row>
        <v-row v-if="Object.keys(results).length > 1" class="text-center">
            <v-col cols=12>
                <GChart type="ColumnChart" :data="chartData" :options="chartOptions"/>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>

import axios from 'axios';
import { GChart } from 'vue-google-charts'

export default {
    name: "StatsPage",
    components: {
        GChart
    },
    methods: {
        /**
         * Function used to run simulation with given user tasks
         */
        runSimulation: function() {
            const accessToken = process.env.VUE_APP_ACCESS_TOKEN
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/simulation'

            // generate request headers using access token
            let headers = {'Authorization': 'Bearer ' + accessToken}
            let vm = this;

            axios({
                method: 'get',
                url: url,
                headers: headers
            }).then(function (response) {
                // parse payload and display notification
                 vm.results = response.data.payload
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully ran task simulation'
                })
                // sort tasks according to the currently active sort function
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'failed to run task simulation'
                })
            })
        },
        formatSimType: function(simType) {
            var result = simType.replace('_', ' ').replace('_', ' ')
            return result.replace(/(^\w|\s\w)/g, m => m.toUpperCase())
        }

    },
    computed: {
        /**
         * Computed property used to format calculated simulation results
         * in format needed by the Graph
         */
        chartData() {
            var data = [['Sim Type', 'Completed', 'Important Completed', 'Completed in Time']]
            let vm = this;
            Object.keys(vm.results).forEach((key) => {
                data.push(
                    [vm.formatSimType(key), vm.results[key]['completed'], vm.results[key]['important_completed'], vm.results[key]['completed_in_time']]
                )
            })
            return data
        },
        chartOptions() {
            return {
                vAxis: {
                    title: 'Percentage of Tasks Completed'
                },
                legend: {
                    position: 'top'
                }
            }
        }
    },
    data() {
        return {
            results: {}
        }
    }
}
</script>

<style scoped>

</style>