import React, { useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { TriggerCondition, TriggerIndicator, TriggerOperator, CombinationRule, Trigger, TriggerFormData } from '../../types';
import { NZ_REGIONS } from '../../constants';

interface TriggerFormProps {
  onSubmit: (data: TriggerFormData) => void;
  onCancel: () => void;
  initialData?: Trigger | null;
  userId: string;
}

const INDICATOR_OPTIONS: { value: TriggerIndicator; label: string; unit: string }[] = [
  { value: 'temp', label: 'Temperature', unit: 'C' },
  { value: 'rainfall', label: 'Rainfall', unit: 'mm' },
  { value: 'humidity', label: 'Humidity', unit: '%' },
  { value: 'wind_speed', label: 'Wind Speed', unit: 'm/s' },
];

const OPERATOR_OPTIONS: { value: TriggerOperator; label: string }[] = [
  { value: '>', label: 'Greater than (>)' },
  { value: '<', label: 'Less than (<)' },
  { value: '>=', label: 'Greater or equal (>=)' },
  { value: '<=', label: 'Less or equal (<=)' },
  { value: '==', label: 'Equal to (==)' },
];

const COMBINATION_RULE_OPTIONS: { value: CombinationRule; label: string; description: string }[] = [
  { value: 'any_1', label: 'Any 1 Condition', description: 'Trigger when at least 1 condition is met' },
  { value: 'any_2', label: 'Any 2 Conditions', description: 'Trigger when at least 2 conditions are met' },
  { value: 'any_3', label: 'Any 3 Conditions', description: 'Trigger when at least 3 conditions are met' },
  { value: 'all', label: 'All Conditions', description: 'Trigger only when all conditions are met' },
];

const TriggerForm: React.FC<TriggerFormProps> = ({ onSubmit, onCancel, initialData, userId }) => {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
    setError,
    clearErrors,
  } = useForm<TriggerFormData>({
    defaultValues: {
      name: initialData?.name || '',
      region: initialData?.region || '',
      conditions: initialData?.conditions || [{ indicator: 'temp', operator: '>', threshold: 0 }],
      combination_rule: initialData?.combination_rule || 'any_1',
      is_active: initialData?.is_active ?? true,
    },
    mode: 'onChange', // Enable real-time validation
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'conditions',
  });

  const watchedConditions = watch('conditions');

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        region: initialData.region,
        conditions: initialData.conditions,
        combination_rule: initialData.combination_rule,
        is_active: initialData.is_active,
      });
    }
  }, [initialData, reset]);

  // Validate that at least one condition exists
  useEffect(() => {
    if (fields.length === 0) {
      setError('conditions', {
        type: 'manual',
        message: 'At least one condition is required',
      });
    } else {
      clearErrors('conditions');
    }
  }, [fields.length, setError, clearErrors]);

  const handleFormSubmit = (data: TriggerFormData) => {
    // Additional validation before submission
    if (data.conditions.length === 0) {
      setError('conditions', {
        type: 'manual',
        message: 'At least one condition is required',
      });
      return;
    }

    // Validate all thresholds are valid numbers
    const hasInvalidThreshold = data.conditions.some(
      (condition) => isNaN(condition.threshold) || !isFinite(condition.threshold)
    );

    if (hasInvalidThreshold) {
      setError('conditions', {
        type: 'manual',
        message: 'All thresholds must be valid numbers',
      });
      return;
    }

    onSubmit(data);
  };

  const addCondition = () => {
    append({ indicator: 'temp', operator: '>', threshold: 0 });
  };

  const getUnitForIndicator = (indicator: TriggerIndicator): string => {
    const option = INDICATOR_OPTIONS.find((opt) => opt.value === indicator);
    return option?.unit || '';
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Trigger Name */}
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">
          Trigger Name
          <span className="text-red-500 ml-1">*</span>
        </label>
        <input
          type="text"
          {...register('name', {
            required: 'Trigger name is required',
            minLength: {
              value: 1,
              message: 'Trigger name must be at least 1 character',
            },
            maxLength: {
              value: 100,
              message: 'Trigger name must not exceed 100 characters',
            },
            validate: {
              notEmpty: (value) => value.trim().length > 0 || 'Trigger name cannot be empty or whitespace only',
            },
          })}
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.name ? 'border-red-500 bg-red-50' : 'border-slate-300'
          }`}
          placeholder="e.g., High Temperature Alert"
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      {/* Region Selection */}
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">
          Region
          <span className="text-red-500 ml-1">*</span>
        </label>
        <select
          {...register('region', { required: 'Region is required' })}
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            errors.region ? 'border-red-500 bg-red-50' : 'border-slate-300'
          }`}
        >
          <option value="">Select a region</option>
          {NZ_REGIONS.map((region) => (
            <option key={region.name} value={region.name}>
              {region.name}
            </option>
          ))}
        </select>
        {errors.region && (
          <p className="mt-1 text-sm text-red-600">{errors.region.message}</p>
        )}
      </div>

      {/* Conditions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="block text-sm font-semibold text-slate-700">
            Conditions
            <span className="text-red-500 ml-1">*</span>
          </label>
          <button
            type="button"
            onClick={addCondition}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Condition
          </button>
        </div>

        <div className="space-y-3">
          {fields.map((field, index) => {
            const selectedIndicator = watch(`conditions.${index}.indicator`);
            const unit = getUnitForIndicator(selectedIndicator);

            return (
              <div
                key={field.id}
                className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase">
                    Condition {index + 1}
                  </span>
                  {fields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-red-600 hover:text-red-700 p-1"
                      title="Remove condition"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Indicator */}
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">
                      Indicator
                    </label>
                    <select
                      {...register(`conditions.${index}.indicator`, {
                        required: 'Indicator is required',
                      })}
                      className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.conditions?.[index]?.indicator ? 'border-red-500 bg-red-50' : 'border-slate-300'
                      }`}
                    >
                      {INDICATOR_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    {errors.conditions?.[index]?.indicator && (
                      <p className="mt-1 text-xs text-red-600">
                        {errors.conditions[index]?.indicator?.message}
                      </p>
                    )}
                  </div>

                  {/* Operator */}
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">
                      Operator
                    </label>
                    <select
                      {...register(`conditions.${index}.operator`, {
                        required: 'Operator is required',
                      })}
                      className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                        errors.conditions?.[index]?.operator ? 'border-red-500 bg-red-50' : 'border-slate-300'
                      }`}
                    >
                      {OPERATOR_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    {errors.conditions?.[index]?.operator && (
                      <p className="mt-1 text-xs text-red-600">
                        {errors.conditions[index]?.operator?.message}
                      </p>
                    )}
                  </div>

                  {/* Threshold */}
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">
                      Threshold
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        step="0.1"
                        {...register(`conditions.${index}.threshold`, {
                          required: 'Threshold is required',
                          valueAsNumber: true,
                          validate: {
                            isNumber: (value) => !isNaN(value) || 'Must be a valid number',
                            isFinite: (value) => isFinite(value) || 'Must be a finite number',
                          },
                        })}
                        className={`w-full px-3 py-2 pr-12 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                          errors.conditions?.[index]?.threshold ? 'border-red-500 bg-red-50' : 'border-slate-300'
                        }`}
                        placeholder="0"
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-500">
                        {unit}
                      </span>
                    </div>
                    {errors.conditions?.[index]?.threshold && (
                      <p className="mt-1 text-xs text-red-600">
                        {errors.conditions[index]?.threshold?.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {(fields.length === 0 || errors.conditions) && (
          <div className="mt-2">
            {fields.length === 0 && (
              <p className="text-sm text-red-600 font-medium">At least one condition is required</p>
            )}
            {errors.conditions && typeof errors.conditions.message === 'string' && (
              <p className="text-sm text-red-600 font-medium">{errors.conditions.message}</p>
            )}
          </div>
        )}
      </div>

      {/* Combination Rule */}
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-3">
          Combination Rule
          <span className="text-red-500 ml-1">*</span>
        </label>
        <div className="space-y-2">
          {COMBINATION_RULE_OPTIONS.map((option) => (
            <label
              key={option.value}
              className="flex items-start gap-3 p-3 border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
            >
              <input
                type="radio"
                value={option.value}
                {...register('combination_rule', { required: 'Combination rule is required' })}
                className={`mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500 ${
                  errors.combination_rule ? 'border-red-500' : ''
                }`}
              />
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-900">{option.label}</div>
                <div className="text-xs text-slate-500 mt-0.5">{option.description}</div>
              </div>
            </label>
          ))}
        </div>
        {errors.combination_rule && (
          <p className="mt-1 text-sm text-red-600">{errors.combination_rule.message}</p>
        )}
      </div>

      {/* Active Toggle */}
      <div className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg">
        <div>
          <label className="text-sm font-semibold text-slate-700">Active Status</label>
          <p className="text-xs text-slate-500 mt-1">
            Enable or disable this trigger
          </p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            {...register('is_active')}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-200">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={Object.keys(errors).length > 0 || fields.length === 0}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600"
        >
          {initialData ? 'Update Trigger' : 'Create Trigger'}
        </button>
      </div>
    </form>
  );
};

export default TriggerForm;
