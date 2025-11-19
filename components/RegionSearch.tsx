import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { Region } from '../types';

interface RegionSearchProps {
  regions: Region[];
  onRegionSelect: (region: Region) => void;
}

export interface RegionSearchRef {
  focus: () => void;
  clear: () => void;
}

const RegionSearch = forwardRef<RegionSearchRef, RegionSearchProps>(({ regions, onRegionSelect }, ref) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Expose methods to parent component via ref
  useImperativeHandle(ref, () => ({
    focus: () => {
      inputRef.current?.focus();
    },
    clear: () => {
      handleClear();
    }
  }));

  // Filter regions based on search term with fuzzy matching
  const filteredRegions = searchTerm.trim()
    ? regions.filter(region =>
        region.name.toLowerCase().includes(searchTerm.toLowerCase())
      ).slice(0, 6) // Limit to 6 results
    : [];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && filteredRegions.length > 0 && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      setIsOpen(true);
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev < filteredRegions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredRegions.length) {
          handleSelectRegion(filteredRegions[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Handle region selection
  const handleSelectRegion = (region: Region) => {
    setSearchTerm(region.name);
    setIsOpen(false);
    setSelectedIndex(-1);
    onRegionSelect(region);
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setIsOpen(value.trim().length > 0);
    setSelectedIndex(-1);
  };

  // Clear search
  const handleClear = () => {
    setSearchTerm('');
    setIsOpen(false);
    setSelectedIndex(-1);
    inputRef.current?.focus();
  };

  // Highlight matching text
  const highlightMatch = (text: string, query: string) => {
    if (!query.trim()) return text;

    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) =>
      regex.test(part) ? (
        <span key={index} className="font-semibold text-blue-700">
          {part}
        </span>
      ) : (
        <span key={index}>{part}</span>
      )
    );
  };

  return (
    <div className="relative w-full max-w-md">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-slate-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (searchTerm.trim() && filteredRegions.length > 0) {
              setIsOpen(true);
            }
          }}
          placeholder="Search regions..."
          className="block w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg text-sm
                     placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500
                     focus:border-transparent bg-white shadow-sm transition-all"
        />
        {searchTerm && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400
                       hover:text-slate-600 transition-colors"
            aria-label="Clear search"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && filteredRegions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-lg
                     shadow-lg max-h-80 overflow-y-auto"
        >
          <ul className="py-1">
            {filteredRegions.map((region, index) => (
              <li key={region.name}>
                <button
                  onClick={() => handleSelectRegion(region)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors
                             flex items-center justify-between group
                             ${selectedIndex === index ? 'bg-blue-50' : ''}`}
                >
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-900">
                      {highlightMatch(region.name, searchTerm)}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      Lat: {region.lat.toFixed(2)}, Lon: {region.lon.toFixed(2)}
                    </div>
                  </div>
                  <div className="ml-3 flex items-center gap-2">
                    <div className="text-xs text-slate-400 group-hover:text-blue-600 transition-colors">
                      Risk: {region.baseRisk}
                    </div>
                    <svg
                      className="h-4 w-4 text-slate-300 group-hover:text-blue-600 transition-colors"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* No Results Message */}
      {isOpen && searchTerm.trim() && filteredRegions.length === 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-lg
                     shadow-lg py-4 px-4"
        >
          <div className="text-center text-slate-500 text-sm">
            <svg
              className="h-8 w-8 mx-auto mb-2 text-slate-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="font-medium">No regions found</p>
            <p className="text-xs mt-1">Try adjusting your search</p>
          </div>
        </div>
      )}
    </div>
  );
});

RegionSearch.displayName = 'RegionSearch';

export default RegionSearch;
