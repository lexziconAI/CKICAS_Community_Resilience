import React, { useState } from 'react';
import { User } from '../types';

interface UserSelectorProps {
  onUserChange: (user: User) => void;
  selectedUser: User | null;
}

// Mock users for the MVP
const MOCK_USERS: User[] = [
  {
    id: 'user_1',
    name: 'Regan',
    email: 'regan@axiomintelligence.co.nz',
    organization: 'Axiom Intelligence',
    region: 'Auckland',
  },
  {
    id: 'user_2',
    name: 'Tim House',
    email: 'tim.house@fonterra.com',
    organization: 'Fonterra',
    region: 'Taranaki',
  },
];

const UserSelector: React.FC<UserSelectorProps> = ({ onUserChange, selectedUser }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleUserSelect = (user: User) => {
    onUserChange(user);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
            {selectedUser ? selectedUser.name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="text-left">
            {selectedUser ? (
              <>
                <div className="text-sm font-semibold text-slate-900">{selectedUser.name}</div>
                <div className="text-xs text-slate-500">{selectedUser.email}</div>
              </>
            ) : (
              <div className="text-sm text-slate-500">Select a user</div>
            )}
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown Menu */}
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-200 rounded-lg shadow-lg z-20 overflow-hidden">
            {MOCK_USERS.map((user) => (
              <button
                key={user.id}
                onClick={() => handleUserSelect(user)}
                className={`w-full px-4 py-3 text-left hover:bg-slate-50 transition-colors border-b border-slate-100 last:border-b-0 ${
                  selectedUser?.id === user.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-slate-900">{user.name}</div>
                    <div className="text-xs text-slate-500">{user.email}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      {user.organization} • {user.region}
                    </div>
                  </div>
                  {selectedUser?.id === user.id && (
                    <svg
                      className="w-5 h-5 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>
        </>
      )}

      {/* User Info Display (when selected) */}
      {selectedUser && (
        <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-500 font-medium">Organization:</span>
              <div className="text-slate-900 font-semibold">{selectedUser.organization}</div>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Primary Region:</span>
              <div className="text-slate-900 font-semibold">{selectedUser.region}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserSelector;
