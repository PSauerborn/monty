<template>
    <v-sheet>
        <v-dialog v-model="dialog" max-width="20%">
            <UpdateTaskModal ref="updateModal" :remainingHours="task.hours_remaining" @hoursUpdated="editTask"/>
        </v-dialog>
        <v-card :id="task.task_id">
            <v-row class="text-center" style="font-size:12px">
                <v-col cols=3>
                    Priority: {{ task.priority }}
                </v-col>
                <v-col cols=3>
                    Created: {{ createdDate }}
                </v-col>
                <v-col cols=3>
                    Deadline: {{ deadlineDate }}
                </v-col>
                <v-col cols=2 align="right" justify="right">
                    <v-icon :size="18" @click="deleteTask">mdi-delete</v-icon>
                </v-col>
            </v-row>

            <v-divider class="mx-4"></v-divider>
            <v-row>
                <v-col cols=9>
                    <v-card-title>
                        <span :class="{ crossedOut: completed }">{{ task.task_title }}</span>
                    </v-card-title>
                    <v-card-subtitle>
                        {{ task.task_id }}
                    </v-card-subtitle>
                </v-col>
                <v-col cols=1 align="right" justify="right">
                    <v-btn icon>
                        <v-icon @click.stop="dialog=true">mdi-circle-edit-outline</v-icon>
                    </v-btn>
                </v-col>
                <v-col cols=2 align="left" justify="left">
                    <v-btn icon>
                        <v-icon @click="completeTask">mdi-check-all</v-icon>
                    </v-btn>
                </v-col>
            </v-row>
            <v-divider class="mx-4"></v-divider>

            <v-row class="text-center" style="font-size:12px">
                <v-col cols=6>
                    Duration: {{ task.duration }}
                </v-col>
                <v-col cols=6>
                    Remaining: {{ task.hours_remaining }}
                </v-col>
            </v-row>
            <v-divider class="mx-4"></v-divider>
            <v-card-text>
                {{ task.content }}
            </v-card-text>
        </v-card>
    </v-sheet>
</template>

<script>

import axios from 'axios'
import moment from 'moment'

import UpdateTaskModal from './UpdateTaskModal'

export default {
    name: "TaskItem",
    components: {
        UpdateTaskModal
    },
    props: {
        task: {
            type: Object,
            default: function() {
                return {
                    task_id: "7302febb-0d56-4e7f-a00f-ad64ca17cb91",
                    content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                    priority: 3,
                    duration: 36,
                    task_title: "Sed cras ornare arcu dui vivamus"
                }
            }
        }
    },
    methods: {
        deleteTask: function() {
            this.$emit('deleteTask', this.task.task_id)
        },
        editTask: function(remainingHours) {
            this.dialog = false;
            // extract access token and URL from environment variables
            const accessToken = localStorage.getItem('userToken')
            if (!accessToken) {
                window.location.replace("http://localhost:8081/login")
                return
            }
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/task/' + this.task.task_id + '?operation=UPDATE'

            // generate request headers using access token
            let headers = {'Authorization': 'Bearer ' + accessToken}
            let vm = this;

            axios({
                method: 'patch',
                url: url,
                headers: headers,
                data: {remaining_hours: remainingHours }
            }).then(function (response) {
                // parse payload and display notification
                console.log(response)
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully edited task ' + vm.task.task_id
                })
                vm.$emit('taskUpdated')
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'unable to edit task'
                })
                if (error.status === 401) {
                    window.location.replace("http://localhost:8081/login")
                    return
                }
            })
        },
        completeTask: function() {
            const accessToken = process.env.VUE_APP_ACCESS_TOKEN
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/task/' + this.task.task_id + '?operation=COMPLETE'

            // generate request headers using access token
            let headers = {'Authorization': 'Bearer ' + accessToken}
            let vm = this;

            axios({
                method: 'patch',
                url: url,
                headers: headers,
                data: {}
            }).then(function (response) {
                // parse payload and display notification
                console.log(response)
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully completed task ' + vm.task.task_id
                })
                // sort tasks according to the currently active sort function
                vm.$emit('taskUpdated')
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'unable to complete task'
                })
            })
        }
    },
    computed: {
        borderColor: function() {
            return this.taskColors[this.task.priority]
        },
        createdDate: function() {
            return moment(String(this.task.created)).format('MM/DD/YYYY')
        },
        deadlineDate: function() {
            return moment(String(this.task.deadline)).format('MM/DD/YYYY')
        },
        completed: function() {
            console.log(this.task.completion_date)
            return this.task.completion_date != null
        }
    },
    data() {
        return {
            dialog: false,
            taskColors: {
                1: "5px solid #FF4B4B",
                2: "5px solid #FFA232",
                3: "5px solid #FFFA63",
                4: "5px solid #C7FF4B",
                5: "5px solid #6DCCFF"
            }
        }
    },
    mounted() {
        let vm = this;

        var card = document.getElementById(vm.task.task_id);
        card.style.borderLeft = vm.borderColor
    }
}
</script>

<style scoped>

.crossedOut {
    text-decoration: line-through;
}

</style>