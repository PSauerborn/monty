<template>
    <v-container>
        <v-row align="center" justify="center">
            <v-col cols=8>
                <v-dialog v-model="dialog" max-width="50%">
                    <NewTaskModal  ref="modal" @taskCreated="updateTasks" @taskUpdated="updateTasks"/>
                </v-dialog>
                <v-toolbar>
                    <v-icon>mdi-apps</v-icon>
                    <v-divider class="mx-4" vertical></v-divider>
                    <v-toolbar-title>View, Create and Modify Tasks</v-toolbar-title>
                    <v-spacer></v-spacer>
                    <v-toolbar-items>
                        <v-btn icon @click.stop="dialog = true">
                            <v-icon>mdi-plus-box-multiple</v-icon>
                        </v-btn>
                        <v-menu offset-y>
                            <template v-slot:activator="{ on }">
                                <v-btn icon v-on=on>
                                    <v-icon>mdi-sort</v-icon>
                                </v-btn>
                            </template>
                            <v-card>
                                <v-list dense>
                                    <v-subheader>Sort By</v-subheader>
                                    <v-divider></v-divider>
                                    <v-list-item v-for="(func, index) in sortFunctions" :key="index" @click="sortTasks(func.title)">
                                        <v-list-item-avatar>
                                            <v-icon>{{ func.icon }}</v-icon>
                                        </v-list-item-avatar>
                                        <v-list-item-title>
                                            {{ func.title }}
                                        </v-list-item-title>
                                    </v-list-item>
                                </v-list>
                            </v-card>
                        </v-menu>
                        <v-btn icon @click="logout">
                            <v-icon>mdi-location-exit</v-icon>
                        </v-btn>
                    </v-toolbar-items>
                </v-toolbar>
            </v-col>
        </v-row>
        <v-row v-for="task in tasks" :key="task.task_id" class="text-center" align="center" justify="center">
            <v-col cols=6>
                <TaskItem v-bind:task="task" @deleteTask="deleteTask" @taskUpdated="updateTasks"/>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>

import axios from 'axios'
import TaskItem from './TaskItem';
import NewTaskModal from './NewTaskModal';

export default {
    name: "TaskPage",
    components: {
        TaskItem,
        NewTaskModal
    },
    methods: {
        logout() {
            window.localStorage.removeItem('userToken')
            window.location.replace("http://localhost:8081/login")
        },
        /**
         * Function used to retrieve current user tasks from the
         * monty backend. Note that all requests require the JWT
         * to be present in the request headers under the
         * Authorization: Bearer <token> scheme. Requests are made
         * using the axios module. Note that all tasks are also sorted
         * once the tasks have bee retrieved
         */
        getTasks() {
            // extract access token and URL from environment variables
            const accessToken = localStorage.getItem('userToken')
            if (!accessToken) {
                window.location.replace("http://localhost:8081/login")
                return
            }
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/tasks'

            // generate request headers using access token
            let headers = {'Authorization': 'Bearer ' + accessToken}
            let vm = this;

            axios({
                method: 'get',
                url: url,
                headers: headers
            }).then(function (response) {
                // parse payload and display notification
                 vm.tasks = response.data.payload
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully retrieved user tasks'
                })
                // sort tasks according to the currently active sort function
                vm.sortTasks(vm.activeSort)
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'failed to retrieve user tasks'
                })
                if (error.status === 401) {
                    window.location.replace("http://localhost:8081/login")
                    return
                }
            })
        },
        /**
         * Function used to sort tasks on a particular field, passed
         * as a parameter. Currently, sorting is supported by priority,
         * time remaining, created timestamp and deadline
         *
         * @param {String} field field to sort tasks on
         */
        sortTasks(field) {
            switch(field) {
                // sort tasks on priority
                case 'priority':
                    this.tasks.sort(function(a,b) { return a.priority - b.priority })
                    this.activeSort = 'priority'
                    break
                // sort tasks on remaining time to complete
                case 'duration':
                    this.tasks.sort(function(a,b) { return a.hours_remaining - b.hours_remaining})
                    this.activeSort = 'duration'
                    break
                // sort tasks on time created
                case 'created':
                    this.tasks.sort(function(a,b) { return new Date(a.created) - new Date(b.created)})
                    this.activeSort = 'created'
                    break
                case 'deadline':
                    this.tasks.sort(function(a,b) { return new Date(a.deadline) - new Date(b.deadline)})
                    this.activeSort = 'deadline'
                    break
            }
        },
        /**
         * Function used to updated tasks once a new task has been created.
         * Additionally, the modal window used to create the new task is closed
         */
        updateTasks() {
            this.dialog = false;
            this.getTasks()
        },
        /**
         * Function used to delete a task. Tasks are deleted by sending a DELETE
         * request with task ID to the backend, which removes the task from the
         * database with the given Task ID if the user has access to said task
         */
        deleteTask(taskId) {
            // extract access token and URL from environment variables
            const accessToken = localStorage.getItem('userToken')
            if (!accessToken) {
                console.log('no access token found. redirecting client to login page')
                window.location.replace("http://localhost:8081/login")
                return
            }
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/task/' + taskId

            // generate request headers using access token
            let headers = {'Authorization': 'Bearer ' + accessToken}
            let vm = this;

            axios({
                method: 'delete',
                url: url,
                headers: headers
            }).then(function (response) {
                // parse payload and display notification
                console.log(response)
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully deleted task ' + taskId
                })
                // sort tasks according to the currently active sort function
                vm.getTasks()
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'unable to delete task'
                })
                if (error.status === 401) {
                    console.log('invalid access token. redirecting to login')
                    window.location.replace("http://localhost:8081/login")
                    return
                }
            })
        }
    },
    data() {
        return {
            dialog: false,
            activeSort: "created",
            sortFunctions: [
                {title: "priority", icon: "mdi-priority-high"},
                {title: "created", icon: "mdi-sort-calendar-descending"},
                {title: "deadline", icon: "mdi-bell-alert"},
                {title: "duration", icon: "mdi-alarm-multiple"}
                ],
            tasks: [
                {
                    task_id: "42103361-680b-4bd0-866f-44ac79340a61",
                    content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                    priority: 1,
                    duration: 8,
                    hours_remaining: 3,
                    created: "2020-08-24",
                    task_title: "Suspendisse sed nisi lacus sed viverra tellus"
                },
                {
                    task_id: "7302febb-0d56-4e7f-a00f-ad64ca17cb91",
                    content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                    priority: 2,
                    duration: 36,
                    hours_remaining: 32,
                    created: "2020-08-23",
                    task_title: "Sed cras ornare arcu dui vivamus"
                },
                {
                    task_id: "2c9137bb-c47b-41a9-8796-fed68a54e719",
                    content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                    priority: 3,
                    duration: 2,
                    hours_remaining: 2,
                    created: "2020-08-19",
                    task_title: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum"
                },
                {
                    task_id: "3bded479-dfeb-4943-920d-4f12b1e5763a",
                    content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                    priority: 4,
                    duration: 9,
                    hours_remaining: 3,
                    created: "2020-08-01",
                    task_title: "Excepteur sint occaecat cupidatat non proident"
                },
                {
                    task_id: "19e086e5-031a-4391-aebe-3309170c6a6d",
                    content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                    priority: 5,
                    duration: 12,
                    hours_remaining: 8,
                    created: "2020-08-20",
                    task_title: "Odio eu feugiat pretium nibh"
                }
            ]
        }
    },
    mounted() {
        const vm = this;
        vm.tasks = vm.getTasks()
    }
}
</script>

<style scoped>

</style>