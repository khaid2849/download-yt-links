<script setup>
import { ref, computed, onMounted } from "vue";

const urls = ref("");
const quality = ref("best");
const videoInfo = ref(null);
const loading = ref(false);
const error = ref("");
const downloading = ref(false);
const progress = ref({ percent: "0%", status: "" });
const downloadReady = ref(false);
const downloadUrl = ref("");
const darkMode = ref(false);
const showSuccessAnimation = ref(false);
let downloadId = "";

// Check for system dark mode preference
onMounted(() => {
  if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    darkMode.value = true;
  }
});

// Computed properties for dynamic styling
const progressPercentage = computed(() => {
  const percent = parseInt(progress.value.percent) || 0;
  return Math.min(percent, 100);
});

const qualityOptions = [
  { value: "best", label: "Best Quality", icon: "✨" },
  { value: "high", label: "High (1080p)", icon: "🎯" },
  { value: "medium", label: "Medium (720p)", icon: "📺" },
  { value: "low", label: "Low (480p)", icon: "📱" },
];

async function fetchInfo() {
  error.value = "";
  videoInfo.value = null;
  loading.value = true;
  try {
    const res = await fetch("/video-info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: urls.value.split("\n")[0].trim() }),
    });
    const data = await res.json();
    if (res.ok) {
      videoInfo.value = data;
    } else {
      error.value = data.error || "Failed to fetch video info.";
    }
  } catch (e) {
    error.value = "Network error.";
  } finally {
    loading.value = false;
  }
}

async function startDownload() {
  error.value = "";
  downloading.value = true;
  downloadReady.value = false;
  showSuccessAnimation.value = false;
  progress.value = { percent: "0%", status: "downloading" };
  try {
    const res = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        urls: urls.value
          .split("\n")
          .map((u) => u.trim())
          .filter(Boolean),
        quality: quality.value,
      }),
    });
    const data = await res.json();
    if (res.ok) {
      downloadId = data.download_id;
      pollProgress();
    } else {
      error.value = data.error || "Failed to start download.";
      downloading.value = false;
    }
  } catch (e) {
    error.value = "Network error.";
    downloading.value = false;
  }
}

async function pollProgress() {
  if (!downloadId) return;
  let done = false;
  while (!done) {
    await new Promise((r) => setTimeout(r, 1500));
    const res = await fetch(`/progress/${downloadId}`);
    const data = await res.json();
    progress.value = {
      percent: data.percent || "0%",
      status: data.status || "",
    };
    if (data.status === "completed" || data.status === "finished") {
      done = true;
      downloading.value = false;
      downloadReady.value = true;
      downloadUrl.value = `/download-file/${downloadId}`;
      showSuccessAnimation.value = true;
      setTimeout(() => (showSuccessAnimation.value = false), 3000);
    }
    if (data.status === "not_found" || data.status === "error") {
      error.value = "Download failed or not found.";
      downloading.value = false;
      break;
    }
  }
}

function toggleDarkMode() {
  darkMode.value = !darkMode.value;
}

function formatFileSize(bytes) {
  if (!bytes) return "Unknown size";
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i];
}

function formatViewCount(count) {
  if (!count) return "0 views";
  if (count >= 1000000) return (count / 1000000).toFixed(1) + "M views";
  if (count >= 1000) return (count / 1000).toFixed(1) + "K views";
  return count + " views";
}
</script>

