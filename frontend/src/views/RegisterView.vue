<template>
  <div class="auth-page">
    <section class="card">
      <h2>注册顺路带</h2>
      <n-form :model="form" ref="formRef">
        <n-form-item label="姓名" path="fullName">
          <n-input v-model:value="form.fullName" placeholder="张三" />
        </n-form-item>
        <n-form-item label="校园邮箱" path="email">
          <n-input v-model:value="form.email" placeholder="student@campus.edu" />
        </n-form-item>
        <n-form-item label="手机号" path="phone">
          <n-input v-model:value="form.phone" placeholder="138****" />
        </n-form-item>
        <n-form-item label="所属校区" path="campus">
          <n-input v-model:value="form.campus" placeholder="下沙校区" />
        </n-form-item>
        <n-form-item label="设置密码" path="password">
          <n-input type="password" v-model:value="form.password" show-password-on="click" />
        </n-form-item>
        <n-form-item label="确认密码" path="confirmPassword">
          <n-input type="password" v-model:value="form.confirmPassword" show-password-on="click" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="agreeTerms">
            我已阅读并同意
            <a href="#" @click.prevent="showTerms">用户协议</a> 和
            <a href="#" @click.prevent="showPrivacy">隐私政策</a>
          </n-checkbox>
        </n-form-item>
        <n-button type="primary" block :loading="auth.loading" @click="handleRegister">
          注册并登录
        </n-button>
      </n-form>
      <p class="hint">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </p>
    </section>
    <aside>
      <h3>为什么选择顺路带？</h3>
      <ul>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z" />
            </svg>
          </n-icon>
          校园专属实名认证
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
            </svg>
          </n-icon>
          信用体系保障交易
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" />
            </svg>
          </n-icon>
          实时追踪任务状态
        </li>
        <li>
          <n-icon size="20">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm4.5-12.5l-5 5-2.5-2.5L7.5 12l4-4 6.5 6.5z" />
            </svg>
          </n-icon>
          一键发布，快速匹配
        </li>
      </ul>
    </aside>

    <!-- 用户协议模态框 -->
    <n-modal v-model:show="showTermsModal" preset="card" style="width: 600px;" title="用户协议">
      <div class="modal-content">
        <h3>顺路带用户服务协议</h3>
        <p>欢迎使用顺路带校园互助平台...</p>
        <p>（此处为协议内容）</p>
      </div>
    </n-modal>

    <!-- 隐私政策模态框 -->
    <n-modal v-model:show="showPrivacyModal" preset="card" style="width: 600px;" title="隐私政策">
      <div class="modal-content">
        <h3>顺路带隐私政策</h3>
        <p>我们非常重视您的隐私保护...</p>
        <p>（此处为隐私政策内容）</p>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { FormInst, FormRules } from 'naive-ui'
import { NIcon } from 'naive-ui'
import { useMessage } from 'naive-ui'

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const formRef = ref<FormInst | null>(null)
const agreeTerms = ref(false)
const showTermsModal = ref(false)
const showPrivacyModal = ref(false)

const form = reactive({
  fullName: '',
  email: '',
  phone: '',
  campus: '',
  password: '',
  confirmPassword: ''
})



// 显示用户协议
function showTerms() {
  showTermsModal.value = true
}

// 显示隐私政策
function showPrivacy() {
  showPrivacyModal.value = true
}

async function handleRegister() {
  if (!agreeTerms.value) {
    message.warning('请先阅读并同意用户协议和隐私政策')
    return
  }
  
  if (!form.fullName || !form.email || !form.phone || !form.campus || !form.password || form.password !== form.confirmPassword) {
    message.warning('请填写完整信息并确保密码一致')
    return
  }
  
  try {
    const result = await auth.register(form)
    message.success(result.message || '注册成功')
    router.push('/')
  } catch (error: any) {
    message.error(error.message || '注册失败')
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(320px, 480px) 1fr;
  gap: 3rem;
  align-items: center;
  min-height: 70vh;
}

.card {
  padding: 2rem;
}

.hint {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--text-secondary);
}

.modal-content {
  line-height: 1.6;
}

.modal-content h3 {
  margin-top: 0;
}

aside {
  background: linear-gradient(135deg, #ff9a62, #ff6262);
  border-radius: var(--radius-large);
  padding: 2.5rem;
  color: #fff;
  min-height: 320px;
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