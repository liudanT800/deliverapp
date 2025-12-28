<template>
  <div class="page">
    <header class="card">
      <div>
        <h2>发布顺路任务</h2>
        <p>30 秒填写关键信息，系统将推送给最顺路的同学</p>
      </div>
      <router-link to="/">
        <n-button tertiary>返回大厅</n-button>
      </router-link>
    </header>

    <section class="card">
      <n-form
        ref="formRef"
        :model="form"
        label-placement="top"
        size="large"
      >
        <div class="grid">
          <n-form-item label="任务标题" path="title">
            <n-input 
              v-model:value="form.title" 
              placeholder="例：带英语教材到一教" 
              
            />
            <div class="input-hint">请输入任务标题</div>
          </n-form-item>
          <n-form-item label="物品描述" path="description" class="full-width">
            <n-input
              type="textarea"
              v-model:value="form.description"
              placeholder="物品数量、注意事项..."
              
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
            <div class="input-hint">请输入物品描述</div>
          </n-form-item>
          <!-- 改进地点选择，增加地图按钮 -->
          <n-form-item label="取件地点" path="pickupLocationName" class="full-width">
            <div class="location-input">
              <n-input 
                v-model:value="form.pickupLocationName" 
                placeholder="宿舍 6 栋" 
                
              />
              <n-button @click="openMapSelector('pickup')" size="medium">地图选址</n-button>
            </div>
            <div class="input-hint">请输入取件地点</div>
          </n-form-item>
          <n-form-item label="送达地点" path="dropoffLocationName" class="full-width">
            <div class="location-input">
              <n-input 
                v-model:value="form.dropoffLocationName" 
                placeholder="图书馆东门" 
                
              />
              <n-button @click="openMapSelector('dropoff')" size="medium">地图选址</n-button>
            </div>
            <div class="input-hint">请输入送达地点</div>
          </n-form-item>
          <n-form-item label="酬金（元）" path="rewardAmount">
            <n-input-number v-model:value="form.rewardAmount" :min="1" :max="99" />
          </n-form-item>
          <n-form-item label="预计完成时间" path="expiresAt">
            <n-date-picker
              v-model:value="form.expiresAt"
              type="datetime"
              placeholder="选择截止时间"
              style="width: 100%;"
            />
          </n-form-item>
          <n-form-item label="抢单截止时间" path="grabExpiresAt">
            <n-date-picker
              v-model:value="form.grabExpiresAt"
              type="datetime"
              placeholder="选择抢单截止时间"
              style="width: 100%;"
            />
          </n-form-item>
        </div>
        
        <!-- 新增任务分类 -->
        <n-form-item label="任务分类" path="category">
          <n-select
            v-model:value="form.category"
            :options="categoryOptions"
            placeholder="选择任务类型"
          />
        </n-form-item>
        
        <!-- 新增紧急程度 -->
        <n-form-item label="紧急程度" path="urgency">
          <n-radio-group v-model:value="form.urgency" name="urgency">
            <n-space>
              <n-radio value="low">一般</n-radio>
              <n-radio value="medium">较急</n-radio>
              <n-radio value="high">紧急</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>
        
        <n-space justify="space-between" style="width: 100%;">
          <n-button 
            v-if="form.pickupLat && form.pickupLng && form.dropoffLat && form.dropoffLng"
            @click="previewMapRoute"
            quaternary 
            type="primary" 
            size="small"
          >
            <template #icon>
              <n-icon><LocationIcon /></n-icon>
            </template>
            预览路线
          </n-button>
          <n-button 
            type="primary" 
            :loading="submitting" 
            @click="submit"
            :disabled="submitting"
          >
            {{ submitting ? '发布中...' : '发布任务' }}
          </n-button>
        </n-space>
      </n-form>
    </section>
    
    <!-- 地图选址模态框 -->
    <n-modal
      v-model:show="showMapModal"
      preset="card"
      style="width: 900px; height: 700px;"
      :title="`选择${mapType === 'pickup' ? '取件' : '送达'}地点`"
    >
      <MapSelector
        :api-key="amapApiKey"
        :default-location="getDefaultLocation()"
        @confirm="handleLocationConfirm"
        @cancel="showMapModal = false"
      />
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import type { FormRules, FormInst } from 'naive-ui'
import { useTaskStore } from '../stores/tasks'
import { useRouter } from 'vue-router'
import { NSelect, NRadioGroup, NRadio, NModal, NIcon } from 'naive-ui'
import { useMessage } from 'naive-ui'
import MapSelector from '../components/MapSelector.vue'
import type { LocationData } from '../utils/map'
import { LocationOutline as LocationIcon } from '@vicons/ionicons5'

const tasks = useTaskStore()
const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)

// 地图相关状态
const showMapModal = ref(false)
const mapType = ref<'pickup' | 'dropoff'>('pickup')
const amapApiKey = import.meta.env.VITE_AMAP_API_KEY || 'your-amap-api-key'

