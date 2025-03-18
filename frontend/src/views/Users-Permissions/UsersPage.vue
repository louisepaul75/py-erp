<template>
  <div>
    <!-- User List Component -->
    <UserList @user-action="handleUserAction" />
    
    <!-- User Edit/Create Modal -->
    <UserModal 
      :show="showUserModal" 
      :user="selectedUser" 
      @close="closeUserModal" 
      @save="handleUserSave"
    />
    
    <!-- User Groups Assignment Modal -->
    <UserGroupsAssignModal
      :show="showGroupsModal"
      :userId="selectedUserId"
      @close="closeGroupsModal"
      @save="handleGroupsSave"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import UserList from './UserList.vue';
import UserModal from './UserModal.vue';
import UserGroupsAssignModal from './UserGroupsAssignModal.vue';

// Modal visibility states
const showUserModal = ref(false);
const showGroupsModal = ref(false);

// Selected user data
const selectedUser = ref(null);
const selectedUserId = ref(null);

// Handle actions from the user list
const handleUserAction = (action, userId) => {
  if (action === 'create') {
    // Show create user modal
    selectedUser.value = null;
    showUserModal.value = true;
  } else if (action === 'edit' && userId) {
    // Show edit user modal
    loadUser(userId);
  } else if (action === 'groups' && userId) {
    // Show groups assignment modal
    selectedUserId.value = userId;
    showGroupsModal.value = true;
  }
};

// Load user data for editing
const loadUser = async (userId) => {
  try {
    // This would typically be an API call
    // For now, we'll just set the selectedUser directly
    // In a real app, this would be:
    // const response = await usersApi.getUser(userId);
    // selectedUser.value = response.data;
    
    selectedUser.value = { id: userId };
    showUserModal.value = true;
  } catch (error) {
    console.error('Error loading user:', error);
    alert('Fehler beim Laden des Benutzers');
  }
};

// Handle user save from modal
const handleUserSave = (user) => {
  // Reload the user list to show the updated user
  // This is a simple approach - in a real app you might
  // update the user directly in the list for better UX
  const userList = document.querySelector('user-list');
  if (userList && userList.fetchUsers) {
    userList.fetchUsers();
  } else {
    // Force component reload by adding a key
    window.location.reload();
  }
};

// Handle groups save from modal
const handleGroupsSave = (user) => {
  // Reload the user list to show the updated groups
  const userList = document.querySelector('user-list');
  if (userList && userList.fetchUsers) {
    userList.fetchUsers();
  } else {
    // Force component reload by adding a key
    window.location.reload();
  }
};

// Close the user modal
const closeUserModal = () => {
  showUserModal.value = false;
  selectedUser.value = null;
};

// Close the groups modal
const closeGroupsModal = () => {
  showGroupsModal.value = false;
  selectedUserId.value = null;
};
</script> 