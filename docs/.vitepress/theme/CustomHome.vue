<script setup>
import { VPTeamMembers } from 'vitepress/theme'

const features = [
  {
    title: 'Coze Agent',
    desc: 'AI 智能体开发实战',
    link: '/posts/coze/index',
    color: 'from-purple-500 to-indigo-600',
    icon: '🤖'
  },
  {
    title: 'HarmonyOS',
    desc: '鸿蒙原生应用开发',
    link: '/posts/harmonyos/index',
    color: 'from-blue-500 to-cyan-400',
    icon: '📱'
  },
  {
    title: 'BaseCut',
    desc: 'Web 视频剪辑引擎',
    link: '/posts/BaseCut/index',
    color: 'from-rose-500 to-orange-400',
    icon: '🎬'
  }
]
</script>

<template>
  <div class="home-container bg-slate-50 dark:bg-slate-900 min-h-screen">
    
    <!-- Hero Section -->
    <div class="relative pt-32 pb-20 px-6 max-w-7xl mx-auto text-center">
      <h1 class="text-6xl md:text-8xl font-black tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600 animate-gradient">
        技术探索
      </h1>
      <p class="text-xl md:text-2xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto font-medium">
        Coze AI · HarmonyOS · WebAV
      </p>
      
      <div class="mt-10 flex justify-center gap-4">
        <a href="https://github.com/briefness/LZYBlog" target="_blank" 
           class="px-8 py-3 rounded-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold hover:scale-105 transition-transform duration-300">
          GitHub
        </a>
      </div>
    </div>

    <!-- Bento Grid -->
    <div class="px-6 pb-32 max-w-7xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]">
        
        <!-- Main Large Card for Coze -->
        <a :href="features[0].link" 
           class="group relative col-span-1 md:col-span-2 row-span-1 overflow-hidden rounded-3xl bg-white dark:bg-slate-800 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
          <div class="absolute inset-0 bg-gradient-to-br opacity-10 group-hover:opacity-20 transition-opacity" :class="features[0].color"></div>
          <div class="absolute top-0 right-0 p-10 opacity-10 text-9xl transform group-hover:scale-110 group-hover:rotate-12 transition-transform duration-500">
            {{ features[0].icon }}
          </div>
          <div class="absolute bottom-0 left-0 p-8">
            <h2 class="text-3xl font-bold mb-2 text-slate-800 dark:text-white">{{ features[0].title }}</h2>
            <p class="text-lg text-slate-500 dark:text-slate-400">{{ features[0].desc }}</p>
          </div>
        </a>

        <!-- HarmonyOS Card -->
        <a :href="features[1].link"
           class="group relative overflow-hidden rounded-3xl bg-white dark:bg-slate-800 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
          <div class="absolute inset-0 bg-gradient-to-br opacity-10 group-hover:opacity-20 transition-opacity" :class="features[1].color"></div>
          <div class="absolute -right-4 -top-4 p-8 opacity-10 text-8xl transform group-hover:scale-110 group-hover:-rotate-12 transition-transform duration-500">
            {{ features[1].icon }}
          </div>
          <div class="absolute bottom-0 left-0 p-8">
            <h2 class="text-2xl font-bold mb-2 text-slate-800 dark:text-white">{{ features[1].title }}</h2>
            <p class="text-slate-500 dark:text-slate-400">{{ features[1].desc }}</p>
          </div>
        </a>

        <!-- BaseCut Card -->
        <a :href="features[2].link"
           class="group relative overflow-hidden rounded-3xl bg-white dark:bg-slate-800 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
           <div class="absolute inset-0 bg-gradient-to-br opacity-10 group-hover:opacity-20 transition-opacity" :class="features[2].color"></div>
           <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-8xl opacity-10 transform group-hover:scale-125 transition-transform duration-500">
             {{ features[2].icon }}
           </div>
           <div class="absolute bottom-0 left-0 p-8 w-full text-center">
             <h2 class="text-2xl font-bold mb-2 text-slate-800 dark:text-white">{{ features[2].title }}</h2>
             <p class="text-slate-500 dark:text-slate-400">{{ features[2].desc }}</p>
           </div>
        </a>

      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animate-gradient {
  background-size: 200% auto;
  animation: gradient 3s linear infinite;
}
</style>
