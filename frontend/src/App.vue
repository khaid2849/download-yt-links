<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const urls = ref("");
const quality = ref("best");
const loading = ref(false);
const error = ref("");
const downloading = ref(false);
const progress = ref({ percent: "0%", status: "" });
const downloadReady = ref(false);
const downloadUrl = ref("");
const showFeatures = ref(false);
const activeSection = ref('hero');
let downloadId = "";

// Animations on mount
onMounted(() => {
  // Trigger animations
  setTimeout(() => {
    showFeatures.value = true;
  }, 500);
  
  // Parallax effect for floating elements
  window.addEventListener('mousemove', handleMouseMove);
});

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove);
});

// Mouse parallax effect
function handleMouseMove(e) {
  const { clientX, clientY } = e;
  const centerX = window.innerWidth / 2;
  const centerY = window.innerHeight / 2;
  const moveX = (clientX - centerX) / 50;
  const moveY = (clientY - centerY) / 50;
  
  document.querySelectorAll('.floating').forEach((el, i) => {
    const speed = el.dataset.speed || 1;
    el.style.transform = `translate(${moveX * speed}px, ${moveY * speed}px)`;
  });
}

// Computed properties for dynamic styling
const progressPercentage = computed(() => {
  const percent = parseInt(progress.value.percent) || 0;
  return Math.min(percent, 100);
});

const qualityOptions = [
  { value: "best", label: "Best Quality", icon: "🚀" },
  { value: "high", label: "High (1080p)", icon: "⭐" },
  { value: "medium", label: "Medium (720p)", icon: "🌟" },
  { value: "low", label: "Low (480p)", icon: "💫" },
];

async function startDownload() {
  if (!urls.value.trim()) {
    error.value = "Please enter at least one YouTube URL";
    return;
  }
  
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
    error.value = "Network error. Please try again.";
    downloading.value = false;
  }
}

// Update the pollProgress function in your App.vue
async function pollProgress() {
  if (!downloadId) return;
  let done = false;
  while (!done) {
    await new Promise((r) => setTimeout(r, 1500));
    try {
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
        
        // Auto-trigger download after a short delay
        setTimeout(() => {
          triggerDownload();
        }, 1000);
      }
      if (data.status === "not_found" || data.status === "error") {
        error.value = "Download failed. Please try again.";
        downloading.value = false;
        break;
      }
    } catch (e) {
      error.value = "Connection error. Please try again.";
      downloading.value = false;
      break;
    }
  }
}

// Add this new function for auto-download
function triggerDownload() {
  if (downloadUrl.value) {
    // Method 1: Using window.location
    window.location.href = downloadUrl.value;
    
    // Alternative Method 2: Using iframe (use if method 1 doesn't work)
    // const iframe = document.createElement('iframe');
    // iframe.style.display = 'none';
    // iframe.src = downloadUrl.value;
    // document.body.appendChild(iframe);
    // setTimeout(() => {
    //   document.body.removeChild(iframe);
    // }, 5000);
  }
}

// Add this function to show success message
function showSuccessMessage() {
  // You can add a success toast or message here
  console.log('Download started successfully!');
}

// Update the download ready section in template to also include a manual download button
// In case auto-download is blocked by browser
`
<div v-if="downloadReady" class="flex flex-col items-center gap-4">
  <div class="relative">
    <div class="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full flex items-center justify-center animate-bounce">
      <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
      </svg>
    </div>
    <div class="absolute inset-0 bg-green-400 rounded-full animate-ping"></div>
  </div>

  <div class="text-center space-y-2">
    <p class="text-white text-lg font-semibold">Download Complete! 🎉</p>
    <p class="text-gray-300 text-sm">Your download should start automatically</p>
  </div>

  <a
    :href="downloadUrl"
    class="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold rounded-xl hover:from-green-700 hover:to-emerald-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-green-500/25 flex items-center gap-2"
    download
  >
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
    </svg>
    <span>Download Manually</span>
  </a>
  
  <button
    @click="resetDownloader"
    class="text-purple-400 hover:text-purple-300 text-sm underline transition-colors"
  >
    Download another video
  </button>
</div>
`

