import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import { createPinia } from "pinia";

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import { fa } from "vuetify/iconsets/fa";
import "@mdi/font/css/materialdesignicons.css"; 
import "@fortawesome/fontawesome-free/css/all.css";
const vuetify = createVuetify({
    
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
            fa,
        }
      },
})
  
const app = createApp(App);
app.use(vuetify)
app.use(createPinia())
app.mount('#app')
