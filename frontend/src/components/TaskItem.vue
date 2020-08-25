<template>
    <v-sheet>
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
            <v-card-title>
                {{ task.task_title }}
            </v-card-title>
            <v-card-subtitle>
                {{ task.task_id }}
            </v-card-subtitle>
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

import moment from 'moment'

export default {
    name: "TaskItem",
    components: {

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
        }
    },
    data() {
        return {
            taskColors: {
                1: "5px solid red",
                2: "5px solid #FFA232",
                3: "5px solid #FFFA63",
                4: "5px solid #6DFF73",
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

</style>