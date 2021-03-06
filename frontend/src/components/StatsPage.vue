<template>
    <v-container id="stats-page-container" fluid>
        <v-row align="center" justify="center">
            <v-col cols=4 align="center" justify="center" class="chart-column">
                <apexchart width="500" type="bar" :options="metricChartOptions" :series="metrics"/>
            </v-col>
            <v-divider class="mx-4" vertical="true"></v-divider>
            <v-col cols=4 align="center" justify="center" class="chart-column">
                <apexchart width="500" type="donut" :options="donutChartOptions" :series="donut"/>
            </v-col>
        </v-row>
        <v-divider class="mx-4"></v-divider>
        <v-row align="center" justify="center">
            <v-col cols=6 align="center" justify="center" class="chart-column">
                <apexchart width="1000" height="250" type="bar" :options="simulationChartOptions" :series="simulation"/>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>

import axios from 'axios';
import shared from '../shared';

export default {
    name: "StatsPage",
    components: {

    },
    methods: {
        /**
         * Function used to run simulation with given user tasks
         */
        runSimulation: function() {
            // extract access token and URL from environment variables
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/simulation'

            // generate request headers using access token
            let vm = this;

            axios({
                method: 'get',
                url: url,
                headers: {'Authorization': 'Bearer ' + shared.getAccessToken()}
            }).then(function (response) {
                // parse payload and display notification
                 vm.simulationResults = response.data.payload
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
                if (error.status === 401) {
                    shared.redirectLogin()
                }
            })
        },
        formatSimType: function(simType) {
            var result = simType.replace('_', ' ').replace('_', ' ')
            return result.replace(/(^\w|\s\w)/g, m => m.toUpperCase())
        },
        getUserMetrics() {
            // extract access token and URL from environment variables
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + `/metrics/${this.start}/${this.end}`

            // generate request headers using access token
            let vm = this;

            axios({
                method: 'get',
                url: url,
                headers: {'Authorization': 'Bearer ' + shared.getAccessToken()}
            }).then(function (response) {
                // parse payload and display notification
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully ran task simulation'
                })
                // sort tasks according to the currently active sort function
                vm.metricResults = response.data.payload
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'failed to run task simulation'
                })
                if (error.status === 401) {
                    shared.redirectLogin()
                }
            })
        }
    },
    computed: {
        metricChartOptions() {
            return {
                chart: {
                    id: 'user-metrics'
                },
                xaxis: {
                    categories: ['Total Tasks', 'Tasks Completed', 'Tasks Completed in Time']
                }
            }
        },
        metrics() {
            const values = this.metricResults
            const series = [{
                name: 'user-metrics',
                data: [
                    values.total_tasks,
                    values.completed_tasks,
                    values.completed_in_time
                ]
            }]
            console.log('returning series data ' + JSON.stringify(series))
            return series
        },
        donutChartOptions() {
            return {
                chart: {
                    id: 'user-metrics'
                },
                xaxis: {
                    categories: ['Tasks Completed', 'Tasks Completed in Time']
                },
                labels: ['Completed', 'Completed in Time']
            }
        },
        donut() {
            const values = this.metricResults
            const series = [
                    values.completed_tasks,
                    values.completed_in_time
                ]
            console.log('returning series data ' + JSON.stringify(series))
            return series
        },
        simulationChartOptions() {
            return {
                chart: {
                    id: 'simulation-results'
                },
                xaxis: {
                    categories: [
                        'As They Come', 'Due First', 'Due Last', 'Important First',
                        'Easier First', 'Easier, Important First', 'Easier, Due First'
                    ]
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        endingShape: 'rounded'
                    }
                }

            }
        },
        simulation() {
            const values = this.simulationResults
            console.log(JSON.stringify(values))
            const series = [
                {
                    name: 'Completed',
                    data: [
                        values.as_they_come.completed, values.due_first.completed, values.due_last.completed,
                        values.important_first.completed, values.easier_first.completed, values.easier_important_first.completed,
                        values.easier_due_first.completed
                    ]
                },
                {
                    name: 'Completed In Time',
                    data: [
                        values.as_they_come.completed_in_time, values.due_first.completed_in_time, values.due_last.completed_in_time,
                        values.important_first.completed_in_time, values.easier_first.completed_in_time, values.easier_important_first.completed_in_time,
                        values.easier_due_first.completed_in_time
                    ]
                },
                {
                    name: 'Important Completed',
                    data: [
                        values.as_they_come.important_completed, values.due_first.important_completed, values.due_last.important_completed,
                        values.important_first.important_completed, values.easier_first.important_completed, values.easier_important_first.important_completed,
                        values.easier_due_first.important_completed
                    ]
                }
            ]
            return series
        }
    },
    data() {
        return {
            start: '2020-06-01',
            end: '2020-09-05',
            simulationResults: {
                as_they_come: { completed: 0, completed_in_time: 0, important_completed: 0 },
                due_first: { completed: 0, completed_in_time: 0, important_completed: 0 },
                due_last: { completed: 0, completed_in_time: 0, important_completed: 0 },
                important_first: { completed: 0, completed_in_time: 0, important_completed: 0 },
                easier_first: { completed: 0, completed_in_time: 0, important_completed: 0 },
                easier_important_first: { completed: 0, completed_in_time: 0, important_completed: 0 },
                easier_due_first: { completed: 0, completed_in_time: 0, important_completed: 0 }
            },
            metricResults: { total_tasks: 0, completed_tasks: 0, completed_in_time: 0 }
        }
    },
    mounted() {
        this.getUserMetrics()
        this.runSimulation()
    }
}
</script>

<style scoped>

.chart-column {
    margin: 20px;
}

</style>