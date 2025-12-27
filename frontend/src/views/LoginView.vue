<template>
  <div class="auth-page">
    <section class="card">
      <h2>登录顺路带</h2>
      <p class="subtitle">使用校园邮箱进入互助平台</p>
      <n-form :model="form" :rules="rules" ref="formRef">
        <n-form-item path="email" label="邮箱">
          <n-input 
            v-model:value="form.email" 
            placeholder="student@campus.edu" 
            @update:value="handleEmailInput"
          />
          <div v-if="emailError" class="input-hint error">{{ emailError }}</div>
          <div v-else class="input-hint">请输入有效的校园邮箱地址</div>
        </n-form-item>
        <n-form-item path="password" label="密码">
          <n-input 
            v-model:value="form.password" 
            type="password" 
            show-password-on="click" 
            @update:value="handlePasswordInput"
          />
          <div v-if="passwordError" class="input-hint error">{{ passwordError }}</div>
          <div v-else class="input-hint">密码至少6位字符</div>
        </n-form-item>
        <div class="form-options">
          <n-checkbox v-model:checked="rememberMe">记住我</n-checkbox>
          <router-link to="/forgot-password" class="forgot-password">忘记密码？</router-link>
        </div>
        <n-button
          type="primary"
          block
          :loading="auth.loading"
          @click="handleLogin"
          :disabled="isFormInvalid"
        >
          {{ auth.loading ? '登录中...' : '登录' }}
        </n-button>
      </n-form>
      <div class="divider">
        <span>其他登录方式</span>
      </div>
      <div class="social-login">
        <n-button secondary circle>
          微信
        </n-button>
        <n-button secondary circle>
          QQ
        </n-button>
        <n-button secondary circle>
          支付宝
        </n-button>
      </div>
      <p class="hint">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </p>
    </section>
    <aside>
      <h3>校园即时互助</h3>
      <ul>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/>
            </svg>
          </n-icon>
          30秒发布顺路任务
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
            </svg>
          </n-icon>
          实名与信用保障安全
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>
            </svg>
          </n-icon>
          担保支付，任务完成自动结算
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
            </svg>
          </n-icon>
          精准定位，快速匹配顺路同学
        </li>
      </ul>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { FormInst, FormRules } from 'naive-ui'
import { NIcon } from 'naive-ui'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const formRef = ref<FormInst | null>(null)
const rememberMe = ref(false)
const emailError = ref('')
const passwordError = ref('')

const form = reactive({
  email: '',
  password: '',
})

// 实时验证表单
const isFormInvalid = computed(() => {
  return !form.email || !form.password || !!emailError.value || !!passwordError.value || form.password.length < 6
})

// 处理邮箱输入
function handleEmailInput(value: string) {
  form.email = value
  // 清除之前的错误
  emailError.value = ''
  
  // 验证邮箱格式
  if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    emailError.value = '请输入有效的邮箱地址'
  }
}

// 处理密码输入
function handlePasswordInput(value: string) {
  form.password = value
  // 清除之前的错误
  passwordError.value = ''
  
  // 验证密码长度
  if (value && value.length < 6) {
    passwordError.value = '密码至少6位字符'
  }
}

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '邮箱格式不正确' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6位' },
    { max: 72, message: '密码不能超过72个字符' }
  ],
}

async function handleLogin() {
  // 执行最终验证
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      // 如果选择了记住我，保存邮箱到localStorage
      if (rememberMe.value) {
        localStorage.setItem('rememberedEmail', form.email)
      } else {
        localStorage.removeItem('rememberedEmail')
      }
      
      try {
        const result = await auth.login(form)
        const redirect = (route.query.redirect as string) ?? '/'
        router.replace(redirect)
      } catch (error: any) {
        // 显示登录错误
        passwordError.value = error.message || '用户名或密码错误，请重试'
      }
    }
  })
}

// 页面加载时，如果之前选择了记住我，则填充邮箱
onMounted(() => {
  const rememberedEmail = localStorage.getItem('rememberedEmail')
  if (rememberedEmail) {
    form.email = rememberedEmail
    rememberMe.value = true
  }
})
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
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.forgot-password {
  color: var(--primary-color);
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: var(--text-secondary);
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  border-bottom: 1px solid var(--border-color);
}

.divider span {
  padding: 0 1rem;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.hint {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--text-secondary);
}

aside {
  background: linear-gradient(135deg, #5b7bff, #50b2ff);
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
  align-items: center;
  gap: 0.75rem;
}

/* 新增输入提示样式 */
.input-hint {
  font-size: 0.85rem;
  margin-top: 0.25rem;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.input-hint.error {
  color: var(--error-color);
}
</style>