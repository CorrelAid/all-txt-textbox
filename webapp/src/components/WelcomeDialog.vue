<template>
  <v-dialog v-model="isDialogActive" max-width="700">
    <template v-slot:default="{ isActive }">
      <v-card>
        <v-card-title class="text-center">Willkommen</v-card-title>
        <v-card-text class="text-center">
          <p class="mb-2">
            Schön, dass du dich für die App entschieden hast. Hier kannst du
            deine eigenen Texte analysieren und verbessern.
          </p>
          <p class="mb-2">
            Die von dir eingegebenen Text werden in unserer Datenbank
            gespeichert. Wir benutzen die Daten, um unsere Algorithmen noch
            besser zu machen. Mit deinem Text wird auch eine Session
            gespeichert. Diese benutzen wir, um zu analysieren, wie lange du
            unsere App nutzt und wie sich dein Text während der Nutzung
            verändert.
          </p>
          <p>
            Mit der Nutzung der App bestätigst du, dass die von dir eingegebenen
            Daten gespeichert werden.
          </p>
        </v-card-text>

        <v-card-actions class="justify-center">
          <v-btn
            color="#2bba86"
            variant="flat"
            text="Jetzt loslegen"
            @click="isActive.value = false"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";

const isDialogActive = ref(true);
</script>
