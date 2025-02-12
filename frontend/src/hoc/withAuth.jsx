// src/hoc/withAuth.js
import { useAuth } from '@/context/AuthProvider';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const withAuth = (WrappedComponent) => {
  const AuthWrapper = (props) => {
    const { user, loadingUser } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loadingUser && (!user || !user.token)) {
        console.log('User not authenticated. Redirecting to login...');
        router.push('/login');
      }
    }, [user, loadingUser, router]);

    if (loadingUser) {
      return <div>Loading...</div>; // Optionally, show a loading state
    }

    if (!user || !user.token) {
      return null; // Optionally, return null if the user is not authenticated
    }

    // Render the wrapped component with all its props
    return <WrappedComponent {...props} />;
  };

  return AuthWrapper;
};

export default withAuth;
