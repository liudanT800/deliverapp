import http from './http'

export function loginRequest(payload: { email: string; password: string }) {
  // bcrypt has a 72 byte limit, truncate password if necessary
  const processedPayload = {
    ...payload,
    password: new TextEncoder().encode(payload.password).length > 72 
      ? payload.password.substring(0, 72) 
      : payload.password
  };
  return http
    .post('/auth/login', processedPayload)
    .then((res) => res.data.data)
}

export function registerRequest(payload: {
  email: string
  password: string
  fullName: string
  campus: string
  phone: string
}) {
  // bcrypt has a 72 byte limit, truncate password if necessary
  const processedPayload = {
    ...payload,
    password: new TextEncoder().encode(payload.password).length > 72 
      ? payload.password.substring(0, 72) 
      : payload.password
  };
  return http.post('/auth/register', processedPayload).then((res) => res.data.data)
}

export function fetchProfile() {
  return http.get('/users/me').then((res) => res.data.data)
}

export function updateProfile(payload: {
  fullName?: string
  phone?: string
  campus?: string
  avatarUrl?: string
}) {
  return http.put('/users/me', payload).then((res) => res.data.data)
}

export function fetchCreditInfo() {
  return http.get('/users/me/credit').then((res) => res.data.data)
}