<template>
  <div
    :class="[
      'min-h-screen transition-all duration-500',
      darkMode ? 'dark' : '',
    ]"
  >
    <!-- Animated Background -->
    <div class="fixed inset-0 overflow-hidden">
      <div
        class="absolute inset-0 bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 dark:from-purple-900 dark:via-pink-800 dark:to-red-900"
      >
        <div class="absolute inset-0 bg-black/20 dark:bg-black/40"></div>
      </div>
      <!-- Animated orbs -->
      <div
        class="absolute top-20 left-20 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"
      ></div>
      <div
        class="absolute top-40 right-20 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"
      ></div>
      <div
        class="absolute bottom-20 left-1/2 w-72 h-72 bg-red-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"
      ></div>
    </div>

    <!-- Main Container -->
    <div
      class="relative min-h-screen flex flex-col items-center justify-center p-4"
    >
      <!-- Dark Mode Toggle -->
      <button
        @click="toggleDarkMode"
        class="absolute top-4 right-4 p-3 rounded-full bg-white/20 backdrop-blur-md border border-white/30 text-white hover:bg-white/30 transition-all duration-300 hover:scale-110"
      >
        <svg
          v-if="!darkMode"
          class="w-6 h-6"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
          ></path>
        </svg>
        <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
            clip-rule="evenodd"
          ></path>
        </svg>
      </button>

      <!-- Main Card -->
      <div class="w-full max-w-2xl">
        <!-- Glass Card -->
        <div
          class="bg-white/10 dark:bg-black/20 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-white/10 p-8 md:p-10 space-y-6 transform hover:scale-[1.02] transition-all duration-300"
        >
          <!-- Header -->
          <div class="text-center space-y-2">
            <div class="flex justify-center mb-4">
              <div
                class="p-4 bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl shadow-lg transform rotate-3 hover:rotate-6 transition-transform duration-300"
              >
                <svg
                  class="w-12 h-12 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 4-8 4z"
                  />
                </svg>
              </div>
            </div>
            <h1 class="text-4xl md:text-5xl font-bold text-white">
              <span
                class="bg-gradient-to-r from-white to-pink-200 bg-clip-text text-transparent"
              >
                YouTube Downloader
              </span>
            </h1>
            <p class="text-white/80 text-lg">
              Download your favorite videos in seconds ⚡
            </p>
          </div>

          <!-- URL Input Section -->
          <div class="space-y-4">
            <div class="relative group">
              <textarea
                v-model="urls"
                rows="3"
                class="w-full px-4 py-3 bg-white/10 dark:bg-black/20 backdrop-blur-md border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent transition-all duration-300 resize-none"
                placeholder="Paste YouTube URL(s) here, one per line..."
              ></textarea>
              <div
                class="absolute inset-0 rounded-2xl bg-gradient-to-r from-pink-500 to-purple-500 opacity-0 group-hover:opacity-20 transition-opacity duration-300 pointer-events-none"
              ></div>
            </div>

            <!-- Controls -->
            <div class="flex flex-col sm:flex-row gap-4">
              <button
                @click="fetchInfo"
                :disabled="loading || !urls.trim()"
                class="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-2xl hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                <svg
                  v-if="loading"
                  class="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>{{ loading ? "Fetching..." : "Fetch Info" }}</span>
              </button>

              <!-- Quality Selector -->
              <div class="relative">
                <select
                  v-model="quality"
                  class="appearance-none px-6 py-3 pr-10 bg-white/10 dark:bg-black/20 backdrop-blur-md border border-white/30 rounded-2xl text-white focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent transition-all duration-300 cursor-pointer hover:bg-white/20"
                >
                  <option
                    v-for="opt in qualityOptions"
                    :key="opt.value"
                    :value="opt.value"
                    class="bg-gray-800"
                  >
                    {{ opt.icon }} {{ opt.label }}
                  </option>
                </select>
                <div
                  class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none"
                >
                  <svg
                    class="w-5 h-5 text-white/70"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 9l-7 7-7-7"
                    ></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Video Info Card -->
          <transition
            enter-active-class="transition-all duration-500 ease-out"
            enter-from-class="opacity-0 transform translate-y-4"
            enter-to-class="opacity-100 transform translate-y-0"
            leave-active-class="transition-all duration-300 ease-in"
            leave-from-class="opacity-100 transform translate-y-0"
            leave-to-class="opacity-0 transform translate-y-4"
          >
            <div
              v-if="videoInfo"
              class="bg-white/10 dark:bg-black/20 backdrop-blur-md rounded-2xl p-6 border border-white/20"
            >
              <div class="flex flex-col md:flex-row gap-6">
                <!-- Thumbnail -->
                <div class="md:w-1/3">
                  <div class="relative group">
                    <img
                      :src="videoInfo.thumbnail"
                      :alt="videoInfo.title"
                      class="w-full rounded-xl shadow-lg group-hover:shadow-2xl transition-all duration-300"
                      v-if="videoInfo.thumbnail"
                    />
                    <div
                      class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    ></div>
                    <div
                      class="absolute bottom-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-sm backdrop-blur-sm"
                    >
                      {{ videoInfo.duration }}
                    </div>
                  </div>
                </div>

                <!-- Info -->
                <div class="md:w-2/3 space-y-3 text-white">
                  <h2 class="text-xl font-bold line-clamp-2">
                    {{ videoInfo.title }}
                  </h2>
                  <div class="flex flex-wrap gap-4 text-sm text-white/80">
                    <span class="flex items-center gap-1">
                      <svg
                        class="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path
                          fill-rule="evenodd"
                          d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      {{ formatViewCount(videoInfo.view_count) }}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg
                        class="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      {{ videoInfo.uploader }}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg
                        class="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      {{ videoInfo.resolution }}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg
                        class="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      {{ formatFileSize(videoInfo.filesize_approx) }}
                    </span>
                  </div>
                  <p class="text-sm text-white/70 line-clamp-3">
                    {{ videoInfo.description }}
                  </p>
                </div>
              </div>

              <!-- Download Button -->
              <div class="mt-6 flex justify-center">
                <button
                  @click="startDownload"
                  :disabled="downloading"
                  class="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-2xl hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center gap-2"
                >
                  <svg
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                    ></path>
                  </svg>
                  <span>{{
                    downloading ? "Downloading..." : "Download Video"
                  }}</span>
                </button>
              </div>
            </div>
          </transition>

          <!-- Progress Bar -->
          <transition
            enter-active-class="transition-all duration-500 ease-out"
            enter-from-class="opacity-0 transform scale-95"
            enter-to-class="opacity-100 transform scale-100"
          >
            <div v-if="downloading || downloadReady" class="space-y-4">
              <div class="relative">
                <div
                  class="bg-white/10 dark:bg-black/20 backdrop-blur-sm rounded-full h-4 overflow-hidden"
                >
                  <div
                    class="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500 ease-out relative overflow-hidden"
                    :style="{ width: progressPercentage + '%' }"
                  >
                    <div
                      class="absolute inset-0 bg-white/30 animate-shimmer"
                    ></div>
                  </div>
                </div>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-white font-semibold text-sm drop-shadow-lg">
                    {{ progressPercentage }}%
                  </span>
                </div>
              </div>

              <div class="text-center text-white/80">
                <span v-if="downloading" class="animate-pulse">
                  {{
                    progress.status === "downloading"
                      ? "Downloading your video..."
                      : progress.status
                  }}
                </span>
              </div>
            </div>
          </transition>

          <!-- Success Animation & Download Button -->
          <transition
            enter-active-class="transition-all duration-500 ease-out"
            enter-from-class="opacity-0 transform scale-50"
            enter-to-class="opacity-100 transform scale-100"
          >
            <div v-if="downloadReady" class="flex flex-col items-center gap-4">
              <div v-if="showSuccessAnimation" class="relative">
                <div
                  class="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full flex items-center justify-center animate-bounce"
                >
                  <svg
                    class="w-10 h-10 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="3"
                      d="M5 13l4 4L19 7"
                    ></path>
                  </svg>
                </div>
                <div
                  class="absolute inset-0 bg-green-400 rounded-full animate-ping"
                ></div>
              </div>

              <a
                :href="downloadUrl"
                class="px-8 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-2xl hover:from-blue-600 hover:to-cyan-600 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center gap-2"
                download
              >
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  ></path>
                </svg>
                <span>Download Your File</span>
              </a>
            </div>
          </transition>

          <!-- Error Message -->
          <transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 transform -translate-y-2"
            enter-to-class="opacity-100 transform translate-y-0"
          >
            <div
              v-if="error"
              class="bg-red-500/20 backdrop-blur-sm border border-red-500/50 rounded-xl p-4"
            >
              <div class="flex items-center gap-3 text-red-100">
                <svg
                  class="w-5 h-5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
                <span>{{ error }}</span>
              </div>
            </div>
          </transition>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-white/60 text-sm">
          <p>Made with ❤️ • © 2024 YouTube Downloader</p>
          <p class="mt-1">Download responsibly and respect copyright</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Custom animations */
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-blob {
  animation: blob 10s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}

/* Dark mode styles */
.dark {
  color-scheme: dark;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 100px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 100px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Line clamp utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>
