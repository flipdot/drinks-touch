<template>
  <div>
    <label for="user_user">Select User:</label>
    <select id="user_user" v-model="selectedUserId">
      <option v-for="user in users" :key="user.id" :value="user.id">
        {{ user.name }}
      </option>
    </select>

    <label for="amount">Amount:</label>
    <input id="amount" type="number" v-model.number="amount" min="0" />

    <div id="qrcode_hint" v-if="!showQRCode">
      Please select a user and enter a valid amount
    </div>

    <img v-if="showQRCode" id="qrcode" :src="qrCodeUrl" alt="QR Code" />

    <div>
      UID:
      <span id="uid">
        {{ selectedUserId || '&lt;uid&gt;' }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'

// Sample users data (replace with your actual users)
const users = ref([
  { id: '1', name: 'Alice' },
  { id: '2', name: 'Bob' },
  { id: '3', name: 'Charlie' },
])

const selectedUserId = ref('')
const amount = ref(0)

const qrCodeUrl = ref('')
const urlNow = ref('')
const urlNext = ref('')

// Find the selected user object
const selectedUser = computed(
  () =>
    users.value.find((user) => user.id === selectedUserId.value) || {
      name: '',
    },
)

const showQRCode = computed(() => selectedUserId.value && amount.value > 0)

const updateQRCode = () => {
  const uid = selectedUserId.value
  const name = selectedUser.value.name
  const amt = amount.value

  const url = `/tx.png?uid=${encodeURIComponent(uid)}&name=${encodeURIComponent(
    name,
  )}&amount=${encodeURIComponent(amt)}`

  if (url !== urlNow.value) {
    qrCodeUrl.value = '' // reset src first
    urlNext.value = url
    setTimeout(realUpdate, 500)
  }
}

const realUpdate = () => {
  if (urlNow.value === urlNext.value) return
  qrCodeUrl.value = urlNext.value
  urlNow.value = urlNext.value
}

// Debounce QR code updates for better UX
const debouncedUpdateQRCode = useDebounceFn(updateQRCode, 300)

// Watch user and amount changes
watch([selectedUserId, amount], debouncedUpdateQRCode)
</script>

<style>
#qrcode {
  max-width: 200px;
  margin-top: 10px;
}
</style>
