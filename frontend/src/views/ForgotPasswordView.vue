<template>
  <div class="auth-page">
    <section class="card">
      <h2>找回密码</h2>
      <p class="subtitle">请输入您的邮箱地址，我们将发送重置密码链接</p>
      
      <n-form :model="form" :rules="rules" ref="formRef">
        <n-form-item path="email" label="邮箱">
          <n-input v-model:value="form.email" placeholder="student@campus.edu" />
        </n-form-item>
        
        <n-form-item path="captcha" label="验证码">
          <div class="captcha-container">
            <n-input v-model:value="form.captcha" placeholder="请输入验证码" />
            <n-button @click="getCaptcha" :disabled="captchaDisabled" type="primary">
              {{ captchaButtonText }}
            </n-button>
          </div>
        </n-form-item>
        
        <n-button
          type="primary"
          block
          :loading="loading"
          @click="handleSubmit"
        >
          发送重置链接
        </n-button>
      </n-form>
      
      <p class="hint">
        <router-link to="/login">返回登录</router-link>
      </p>
    </section>
    
    <aside>
      <h3>密码重置说明</h3>
      <ul>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
          </n-icon>
          我们将向您的邮箱发送密码重置链接
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/>
            </svg>
          </n-icon>
          验证码5分钟内有效
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
          </n-icon>
          重置链接将在1小时内失效
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
            </svg>
          </n-icon>
          如未收到邮件，请检查垃圾邮件箱
        </li>
      </ul>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInst, FormRules } from 'naive-ui'
import { NIcon } from 'naive-ui'
import { useMessage } from 'naive-ui'

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const loading = ref(false)

// 验证码相关状态
const captchaCountdown = ref(0)
const captchaDisabled = computed(() => captchaCountdown.value > 0)
const captchaButtonText = computed(() => 
  captchaCountdown.value > 0 ? `${captchaCountdown.value}秒后重新获取` : '获取验证码'
)

const form = reactive({
  email: '',
  captcha: ''
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '邮箱格式不正确' },
  ],
  captcha: [
    { required: true, message: '请输入验证码' },
    { len: 6, message: '验证码为6位字符' }
  ]
}

// 获取验证码
function getCaptcha() {
  if (!form.email) {
    message.warning('请先输入邮箱地址')
    return
  }
  
  // 验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    message.warning('请输入正确的邮箱格式')
    return
  }
  
  // 模拟发送验证码
  message.success('验证码已发送至您的邮箱，请注意查收')
  captchaCountdown.value = 60
  
  // 倒计时
  const timer = setInterval(() => {
    captchaCountdown.value--
    if (captchaCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 提交表单
function handleSubmit() {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      loading.value = true
      try {
        // 模拟发送重置密码链接
        await new Promise(resolve => setTimeout(resolve, 1000))
        message.success('密码重置链接已发送至您的邮箱，请注意查收')
        router.push('/login')
      } catch (error) {
        message.error('发送失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(320px, 420px) 1fr;
  gap: 3rem;
  align-items: center;
  min-height: 70vh;
}

.card {
  padding: 2rem;
}

.subtitle {
  margin-top: -0.5rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.captcha-container {
  display: flex;
  gap: 0.5rem;
}

.captcha-container .n-input {
  flex: 1;
}

.hint {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--text-secondary);
}

.hint a {
  color: var(--primary-color);
  text-decoration: none;
}

.hint a:hover {
  text-decoration: underline;
}

aside {
  background: linear-gradient(135deg, #8a6de9, #6b8ddf);
  border-radius: var(--radius-large);
  padding: 2.5rem;
  color: #fff;
}

aside ul {
  margin-top: 1.5rem;
  display: grid;
  gap: 1rem;
  font-size: 1.05rem;
}

aside li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}
</style>