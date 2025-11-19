import React, { useState } from 'react';
import { Trigger } from '../../types';

interface TriggerListProps {
  triggers: Trigger[];
  loading: boolean;
  onEdit: (trigger: Trigger) => void;
  onDelete: (triggerId: string) => void;
  onToggle: (triggerId: string) => void;
}

const TriggerList: React.FC<TriggerListProps> = ({
  triggers,
  loading,
  onEdit,
  onDelete,
  onToggle,
}) => {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDeleteClick = (triggerId: string) => {
    setDeletingId(triggerId);
  };

  const confirmDelete = (triggerId: string) => {
    onDelete(triggerId);
    setDeletingId(null);
  };

  const cancelDelete = () => {
    setDeletingId(null);
  };

  const getCombinationRuleLabel = (rule: string): string => {
    const labels: Record<string, string> = {
      any_1: 'Any 1 condition',
      any_2: 'Any 2 conditions',
      any_3: 'Any 3 conditions',
      all: 'All conditions',
    };
    return labels[rule] || rule;
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm animate-pulse"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="h-5 bg-slate-200 rounded w-48 mb-2"></div>
                <div className="h-4 bg-slate-100 rounded w-32"></div>
              </div>
              <div className="h-6 w-16 bg-slate-200 rounded-full"></div>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="h-4 bg-slate-100 rounded"></div>
              <div className="h-4 bg-slate-100 rounded"></div>
            </div>
            <div className="flex gap-2">
              <div className="h-8 w-20 bg-slate-200 rounded"></div>
              <div className="h-8 w-20 bg-slate-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (triggers.length === 0) {
    return (
      <div className="bg-white rounded-xl p-12 border border-slate-200 shadow-sm text-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-slate-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-1">No Triggers Yet</h3>
            <p className="text-sm text-slate-500">
              Create your first drought alert trigger to get started
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {triggers.map((trigger) => (
        <div
          key={trigger.id}
          className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-slate-900 mb-1">{trigger.name}</h3>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                {trigger.region}
              </div>
            </div>
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full ${
                trigger.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {trigger.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          {/* Details */}
          <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-slate-100">
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                Conditions
              </span>
              <div className="text-sm font-semibold text-slate-900 mt-1">
                {trigger.conditions.length} condition{trigger.conditions.length !== 1 ? 's' : ''}
              </div>
            </div>
            <div>
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                Combination Rule
              </span>
              <div className="text-sm font-semibold text-slate-900 mt-1">
                {getCombinationRuleLabel(trigger.combination_rule)}
              </div>
            </div>
          </div>

          {/* Conditions Preview */}
          <div className="mb-4">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wide block mb-2">
              Trigger Conditions
            </span>
            <div className="space-y-1.5">
              {trigger.conditions.map((condition, index) => (
                <div
                  key={index}
                  className="text-sm text-slate-700 bg-slate-50 px-3 py-2 rounded-lg flex items-center gap-2"
                >
                  <span className="font-medium capitalize">{condition.indicator}</span>
                  <span className="text-slate-500">{condition.operator}</span>
                  <span className="font-semibold">{condition.threshold}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          {deletingId === trigger.id ? (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <svg
                className="w-5 h-5 text-red-600 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <span className="text-sm font-medium text-red-900 flex-1">
                Are you sure you want to delete this trigger?
              </span>
              <button
                onClick={cancelDelete}
                className="px-3 py-1.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => confirmDelete(trigger.id)}
                className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => onToggle(trigger.id)}
                className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  trigger.is_active
                    ? 'text-slate-600 bg-slate-100 hover:bg-slate-200'
                    : 'text-green-600 bg-green-50 hover:bg-green-100'
                }`}
              >
                {trigger.is_active ? (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Deactivate
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Activate
                  </>
                )}
              </button>
              <button
                onClick={() => onEdit(trigger)}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                Edit
              </button>
              <button
                onClick={() => handleDeleteClick(trigger.id)}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                Delete
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default TriggerList;
