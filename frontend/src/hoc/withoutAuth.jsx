// src/hoc/withoutAuth.js
import { useAuth } from '@/context/AuthProvider';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { getNextOnboardingStep } from '@/lib/utils'

const withoutAuth = (WrappedComponent) => {
  const NoAuthWrapper = (props) => {
    const { user, loadingUser } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loadingUser && user && user.token) {
        console.log('User is authenticated. Redirecting to home...');
        if (!user.profile?.is_email_verified) {
          router.push('/verify-email?email=' + encodeURIComponent(user.email))
        } else {
          router.push(getNextOnboardingStep(
            user.user_type,
            user.onboarding_steps_completed ? user.onboarding_steps_completed[user.onboarding_steps_completed.length - 1] : null
          ))
        }
      }
    }, [user, loadingUser, router]);

    if (loadingUser) {
      return <div>Loading...</div>; // Optionally, show a loading state
    }
  
    if (user && user.token) {
      return null; // Optionally, return null if the user is authenticated
    }
  
    // Render the wrapped component with all its props
    return <WrappedComponent {...props} />;
  };

  return NoAuthWrapper;
};

export default withoutAuth;
