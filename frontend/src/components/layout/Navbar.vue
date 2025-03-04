<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <img src="@/assets/wsz_logo.png" alt="pyERP Logo" height="30" class="me-2">
        pyERP
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarContent"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Dashboard</router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/products">Products</router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/sales">Sales</router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/inventory">Inventory</router-link>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link" to="/production">Production</router-link>
          </li>
        </ul>
        
        <!-- Authentication Links -->
        <ul class="navbar-nav">
          <template v-if="authStore.isAuthenticated">
            <li class="nav-item dropdown">
              <a 
                class="nav-link dropdown-toggle" 
                href="#" 
                role="button" 
                data-bs-toggle="dropdown"
              >
                <i class="fas fa-user me-1"></i>
                {{ authStore.fullName || authStore.user?.username }}
              </a>
              
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="fas fa-id-card me-2"></i> Profile
                  </router-link>
                </li>
                
                <li v-if="authStore.isAdmin">
                  <a class="dropdown-item" href="/admin/" target="_blank">
                    <i class="fas fa-cog me-2"></i> Admin
                  </a>
                </li>
                
                <li><hr class="dropdown-divider"></li>
                
                <li>
                  <router-link class="dropdown-item" to="/logout">
                    <i class="fas fa-sign-out-alt me-2"></i> Logout
                  </router-link>
                </li>
              </ul>
            </li>
          </template>
          
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">
                <i class="fas fa-sign-in-alt me-1"></i> Login
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../store/auth';

const authStore = useAuthStore();
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-link {
  padding: 0.5rem 1rem;
}

.dropdown-item {
  padding: 0.5rem 1rem;
}
</style> 