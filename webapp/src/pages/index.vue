<template>
  <div class="pa-8">
    <welcome-dialog></welcome-dialog>
    <v-expand-transition>
      <div v-if="error" class="mb-5">
        <v-alert class="text-black" icon="mdi-alert" color="#2bba86">
          <strong>{{ error }}</strong>
        </v-alert>
      </div>
    </v-expand-transition>
    <v-card :border="true" variant="flat" color="#F4F6F7">
      <div class="d-flex align-center justify-center py-2">
        <v-btn
          icon="mdi-arrow-right-bold-circle"
          variant="text"
          color="#2bba86"
          @click="fetchSuggestions"
        ></v-btn>
      </div>
      <v-divider></v-divider>
      <div class="grid-row">
        <div>
          <div
            ref="text"
            contenteditable
            class="pa-4"
            data-placeholder="Füge hier deinen Text ein."
            @input="updateCounter"
            @keydown="fetchSuggestionsOnEnter"
          ></div>
          <div class="d-flex justify-end pa-4 align-center">
            <p
              :class="{ 'text-error': textCounter > 1200 }"
              class="text-overline text-light-grey"
            >
              {{ textCounter }}/1.200
            </p>
          </div>
        </div>
        <div>
          <div id="suggestion-box" class="pa-4" contenteditable></div>
          <div class="d-flex pa-4 align-center">
            <img
              id="logo-loading-animation"
              src="/logo.png"
              alt="Logo"
              height="30"
              class="mr-4"
            />
            <v-select
              v-model="preferredVariant"
              :items="variants"
              bg-color="#e3e3e3"
              variant="solo"
              rounded="lg"
              label="Wähle deine Gendergerechte Sprachform aus"
              style="max-width: 350px"
              item-value="value"
              item-title="text"
              density="compact"
              hide-details
              flat
              @update:modelValue="generateReplacements"
            ></v-select>
            <v-spacer></v-spacer>
            <v-btn
              icon="mdi-content-copy"
              variant="text"
              size="small"
              @click="writeTextToClipboard"
            >
            </v-btn>
          </div>

          <v-menu
            v-model="isMenuVisible"
            :activator="menuActivator"
            location="bottom"
          >
            <v-card width="300" rounded="lg">
              <div class="pa-4">
                <h2 class="text-h5">{{ menuSuggestion?.original }}</h2>
              </div>
              <v-divider></v-divider>
              <div class="pa-4">
                <p>
                  {{ menuSuggestion.comment }}
                </p>
              </div>
              <v-divider></v-divider>
              <div class="px-4 py-2">
                <v-list class="px-0" density="compact" nav>
                  <v-list-item
                    @click="
                      replaceWord(menuSuggestion.id, menuSuggestion.original)
                    "
                  >
                    <v-icon>mdi-delete-empty</v-icon> Vorschlag verwerfen
                  </v-list-item>
                </v-list>
              </div>
              <v-divider></v-divider>
              <div class="pa-4">
                <h4>Weitere Alternativen</h4>
                <v-list class="px-0" density="compact" nav>
                  <v-list-item
                    v-for="suggestion in menuSuggestion.suggestions"
                    :key="suggestion.text"
                    :disabled="
                      suggestion.text === replacements[menuSuggestion.id]
                    "
                    @click="replaceWord(menuSuggestion.id, suggestion.text)"
                  >
                    {{ suggestion.text }}
                  </v-list-item>
                </v-list>
              </div>
            </v-card>
          </v-menu>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script lang="ts" setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useApiClient } from "../api";
import { PipelineResponse, SuggestionTarget } from "../api/client/types.gen";
import WelcomeDialog from "../components/WelcomeDialog.vue";
import { ApiError } from "../api/client/core/ApiError";

const { apiClient } = useApiClient();

const variants = [
  {
    value: "neutral",
    text: "Neutral",
  },
  {
    value: "inclusive_colon",
    text: "Inklusiv (Doppelpunkt)",
  },
  {
    value: "inclusive_underscore",
    text: "Inklusiv (Unterstrich)",
  },
  {
    value: "inclusive_star",
    text: "Inklusiv (Sternchen)",
  },
  {
    value: "inclusive_dash",
    text: "Inklusiv (Slash)",
  },
  {
    value: "inclusive_capital",
    text: "Inklusiv (Großbuchstaben)",
  },
];
const preferredVariant = ref("neutral");

const text = ref();
const textCounter = ref(0);

const updateCounter = () => {
  textCounter.value = text.value.innerText.length;
};

const pipelineResponse = ref<PipelineResponse>();
const replacements = ref<{ [key: string]: string }>({});

const isMenuVisible = ref(false);
const menuActivator = ref<string>("");
const menuSuggestion = ref<SuggestionTarget>();

