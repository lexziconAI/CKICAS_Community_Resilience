import toast from 'react-hot-toast';

export const toastNotifications = {
  triggerFired: (triggerName: string, region: string) => {
    toast.error(
      `Alert Triggered: ${triggerName} in ${region}`,
      {
        duration: 5000,
        icon: '🚨',
        style: {
          border: '1px solid #EF4444',
          padding: '16px',
          color: '#7F1D1D',
        },
      }
    );
  },

  multipleTriggersFired: (count: number) => {
    toast.error(
      `${count} Alerts Triggered! Check dashboard for details.`,
      {
        duration: 5000,
        icon: '🚨',
        style: {
          border: '1px solid #EF4444',
          padding: '16px',
          color: '#7F1D1D',
        },
      }
    );
  },

  dataRefreshSuccess: () => {
    toast.success('Data refreshed successfully', {
      duration: 3000,
      icon: '🔄',
    });
  },

  dataRefreshError: () => {
    toast.error('Failed to refresh data. Check connection.', {
      duration: 4000,
      icon: '⚠️',
    });
  },

  regionLoaded: (regionName: string) => {
    toast.success(`Loaded data for ${regionName}`, {
      duration: 2000,
      icon: '📍',
    });
  }
};
