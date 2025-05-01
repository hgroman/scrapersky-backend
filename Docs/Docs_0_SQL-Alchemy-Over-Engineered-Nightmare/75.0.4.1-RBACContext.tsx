import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from './AuthContext';
import { Permission, SidebarFeature, RBACContextType, ServiceTab } from '@/types/rbac';

const RBACContext = createContext<RBACContextType | null>(null);

export const RBACProvider = ({ children }: { children: ReactNode }) => {
  const { session } = useAuth();
  const [userPermissions, setUserPermissions] = useState<Permission[]>([]);
  const [sidebarFeatures, setSidebarFeatures] = useState<SidebarFeature[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch RBAC data (permissions and sidebar features)
  useEffect(() => {
    const fetchRBACData = async () => {
      if (!session?.user) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);

      try {
        // 1. Fetch user permissions (simplified approach)
        const { data: permissionsData, error: permissionsError } = await supabase
          .from('permissions')
          .select(`
            name,
            role_permissions!inner(
              role_id,
              user_roles!inner(
                user_id
              )
            )
          `)
          .eq('role_permissions.user_roles.user_id', session.user.id);

        if (permissionsError) {
          console.error('Error fetching permissions:', permissionsError);
          throw permissionsError;
        }

        // Extract permissions from the result
        const permissions = permissionsData?.map(p => p.name as Permission) || [];

        // 2. Fetch sidebar features (directly, without feature flag dependency)
        const { data: sidebarData, error: sidebarError } = await supabase
          .from('sidebar_features')
          .select('*')
          .order('display_order', { ascending: true });

        if (sidebarError) {
          console.error('Error fetching sidebar features:', sidebarError);
          throw sidebarError;
        }

        // Set state with fetched data
        setUserPermissions(permissions);
        setSidebarFeatures(sidebarData || []);
      } catch (error) {
        console.error('Error in RBAC data fetching:', error);
        // In case of error, give minimal permissions for graceful degradation
        setUserPermissions([]);
        setSidebarFeatures([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRBACData();
  }, [session]);

  // Helper functions for checking permissions
  const hasPermission = (permission: Permission): boolean => {
    return userPermissions.includes(permission);
  };

  // Simplified feature flag check - we'll just check if the user has permission
  // to access a feature, rather than checking tenant feature flags
  const isFeatureEnabled = (featureName: string): boolean => {
    // Convert to permission format (view_{feature})
    const viewPermission = `view_${featureName}` as Permission;
    return hasPermission(viewPermission);
  };

  // Determine if user can access a specific tab based on permissions
  const canAccessTab = (feature: string, tab: ServiceTab): boolean => {
    // Basic view permission check
    const viewPermissionName = `view_${feature}` as Permission;
    if (!hasPermission(viewPermissionName)) return false;

    // For certain tabs that require more privileges
    if (tab === 'deep-analysis' || tab === 'review-export') {
      const startPermissionName = `start_${feature}` as Permission;
      return hasPermission(startPermissionName);
    }

    // Default access for other tabs if user has general view permission
    return true;
  };

  // Context value
  const contextValue: RBACContextType = {
    userPermissions,
    sidebarFeatures,
    isLoading,
    hasPermission,
    isFeatureEnabled,
    canAccessTab
  };

  return (
    <RBACContext.Provider value={contextValue}>
      {children}
    </RBACContext.Provider>
  );
};

export const useRBAC = () => {
  const context = useContext(RBACContext);
  if (!context) {
    throw new Error('useRBAC must be used within an RBACProvider');
  }
  return context;
};
