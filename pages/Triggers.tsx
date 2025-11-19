import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TriggerList, TriggerForm } from '../components/triggers';
import { Trigger, TriggerFormData } from '../types';

// Mock data for initial state
const MOCK_TRIGGERS: Trigger[] = [
  {
    id: '1',
    name: 'High Temp Alert - Canterbury',
    region: 'Canterbury',
    conditions: [
      { indicator: 'temp', operator: '>', threshold: 25 }
    ],
    combination_rule: 'any_1',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    user_id: 'user_1'
  },
  {
    id: '2',
    name: 'Drought Warning - Hawke\'s Bay',
    region: 'Hawke\'s Bay',
    conditions: [
      { indicator: 'rainfall', operator: '<', threshold: 10 },
      { indicator: 'soil_moisture', operator: '<', threshold: 30 }
    ],
    combination_rule: 'all',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    user_id: 'user_1'
  }
];

const Triggers: React.FC = () => {
  const [triggers, setTriggers] = useState<Trigger[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingTrigger, setEditingTrigger] = useState<Trigger | null>(null);

  useEffect(() => {
    // Simulate API fetch
    const timer = setTimeout(() => {
      setTriggers(MOCK_TRIGGERS);
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleCreateTrigger = (data: TriggerFormData) => {
    const newTrigger: Trigger = {
      id: Math.random().toString(36).substr(2, 9),
      ...data,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      user_id: 'user_1'
    };
    setTriggers([newTrigger, ...triggers]);
  };

  const handleUpdateTrigger = (data: TriggerFormData) => {
    if (!editingTrigger) return;
    
    const updatedTriggers = triggers.map(t => 
      t.id === editingTrigger.id 
        ? { ...t, ...data, updated_at: new Date().toISOString() }
        : t
    );
    setTriggers(updatedTriggers);
    setEditingTrigger(null);
  };

  const handleDeleteTrigger = (triggerId: string) => {
    setTriggers(triggers.filter(t => t.id !== triggerId));
  };

  const handleToggleTrigger = (triggerId: string) => {
    setTriggers(triggers.map(t => 
      t.id === triggerId 
        ? { ...t, is_active: !t.is_active }
        : t
    ));
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
             <Link to="/" className="font-bold text-xl text-slate-900 tracking-tight hover:text-blue-600 transition-colors">
              CKCIAS <span className="text-slate-500 font-normal">Drought Monitor</span>
            </Link>
            <span className="text-slate-300">/</span>
            <h2 className="font-semibold text-slate-700">Alert Triggers</h2>
          </div>
          <Link
            to="/"
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h3 className="text-lg font-bold text-slate-800">Active Triggers</h3>
                <p className="text-sm text-slate-500 mt-1">Manage your automated alert conditions</p>
              </div>
              <div className="p-6">
                <TriggerList 
                  triggers={triggers}
                  loading={loading}
                  onEdit={setEditingTrigger}
                  onDelete={handleDeleteTrigger}
                  onToggle={handleToggleTrigger}
                />
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sticky top-24">
              <h3 className="text-lg font-bold text-slate-800 mb-4">
                {editingTrigger ? 'Edit Trigger' : 'Create New Trigger'}
              </h3>
              <TriggerForm 
                onSubmit={editingTrigger ? handleUpdateTrigger : handleCreateTrigger}
                onCancel={() => setEditingTrigger(null)}
                initialData={editingTrigger}
                userId="user_1"
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Triggers;
