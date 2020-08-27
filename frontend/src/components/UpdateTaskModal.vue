<template>
    <v-card>
        <v-card-title primary-title class="justify-center">
            Update Remaining Hours
        </v-card-title>
        <v-divider class="mx-4"></v-divider>
        <v-card-text>
            <v-row align="center" justify="center">
                <v-col cols=6>
                    <v-select v-model="hourEntry" :items="hourSelection" label="Remaining Hours" data-vv-name="select" required></v-select>
                </v-col>
            </v-row>
        </v-card-text>
        <v-card-text>
            <v-row class="text-center" align="center" justify="center">
                <v-col cols=4>
                    <v-btn icon @click=updateTask><v-icon :size="64">mdi-clipboard-check</v-icon></v-btn>
                </v-col>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script>

export default {
    name: "UpdateTaskModal",
    props: {
        remainingHours: Number
    },
    methods: {
        updateTask: function() {
            this.$emit('hoursUpdated', this.hourEntry)
        }
    },
    computed: {
        hourSelection: function() {
            return [...Array(this.$props.remainingHours).keys()].reverse()
        }
    },
    data() {
        return {
            hourEntry: null
        }
    }
}

</script>