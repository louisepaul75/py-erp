export interface User {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  name: string; // Combined name
  is_active: boolean;
  is_staff: boolean;
  is_superuser?: boolean; // Optional based on context (list vs detail)
  groups: { id: string; name: string }[];
  date_joined: string;
  last_login?: string | null;
  status?: string; // From profile
  department?: string; // From profile
  last_seen?: string | null; // Added: ISO string format or null
}

// You might also want a more detailed type if the API provides more info in certain contexts
export interface UserDetail extends User {
  profile?: {
    department?: string;
    position?: string;
    phone?: string;
    language_preference?: string;
    profile_picture?: string | null;
    status?: string;
    two_factor_enabled?: boolean;
    last_password_change?: string | null;
    last_seen?: string | null; // Added here too for consistency
  };
} 