// Add reset function
function resetDownloader() {
  urls.value = "";
  downloadReady.value = false;
  downloadUrl.value = "";
  progress.value = { percent: "0%", status: "" };
  error.value = "";
  downloadId = "";
}

function scrollToSection(section) {
  activeSection.value = section;
  const element = document.getElementById(section);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#0a0a1f] overflow-x-hidden">
    <!-- Space Background -->
    <div class="fixed inset-0 overflow-hidden">
      <!-- Stars -->
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
      
      <!-- Nebula Effect -->
      <div class="absolute inset-0">
        <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-purple-900/20 via-pink-900/20 to-blue-900/20"></div>
        <div class="absolute top-1/4 -left-1/4 w-96 h-96 bg-purple-600/30 rounded-full filter blur-[128px] animate-pulse"></div>
        <div class="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-pink-600/30 rounded-full filter blur-[128px] animate-pulse animation-delay-2000"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/30 rounded-full filter blur-[128px] animate-pulse animation-delay-4000"></div>
      </div>

      <!-- Floating Elements -->
      <div class="floating absolute top-20 left-10 w-16 h-16 opacity-70" data-speed="2">
        <div class="w-full h-full bg-orange-500 rounded-full"></div>
      </div>
      <div class="floating absolute bottom-20 right-20 w-20 h-20 opacity-60" data-speed="1.5">
        <div class="w-full h-full bg-purple-500 rounded-full relative">
          <div class="absolute inset-x-0 top-1/2 h-1 bg-red-400 -rotate-12"></div>
        </div>
      </div>
      <div class="floating absolute top-1/3 right-1/4 w-8 h-8 opacity-80" data-speed="3">
        <div class="w-full h-full bg-yellow-400 clip-star"></div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="relative z-20 px-6 py-4">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <div class="flex items-center gap-2">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
            <span class="text-white font-bold text-xl">A</span>
          </div>
          <span class="text-white font-bold text-xl">AJUS GALXY</span>
        </div>
        <div class="hidden md:flex items-center gap-6">
          <a href="#" class="text-white/70 hover:text-white transition-colors">About</a>
          <a href="#" class="text-white/70 hover:text-white transition-colors">Works</a>
          <a href="#" class="text-white/70 hover:text-white transition-colors">Services</a>
          <a href="#" class="text-white/70 hover:text-white transition-colors">News</a>
          <a href="#" class="text-white/70 hover:text-white transition-colors">Contact</a>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="hero" class="relative z-10 min-h-screen flex items-center justify-center px-6 py-20">
      <div class="max-w-7xl mx-auto w-full">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <!-- Left Content -->
          <div class="space-y-8">
            <div class="space-y-4">
              <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
                Get The Best<br/>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                  YouTube Downloader
                </span>
              </h1>
              <p class="text-xl text-gray-300">
                Download any YouTube video in seconds with our powerful space-themed downloader. Fast, reliable, and beautiful.
              </p>
            </div>

            <!-- Input Section -->
            <div class="space-y-4">
              <div class="relative">
                <textarea
                  v-model="urls"
                  rows="4"
                  class="w-full px-6 py-4 bg-white/5 backdrop-blur-md border border-purple-500/30 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                  placeholder="Paste YouTube URL(s) here, one per line...&#10;Example: https://youtube.com/watch?v=..."
                ></textarea>
                <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 -z-10 blur-xl"></div>
              </div>

              <div class="flex flex-col sm:flex-row gap-4">
                <!-- Quality Selector -->
                <select
                  v-model="quality"
                  class="px-6 py-3 bg-white/5 backdrop-blur-md border border-purple-500/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all duration-300"
                >
                  <option v-for="opt in qualityOptions" :key="opt.value" :value="opt.value" class="bg-gray-900">
                    {{ opt.icon }} {{ opt.label }}
                  </option>
                </select>

                <!-- Download Button -->
                <button
                  @click="startDownload"
                  :disabled="downloading || !urls.trim()"
                  class="flex-1 px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-purple-500/25 flex items-center justify-center gap-2"
                >
                  <svg v-if="!downloading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                  </svg>
                  <svg v-else class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{{ downloading ? "Downloading..." : "Download Videos" }}</span>
                </button>
              </div>
            </div>

            <!-- Progress Bar -->
            <transition
              enter-active-class="transition-all duration-500 ease-out"
              enter-from-class="opacity-0 transform scale-95"
              enter-to-class="opacity-100 transform scale-100"
            >
              <div v-if="downloading || downloadReady" class="space-y-4">
                <div class="relative">
                  <div class="bg-white/10 backdrop-blur-sm rounded-full h-6 overflow-hidden">
                    <div
                      class="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 transition-all duration-500 ease-out relative overflow-hidden"
                      :style="{ width: progressPercentage + '%' }"
                    >
                      <div class="absolute inset-0 bg-white/30 animate-shimmer"></div>
                    </div>
                  </div>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-white font-semibold text-sm drop-shadow-lg">
                      {{ progressPercentage }}%
                    </span>
                  </div>
                </div>

                <div class="text-center text-gray-300">
                  <span v-if="downloading" class="animate-pulse">
                    Downloading from space... 🚀
                  </span>
                </div>
              </div>
            </transition>

            <!-- Download Ready -->
            <transition
              enter-active-class="transition-all duration-500 ease-out"
              enter-from-class="opacity-0 transform scale-50"
              enter-to-class="opacity-100 transform scale-100"
            >
              <div v-if="downloadReady" class="flex flex-col items-center gap-4">
                <div class="relative">
                  <div class="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full flex items-center justify-center animate-bounce">
                    <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  <div class="absolute inset-0 bg-green-400 rounded-full animate-ping"></div>
                </div>

                <a
                  :href="downloadUrl"
                  class="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold rounded-xl hover:from-green-700 hover:to-emerald-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-green-500/25 flex items-center gap-2"
                  download
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
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
                  <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                  </svg>
                  <span>{{ error }}</span>
                </div>
              </div>
            </transition>
          </div>

          <!-- Right Content - Astronaut -->
          <div class="relative hidden lg:block">
            <div class="w-full max-w-md mx-auto animate-float">
              <!-- Simple Astronaut SVG -->
              <svg viewBox="0 0 400 600" class="w-full h-auto">
                <!-- Helmet -->
                <ellipse cx="200" cy="200" rx="80" ry="100" fill="url(#helmet)" />
                <!-- Body -->
                <rect x="140" y="280" width="120" height="150" rx="40" fill="#E5E7EB" />
                <!-- Arms -->
                <rect x="100" y="320" width="60" height="100" rx="30" fill="#E5E7EB" />
                <rect x="240" y="320" width="60" height="100" rx="30" fill="#E5E7EB" />
                <!-- Legs -->
                <rect x="140" y="420" width="50" height="120" rx="25" fill="#E5E7EB" />
                <rect x="210" y="420" width="50" height="120" rx="25" fill="#E5E7EB" />
                <!-- Visor -->
                <circle cx="200" cy="200" r="60" fill="#111827" opacity="0.8" />
                <!-- Reflection -->
                <path d="M170 180 Q200 160 230 180" fill="none" stroke="#F3F4F6" stroke-width="3" />
                
                <defs>
                  <linearGradient id="helmet" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#9333EA;stop-opacity:0.8" />
                    <stop offset="100%" style="stop-color:#EC4899;stop-opacity:0.6" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            
            <!-- Floating laptop -->
            <div class="absolute top-20 -left-10 animate-float animation-delay-2000">
              <svg viewBox="0 0 200 150" class="w-32 opacity-80">
                <rect x="20" y="20" width="160" height="100" rx="10" fill="#4B5563" />
                <rect x="30" y="30" width="140" height="80" rx="5" fill="#1F2937" />
                <rect x="10" y="120" width="180" height="20" rx="5" fill="#6B7280" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="relative z-10 px-6 py-20">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-4xl md:text-5xl font-bold text-white mb-4">
            Choose Your
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400"> Subject</span>
          </h2>
          <p class="text-xl text-gray-300">
            Fast, reliable, and beautiful YouTube video downloads
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="group">
            <div class="bg-white/5 backdrop-blur-md border border-purple-500/30 rounded-2xl p-8 hover:bg-white/10 transition-all duration-300 h-full">
              <div class="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <span class="text-2xl">🎨</span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-4">Graphic Design</h3>
              <p class="text-gray-300">
                Download any YouTube video in the highest quality. Support for multiple formats and resolutions.
              </p>
            </div>
          </div>

          <!-- Feature 2 -->
          <div class="group">
            <div class="bg-white/5 backdrop-blur-md border border-purple-500/30 rounded-2xl p-8 hover:bg-white/10 transition-all duration-300 h-full">
              <div class="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <span class="text-2xl">🎯</span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-4">UI/UX Design</h3>
              <p class="text-gray-300">
                Beautiful and intuitive interface. Download multiple videos at once with our batch processing.
              </p>
            </div>
          </div>

          <!-- Feature 3 -->
          <div class="group">
            <div class="bg-white/5 backdrop-blur-md border border-purple-500/30 rounded-2xl p-8 hover:bg-white/10 transition-all duration-300 h-full">
              <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <span class="text-2xl">💻</span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-4">Web Development</h3>
              <p class="text-gray-300">
                Fast processing with our powerful servers. Get your videos downloaded in seconds.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="relative z-10 px-6 py-20">
      <div class="max-w-4xl mx-auto text-center">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-8">
          How Can You
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400"> Reach To Us?</span>
        </h2>
        <p class="text-xl text-gray-300 mb-8">
          Start downloading your favorite YouTube videos now. It's fast, free, and easy!
        </p>
        <button
          @click="scrollToSection('hero')"
          class="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-purple-500/25 inline-flex items-center gap-2"
        >
          <span>Explore More</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
          </svg>
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="relative z-10 px-6 py-8 border-t border-purple-500/20">
      <div class="max-w-7xl mx-auto text-center">
        <p class="text-gray-400">
          © 2024 AJUS GALXY YouTube Downloader. Made with ❤️ in space.
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Space theme animations */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
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

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-blob {
  animation: blob 10s infinite;
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

/* Stars background */
.stars {
  position: fixed;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(2px 2px at 20px 30px, #eee, transparent),
                    radial-gradient(2px 2px at 40px 70px, #eee, transparent),
                    radial-gradient(1px 1px at 50px 50px, #eee, transparent),
                    radial-gradient(1px 1px at 80px 10px, #eee, transparent),
                    radial-gradient(2px 2px at 130px 80px, #eee, transparent);
  background-repeat: repeat;
  background-size: 200px 200px;
  animation: zoom 10s infinite;
  opacity: 0.3;
}

.stars2 {
  position: fixed;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(1px 1px at 20px 30px, #fff, transparent),
                    radial-gradient(1px 1px at 40px 70px, #fff, transparent),
                    radial-gradient(2px 2px at 50px 50px, #fff, transparent),
                    radial-gradient(2px 2px at 80px 10px, #fff, transparent),
                    radial-gradient(1px 1px at 130px 80px, #fff, transparent);
  background-repeat: repeat;
  background-size: 250px 250px;
  animation: zoom 15s infinite;
  opacity: 0.2;
}

.stars3 {
  position: fixed;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(2px 2px at 20px 30px, #fff, transparent),
                    radial-gradient(2px 2px at 40px 70px, #fff, transparent),
                    radial-gradient(1px 1px at 50px 50px, #fff, transparent);
  background-repeat: repeat;
  background-size: 300px 300px;
  animation: zoom 20s infinite;
  opacity: 0.1;
}

@keyframes zoom {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.2);
  }
}

/* Star shape */
.clip-star {
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #9333ea, #ec4899);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #7c3aed, #db2777);
}
</style>