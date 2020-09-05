<template>
    <v-card>
        <v-card-title>Create New Task</v-card-title>
        <v-divider class="mx-4"></v-divider>
        <v-card-subtitle>generate a new task and stick it into the database</v-card-subtitle>
        <v-card-text>
            <ValidationObserver ref="observer" v-slot="{ }">
                <form ref="form">
                    <v-row align="center" justify="center">
                        <v-col cols=6>
                            <ValidationProvider v-slot="{ errors }" name="Task Title" rules="required|max:25">
                                <v-text-field v-model="taskTitle" :counter="25" :error-messages="errors"
                                    label="Task Title" required>
                                </v-text-field>
                            </ValidationProvider>
                        </v-col>
                    </v-row>
                    <v-row align="center" justify="center">
                        <v-col cols=6>
                            <ValidationProvider v-slot="{ errors }" name="Task Content" rules="required|max:120">
                                <v-textarea :no-resize=true v-model="taskContent" :counter="120"
                                    :error-messages="errors" label="Task Content" required>
                                </v-textarea>
                            </ValidationProvider>
                        </v-col>
                    </v-row>
                    <v-row align="center" justify="center">
                        <v-col cols=6>
                            <ValidationProvider v-slot="{ errors }" name="priority" rules="required">
                                <v-select v-model="taskPriority" :items="[1,2,3,4,5]" :error-messages="errors"
                                    label="Priority" data-vv-name="select" required></v-select>
                            </ValidationProvider>
                        </v-col>
                    </v-row>
                    <v-row align="center" justify="center">
                        <v-col cols=6>
                            <ValidationProvider v-slot="{ errors }" name="Task Duration" rules="required|numeric">
                                <v-text-field v-model="taskDuration" :error-messages="errors" label="Task Duration"
                                    required>
                                </v-text-field>
                            </ValidationProvider>
                        </v-col>
                    </v-row>
                    <v-row align="center" justify="center">
                        <v-col cols=6>
                            <v-menu ref="menu" v-model="menu" :close-on-content-click="false" :return-value.sync="taskDeadline"
                                transition="scale-transition" offset-y min-width="290px">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-text-field v-model="taskDeadline" label="Task Deadline" v-bind="attrs" v-on="on"></v-text-field>
                                </template>
                                <v-date-picker v-model="taskDeadline" no-title scrollable>
                                    <v-spacer></v-spacer>
                                    <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
                                    <v-btn text color="primary" @click="$refs.menu.save(taskDeadline)">OK</v-btn>
                                </v-date-picker>
                            </v-menu>
                        </v-col>
                    </v-row>
                </form>
            </ValidationObserver>
        </v-card-text>
        <v-card-text>
            <v-row class="text-center" align="center" justify="center">
                <v-col cols=4>
                    <v-btn @click=submit()>Create Task</v-btn>
                </v-col>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script>

import axios from 'axios'
import { required, numeric, max } from 'vee-validate/dist/rules'
import { extend, ValidationObserver, ValidationProvider, setInteractionMode } from 'vee-validate'
import shared from '../shared'

setInteractionMode('eager')

extend('required', {
    ...required,
    message: '{_field_} can not be empty',
})

extend('max', {
    ...max,
    message: '{_field_} may not be greater than {length} characters',
})

extend('numeric', {
    ...numeric,
    message: '{_field_} must be numeric value',
})


export default {
    name: "NewTaskModal",
    components: {
        ValidationProvider,
        ValidationObserver
    },
    props: {

    },
    methods: {
        /**
         * Function used to create a new task in the database. Note
         * that, before the request is sent, all input fields are
         * checked using the provided validators (if relevant). Requests
         * are then sent using a POST request, and a success message
         * is returned containing the new task ID
         */
        submit: async function () {
            // validate input form entries and construct payload
            const isValid = await this.$refs.observer.validate();
            if (!isValid) {
                this.$notify({
                    group: 'main',
                    title: 'Invalid Task',
                    type: 'error',
                    text: 'invalid task. check inputs and try again'
                })
                return
            }
            // construct payload from form inputs
            const payload = {
                task_title: this.taskTitle,
                content: this.taskContent,
                priority: this.taskPriority,
                duration: this.taskDuration,
                deadline: this.taskDeadline
            }

            // extract access token and URL from environment variables
            const url = process.env.VUE_APP_MONTY_BACKEND_URL + '/task'
            // generate request headers using access token
            let vm = this;

            axios({
                method: 'post',
                data: payload,
                url: url,
                headers: {'Authorization': 'Bearer ' + shared.getAccessToken()}
            }).then(function (response) {
                 vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'success',
                    text: 'successfully created new task ' + response.data.payload.task_id
                })
                // emit event to parent in order to close modal
                vm.$emit('taskCreated')
            }).catch(function (error) {
                console.log(error)
                vm.$notify({
                    group: 'main',
                    title: ' monty backend',
                    type: 'error',
                    text: 'failed to create new task'
                })
                if (error.status === 401) {
                    shared.redirectLogin()
                }
            })
        },
    },
    data() {
        return {
            dialog: false,
            taskTitle: "",
            taskContent: "",
            taskPriority: "",
            taskDuration: "",
            taskDeadline: new Date().toISOString().substr(0, 10),
            menu: false,
        }
    }
}
</script>

<style scoped>

</style>