<script setup>
import { ref } from "vue";

const urls = ref("");
const quality = ref("best");
const videoInfo = ref(null);
const loading = ref(false);
const error = ref("");
const downloading = ref(false);
const progress = ref({ percent: "0%", status: "" });
const downloadReady = ref(false);
const downloadUrl = ref("");
let downloadId = "";

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
    }
    if (data.status === "not_found" || data.status === "error") {
      error.value = "Download failed or not found.";
      downloading.value = false;
      break;
    }
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4"
  >
    <div class="w-full max-w-xl bg-white rounded-xl shadow-lg p-8 space-y-6">
      <h1 class="text-3xl font-bold text-center text-gray-800 mb-2">
        YouTube Video Downloader
      </h1>
      <p class="text-center text-gray-500 mb-4">
        Paste one or more YouTube links below to fetch info and download videos.
      </p>
      <!-- URL Input -->
      <textarea
        v-model="urls"
        rows="3"
        class="w-full border rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
        placeholder="Paste YouTube URL(s) here, one per line..."
      ></textarea>
      <div class="flex justify-between items-center gap-2">
        <button
          @click="fetchInfo"
          :disabled="loading || !urls.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition"
        >
          Fetch Info
        </button>
        <select v-model="quality" class="border rounded p-2">
          <option value="best">Best</option>
          <option value="high">High (1080p)</option>
          <option value="medium">Medium (720p)</option>
          <option value="low">Low (480p)</option>
        </select>
      </div>
      <!-- Video Info -->
      <div
        v-if="videoInfo"
        class="flex flex-col items-center border-t pt-4 mt-2"
      >
        <img
          :src="videoInfo.thumbnail"
          alt="Thumbnail"
          class="w-48 rounded shadow mb-2"
          v-if="videoInfo.thumbnail"
        />
        <h2 class="text-xl font-semibold text-gray-700">
          {{ videoInfo.title }}
        </h2>
        <p class="text-gray-500">
          Duration: {{ videoInfo.duration }} | By: {{ videoInfo.uploader }}
        </p>
        <p class="text-gray-400 text-sm mt-1">{{ videoInfo.description }}</p>
      </div>
      <!-- Download Section -->
      <div v-if="videoInfo" class="flex flex-col items-center gap-2 mt-4">
        <button
          @click="startDownload"
          :disabled="downloading"
          class="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition"
        >
          Download
        </button>
        <div v-if="downloading" class="w-full flex flex-col items-center mt-2">
          <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
            <div
              class="bg-blue-500 h-3 rounded-full transition-all"
              :style="{ width: progress.percent }"
            ></div>
          </div>
          <span class="text-sm text-gray-600">{{
            progress.status === "downloading"
              ? `Downloading... (${progress.percent})`
              : progress.status
          }}</span>
        </div>
        <a
          v-if="downloadReady"
          :href="downloadUrl"
          class="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
          download
          >Download File</a
        >
      </div>
      <!-- Error Message -->
      <div v-if="error" class="text-red-500 text-center mt-2">{{ error }}</div>
    </div>
    <footer class="mt-8 text-gray-400 text-xs text-center">
      &copy; 2024 Simple YouTube Downloader
    </footer>
  </div>
</template>

<style>
body {
  background: #f9fafb;
}
</style>
