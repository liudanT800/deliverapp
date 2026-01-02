<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-loading-bar-provider>
      <n-notification-provider>
        <n-message-provider>
          <div class="app-shell">
            <header class="app-header card">
              <div class="brand">
                <img src="/vite.svg" alt="logo" />
                <h1>顺路带 · 校园互助</h1>
              </div>
              <nav>
                <router-link to="/">任务大厅</router-link>
                <router-link to="/tasks/create">发布任务</router-link>
                <router-link v-if="auth.user?.role === 'admin'" to="/management/tasks">任务管理</router-link>
                <router-link v-if="auth.user?.role === 'admin'" to="/management/users">用户管理</router-link>
                <router-link v-if="auth.user?.role === 'admin'" to="/management/history">历史记录</router-link>
                <router-link to="/chat-sessions">沟通</router-link>
                <router-link to="/wallet">钱包</router-link>
                <router-link to="/appeals">申诉</router-link>
                <router-link to="/profile">我的</router-link>
              </nav>
            </header>
            <main>
              <router-view />
            </main>
            <footer class="app-footer">
              <p>© 2025 顺路带 · 校园互助平台</p>
            </footer>
          </div>
        </n-message-provider>
      </n-notification-provider>
    </n-loading-bar-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import {
  NConfigProvider,
  NLoadingBarProvider,
  NNotificationProvider,
  NMessageProvider,
  zhCN,
  dateZhCN,
} from 'naive-ui'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 0;
  box-shadow: var(--shadow-light);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand h1 {
  font-size: 1.2rem;
  margin: 0;
  color: var(--text-primary);
}

nav {
  display: flex;
  gap: 1rem;
  font-weight: 500;
}

nav a {
  color: var(--primary-color);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-small);
  transition: background-color 0.2s;
}

nav a:hover {
  background-color: var(--primary-light);
}

nav a.router-link-exact-active {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

main {
  flex: 1;
  padding: 2rem;
}

.app-footer {
  text-align: center;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.9rem;
}
</style>