// 输入提示状态
const titleHint = ref('请简洁描述任务内容')
const descriptionHint = ref('详细描述物品信息和注意事项')
const pickupHint = ref('请输入取件地点')
const dropoffHint = ref('请输入送达地点')

const form = reactive<{
  title: string
  description: string
  pickupLocationName: string
  pickupLat?: number
  pickupLng?: number
  dropoffLocationName: string
  dropoffLat?: number
  dropoffLng?: number
  rewardAmount: number
  expiresAt: number
  grabExpiresAt: number
  category: string
  urgency: string
}>({
  title: '',
  description: '',
  pickupLocationName: '',
  dropoffLocationName: '',
  rewardAmount: 5,
  expiresAt: Date.now() + 60 * 60 * 1000,
  grabExpiresAt: Date.now() + 60 * 60 * 1000, // 默认1小时后截止抢单
  category: '',
  urgency: 'medium'
})













// 任务分类选项
const categoryOptions = [
  { label: '快递代取', value: 'delivery' },
  { label: '餐饮代买', value: 'food' },
  { label: '文件传递', value: 'document' },
  { label: '物品代购', value: 'purchase' },
  { label: '其他', value: 'other' }
]

function openMapSelector(type: 'pickup' | 'dropoff') {
  mapType.value = type
  showMapModal.value = true
}

function getDefaultLocation(): LocationData | undefined {
  if (mapType.value === 'pickup') {
    return form.pickupLat && form.pickupLng ? {
      name: form.pickupLocationName,
      address: form.pickupLocationName,
      lat: form.pickupLat,
      lng: form.pickupLng
    } : undefined
  } else {
    return form.dropoffLat && form.dropoffLng ? {
      name: form.dropoffLocationName,
      address: form.dropoffLocationName,
      lat: form.dropoffLat,
      lng: form.dropoffLng
    } : undefined
  }
}

function handleLocationConfirm(location: LocationData) {
  // 确保 location.name 和 location.address 是字符串类型，防止对象被传递给表单
  const locationName = (location.name && typeof location.name === 'string') ? location.name : '已选择位置';
  const locationAddress = (location.address && typeof location.address === 'string') ? location.address : `${location.lng?.toFixed(6) || 0}, ${location.lat?.toFixed(6) || 0}`;
  
  if (mapType.value === 'pickup') {
    form.pickupLocationName = locationName
    form.pickupLat = location.lat
    form.pickupLng = location.lng
    pickupHint.value = `取件地点：${locationName} (${locationAddress})`
    form.pickupLocationName = locationName
  } else {
    form.dropoffLocationName = locationName
    form.dropoffLat = location.lat
    form.dropoffLng = location.lng
    dropoffHint.value = `送达地点：${locationName} (${locationAddress})`
    form.dropoffLocationName = locationName
  }
  showMapModal.value = false
  message.success('地点选择成功')
}

function previewMapRoute() {
  // 预览地图路线，从取件点到送达点
  if (form.pickupLng && form.pickupLat && form.dropoffLng && form.dropoffLat) {
    const url = `https://uri.amap.com/route?from=${form.pickupLng},${form.pickupLat},${form.pickupLocationName}&to=${form.dropoffLng},${form.dropoffLat},${form.dropoffLocationName}&fromtype=wp&tocounty=1`;
    window.open(url, '_blank');
  }
}

async function submit() {
  if (!form.title || !form.description || !form.pickupLocationName || 
      !form.dropoffLocationName || !form.category || form.rewardAmount < 1) {
    message.warning('请填写完整信息')
    return
  }
  
  submitting.value = true
  try {
    // 构造正确的payload对象
    const payload = {
      title: form.title,
      description: form.description,
      pickupLocationName: form.pickupLocationName,
      pickupLat: form.pickupLat,
      pickupLng: form.pickupLng,
      dropoffLocationName: form.dropoffLocationName,
      dropoffLat: form.dropoffLat,
      dropoffLng: form.dropoffLng,
      rewardAmount: form.rewardAmount,
      expiresAt: new Date(form.expiresAt).toISOString(),
      grabExpiresAt: new Date(form.grabExpiresAt).toISOString(),
      category: form.category,
      urgency: form.urgency
    }
    const task = await tasks.createTask(payload)
    message.success('任务发布成功')
    router.push(`/tasks/${task.id}`)
  } catch (error: any) {
    console.error('发布任务失败:', error)
    message.error(error.message || '任务发布失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
}

.card {
  padding: 2rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* 全宽表单项样式 */
.full-width {
  grid-column: 1 / -1;
}

/* 响应式网格布局 */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  .location-input {
    flex-direction: column;
    align-items: stretch;
  }
  
  .location-input .n-button {
    align-self: stretch;
    margin-top: 0.5rem;
  }
}

/* 新增样式 */
.location-input {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.location-input .n-input {
  flex: 1;
  min-width: 0; /* 允许flex项目收缩到其内容的大小以下 */
}

.map-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.map-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: var(--radius-small);
}

.map-controls {
  display: flex;
  gap: 0.5rem;
}

.map-controls .n-input {
  flex: 1;
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
