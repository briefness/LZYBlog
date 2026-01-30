<script setup>
import { onMounted } from 'vue'

const projects = [
  {
    title: 'Coze Agent',
    desc: 'Neural_Net // AI Development',
    link: '/posts/coze/index',
    id: 'P-01',
    status: 'ACTIVE'
  },
  {
    title: 'HarmonyOS',
    desc: 'System_Core // Mobile Arch',
    link: '/posts/harmonyos/index',
    id: 'P-02',
    status: 'STABLE'
  },
  {
    title: 'BaseCut',
    desc: 'Media_Eng // Video Process',
    link: '/posts/BaseCut/index',
    id: 'P-03',
    status: 'BETA'
  }
]
</script>

<template>
  <div class="cyber-container w-full min-h-screen cyber-mode cyber-grid-bg flex flex-col items-center justify-center p-4">
    
    <!-- Hero Section -->
    <div class="relative z-10 text-center mb-16 mt-20">
      <div class="inline-block border border-[color:var(--cyber-cyan)] px-4 py-1 mb-4 text-xs tracking-[0.2em] text-[color:var(--cyber-cyan)] opacity-70">
        SYSTEM_READY
      </div>
      <h1 class="text-6xl md:text-8xl font-black mb-2 glitch" data-text="LZY LAB">
        LZY LAB<span class="animate-pulse">_</span>
      </h1>
      <p class="text-[color:var(--cyber-purple)] tracking-widest text-sm md:text-base font-bold mt-2">
        &lt;CODE / DESIGN / FUTURE&gt;
      </p>
    </div>

    <!-- HUD Grid -->
    <div class="relative z-10 w-full max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-8 py-10 px-4">
      
      <!-- Project Cards -->
      <a v-for="project in projects" :key="project.id" :href="project.link" 
         class="hud-border group relative h-64 p-6 flex flex-col justify-between transition-all duration-300 hover:-translate-y-2 hover:bg-[rgba(0,243,255,0.05)]">
        
        <!-- Header -->
        <div class="flex justify-between items-start">
          <span class="text-xs text-[color:var(--cyber-cyan)] font-mono opacity-60">{{ project.id }}</span>
          <span class="text-[10px] px-2 py-0.5 border border-[color:var(--cyber-purple)] text-[color:var(--cyber-purple)]">
            {{ project.status }}
          </span>
        </div>

        <!-- Content -->
        <div>
          <h2 class="text-2xl font-bold mb-2 group-hover:text-[color:var(--cyber-cyan)] transition-colors">
            {{ project.title }}
          </h2>
          <p class="text-sm opacity-70 font-mono">{{ project.desc }}</p>
        </div>

        <!-- Footer / Scanline -->
        <div class="w-full h-[1px] bg-[color:var(--cyber-cyan)] opacity-20 group-hover:opacity-100 transition-opacity relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1/2 h-full bg-[color:var(--cyber-cyan)] animate-[scan_2s_linear_infinite]"></div>
        </div>
      </a>

    </div>

    <!-- Fake Terminal / Footer -->
    <div class="mt-16 font-mono text-xs opacity-50 text-center max-w-2xl mx-auto">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-[color:var(--cyber-cyan)]">
        <div>> CPU_LOAD: 12%</div>
        <div>> MEM_FREE: 64TB</div>
        <div>> NET_STAT: SECURE</div>
        <div><a href="https://github.com/briefness/LZYBlog" class="hover:text-white underline decoration-dashed">GITHUB_LINK</a></div>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes scan {
  0% { left: -100%; }
  100% { left: 200%; }
}
</style>
