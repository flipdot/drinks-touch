<template>
  <div>
    <h1 class="text-2xl font-bold">drinks-touch</h1>
    <hr class="my-4 border-t border-gray-300" />
    <!-- {% include "recharge.html" %} -->
    <div class="w-full md:w-1/2">
      <p>Du kannst per SEPA-Überweisung aufladen:<br /></p>
      <ul class="list-inside list-disc">
        <li><b>Kontoinhaber:</b> flipdot e.V.</li>
        <li><b>IBAN:</b> DE07 5205 0353 0001 1477 13</li>
        <li>
          <b>Verwendungszweck:</b>
          <code>
            drinks
            <span id="uid">&lacute;uid&racute;</span>
            <abbr title="Der Hinweistext ist frei wählbar"> hinweistext </abbr>
          </code>
        </li>
      </ul>
      <div class="flex items-center justify-center">
        <img class="hidden w-1/2" id="qrcode" />
        <p class="hidden" id="qrcode_hint">
          Bitte wähle einen Benutzer und gib einen Betrag ein, damit der
          SEPA-QR-Code angezeigt werden kann.
        </p>
      </div>
    </div>
    <!-- {# include "stats.html" #} -->
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  alias: '/recharge',
})

useHeadSafe({ title: 'Start' })
</script>
