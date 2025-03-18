import { useLogout } from '../../lib/auth/authHooks';

export const LogoutButton = () => {
  const logout = useLogout();
  
  return (
    <button 
      onClick={() => logout.mutate()}
      disabled={logout.isPending}
      className="logout-button px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600 disabled:bg-red-300"
    >
      {logout.isPending ? 'Abmeldung läuft...' : 'Abmelden'}
    </button>
  );
}; 