# 实时聊天模块前端对接文档

本文档描述了如何与后端实时聊天模块进行对接，包括 REST API 和 WebSocket 的使用。

## 1. 基础信息

*   **REST API 基础路径**: `http://localhost:8000/api/chat`
*   **WebSocket 基础路径**: `ws://localhost:8000/api/chat/ws/{task_id}`
*   **通信协议**: 
    *   消息持久化：HTTP (REST)
    *   实时推送：WebSocket

---

## 2. 接口详述

### 2.1 获取聊天历史记录
在进入聊天窗口时调用，用于渲染初始消息列表。

*   **接口**: `GET /history/{task_id}`
*   **鉴权**: 需要在 Header 中携带 `Authorization: Bearer {token}`
*   **响应示例**:
    ```json
    {
      "data": [
        {
          "id": 1,
          "taskId": 101,
          "senderId": 1,
          "receiverId": 2,
          "content": "你好，我已经出发了",
          "isRead": false,
          "createdAt": "2023-10-27T10:00:00"
        }
      ]
    }
    ```

### 2.2 发送消息
*   **接口**: `POST /send`
*   **请求体**:
    ```json
    {
      "taskId": 101,
      "receiverId": 2,
      "content": "我到楼下了"
    }
    ```
*   **说明**: 发送成功后，后端会自动通过 WebSocket 向该任务房间内的所有成员广播。

### 2.3 获取会话列表
用于显示“我的消息”列表页面。
*   **接口**: `GET /sessions`
*   **响应**: 返回包含最后一条消息、未读数和对方信息的列表。

---

## 3. WebSocket 实时推送

### 3.1 建立连接
*   **连接地址**: `ws://localhost:8000/api/chat/ws/{task_id}?token={your_jwt_token}`
*   **说明**: 由于 WebSocket Header 支持有限，建议通过 Query 参数传递 Token 进行身份验证。

### 3.2 接收消息
当房间内有人发送消息时，WebSocket 会收到如下 JSON 格式的数据：

```json
{
  "type": "new_message",
  "data": {
    "id": 2,
    "taskId": 101,
    "senderId": 2,
    "receiverId": 1,
    "content": "好的，辛苦了！",
    "createdAt": "2023-10-27T10:05:00"
  }
}
```

---

## 4. 前端实现参考 (Vue 3)

```javascript
import { ref, onMounted, onUnmounted } from 'vue';

export function useChat(taskId, token) {
  const messages = ref([]);
  let socket = null;

  // 1. 加载历史记录
  const loadHistory = async () => {
    const res = await api.get(`/chat/history/${taskId}`);
    messages.value = res.data;
  };

  // 2. 初始化 WebSocket
  const initWebSocket = () => {
    socket = new WebSocket(`ws://localhost:8000/api/chat/ws/${taskId}?token=${token}`);

    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.type === 'new_message') {
        messages.value.push(response.data);
        // 可选：如果不在页面底部，显示新消息提醒
      }
    };

    socket.onclose = () => {
      console.log('Chat connection closed');
    };
  };

  onMounted(() => {
    loadHistory();
    initWebSocket();
  });

  onUnmounted(() => {
    if (socket) socket.close();
  });

  return { messages };
}
```

## 5. 注意事项
1. **心跳检测**: 建议前端实现心跳机制（Ping/Pong），防止 WebSocket 连接因长时间无数据传输被网关断开。
2. **自动重连**: 当 WebSocket 异常断开时，前端应尝试自动重连。
3. **消息去重**: 虽然后端有 ID，但前端在收到 WebSocket 广播时，应根据 `id` 检查是否已存在于列表中（防止 API 回显和 WS 广播重复）。