const generateMenuEvent = (suggestion: SuggestionTarget) => {
  return () => {
    setTimeout(() => {
      menuActivator.value = `#suggestion-${suggestion.start}-${suggestion.stop}`;
      isMenuVisible.value = true;
      menuSuggestion.value = suggestion;
    }, 0);
  };
};

const replaceWord = async (suggestionTargetId: string, replacement: string) => {
  replacements.value[suggestionTargetId] = replacement;
  replaceText();
};

const generateReplacements = () => {
  if (!pipelineResponse.value) {
    return;
  }

  pipelineResponse.value.suggestions.forEach((suggestion) => {
    let replacement =
      suggestion.suggestions.find((s) => s.variant === preferredVariant.value)
        ?.text || suggestion.suggestions[0].text;
    replacements.value[suggestion.id] = replacement;
  });
  replaceText();
};

const fetchSuggestionsOnEnter = async (event: KeyboardEvent) => {
  if (event.shiftKey) return;
  if (event.ctrlKey) return;
  if (event.key === "Enter") {
    event.preventDefault();
    event.stopPropagation();
    await fetchSuggestions();
  }
};

const error = ref<string | false>(false);

const fetchSuggestions = async () => {
  if (text.value.innerText.length < 1) {
    return;
  }
  error.value = false;
  const start = new Date();
  document.getElementById("logo-loading-animation")!.classList.add("rotate");
  try {
    const response = await apiClient.pipeline.run({
      requestBody: {
        text: text.value.innerText,
      },
    });
    pipelineResponse.value = response;
  } catch (e: unknown) {
    const err = e as ApiError;
    if (err.status === 429) {
      error.value =
        "Die Anzahl der Anfragen ist limitiert. Du kannst es in einer Minute wieder probieren. Wenn du mehr Anfragen stellen möchtest, dann melde dich bei uns.";
    } else {
      error.value =
        "Ein Fehler ist aufgetreten. Bitte versuche es später erneut.";
    }
  } finally {
    let timeout = 800 - (new Date().getTime() - start.getTime());
    if (timeout < 0) {
      timeout = 0;
    }
    setTimeout(() => {
      generateReplacements();
      document
        .getElementById("logo-loading-animation")!
        .classList.remove("rotate");
    }, timeout);
  }
};

const replaceText = () => {
  if (!pipelineResponse.value) {
    return;
  }
  document.getElementById("suggestion-box")!.innerHTML = "";
  let textHTML = document.createElement("p");
  if (pipelineResponse.value.suggestions.length < 1) {
    textHTML.insertAdjacentText(
      "beforeend",
      pipelineResponse.value.original_text
    );
    document.getElementById("suggestion-box")!.appendChild(textHTML);
    return;
  }
  pipelineResponse.value.suggestions.reduce((prev, next) => {
    textHTML.insertAdjacentText(
      "beforeend",
      pipelineResponse.value.original_text.slice(prev, next.start)
    );
    const suggestion = document.createElement("span");
    suggestion.classList.add("suggestion");
    suggestion.id = `suggestion-${next.start}-${next.stop}`;
    suggestion.innerHTML = replacements.value[next.id];
    suggestion.addEventListener("click", generateMenuEvent(next));
    textHTML.insertAdjacentElement("beforeend", suggestion);
    return next.stop;
  }, 0);

  textHTML.insertAdjacentText(
    "beforeend",
    pipelineResponse.value.original_text.slice(
      pipelineResponse.value.suggestions.slice(-1)[0].stop
    )
  );
  document.getElementById("suggestion-box")!.replaceChildren(textHTML);
  document.getElementById("suggestion-box")!.focus();
};

const writeTextToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(
      document.getElementById("suggestion-box")!.innerText
    );
  } catch (err) {
    console.error("Failed to copy: ", err);
  }
};

onMounted(() => {
  updateCounter();
});

onBeforeUnmount(() => {
  document.getElementById("suggestion-box")!.innerHTML = "";
});
</script>

<style>
[contenteditable] {
  min-height: 200px;
}

[contenteditable]:focus {
  outline: 2px solid #696969;
}
[contenteditable]:empty:not(:focus):before {
  content: attr(data-placeholder);
  color: #d3d3d3;
  font-style: italic;
}

.text-light-grey {
  color: #d3d3d3;
}

.suggestion {
  background-color: #77d8ac;
  padding: 0 4px;
  border-radius: 4px;
  margin: 2px 2px;
  display: inline-block;
  font-weight: 700;
  color: #000;
  cursor: pointer;
}

.grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.grid-row > div:first-child {
  border-right: 1px solid #e0e0e0;
}

@media screen and (max-width: 599px) {
  .grid-row {
    display: grid;
    grid-template-columns: 1fr;
  }

  .grid-row > div:first-child {
    border-right: 0;
    border-bottom: 1px solid #e0e0e0;
  }
}

.rotate {
  animation: rotation 1s infinite linear;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}
</style>
