<template>
  <div class="not-found-container">
    <div class="card">
      <div class="card-body text-center">
        <h1 class="display-1 text-danger">404</h1>
        <h2 class="mb-4">Page Not Found</h2>
        <p class="lead mb-4">The page you are looking for does not exist or has been moved.</p>
        <router-link to="/" class="btn btn-primary">
          <i class="fas fa-home me-2"></i> Go to Home
        </router-link>
      </div>
    </div>
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

.card {
  width: 100%;
  max-width: 600px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style> 