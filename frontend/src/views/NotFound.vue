<template>
  <div class="not-found-container">
    <v-card class="mx-auto" max-width="600">
      <v-card-text class="text-center">
        <h1 class="text-h2 text-error mb-4">{{ $t('errors.notFound') }}</h1>
        <h2 class="text-h4 mb-4">{{ $t('errors.pageNotFound') }}</h2>
        <p class="text-body-1 mb-6">{{ $t('errors.pageNotFoundMessage') }}</p>
        <v-btn color="primary" to="/" prepend-icon="mdi-home">
          {{ $t('common.goToHome') }}
        </v-btn>
      </v-card-text>
    </v-card>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}
</style>
