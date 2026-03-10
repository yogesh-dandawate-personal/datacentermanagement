/**
 * ListingSearch Component
 * Advanced search and filter controls for marketplace listings
 */

import { Search, Filter, X, SlidersHorizontal } from 'lucide-react'
import { useState } from 'react'
import { Input, Select, Button, Badge } from '../ui'
import type { ListingFilters } from '../../types/marketplace'

export interface ListingSearchProps {
  filters: ListingFilters
  onFilterChange: (filters: Partial<ListingFilters>) => void
  onClearFilters: () => void
  onSearch: () => void
}

export function ListingSearch({ filters, onFilterChange, onClearFilters, onSearch }: ListingSearchProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [searchInput, setSearchInput] = useState(filters.search || '')

  const handleSearchInputChange = (value: string) => {
    setSearchInput(value)
    onFilterChange({ search: value })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSearch()
    }
  }

  const activeFilterCount = () => {
    let count = 0
    if (filters.search) count++
    if (filters.min_price) count++
    if (filters.max_price) count++
    if (filters.listing_type && filters.listing_type !== 'all') count++
    if (filters.min_quality) count++
    if (filters.sort_by && filters.sort_by !== 'date_desc') count++
    return count
  }

  const filterCount = activeFilterCount()

  return (
    <div className="space-y-4">
      {/* Main Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <Input
            type="text"
            placeholder="Search by batch name, seller, or credit type..."
            value={searchInput}
            onChange={(e) => handleSearchInputChange(e.target.value)}
            onKeyPress={handleKeyPress}
            className="pl-10 bg-slate-800 border-slate-700 text-white"
          />
          {searchInput && (
            <button
              onClick={() => handleSearchInputChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <Button
          variant="outline"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="gap-2 relative"
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span className="hidden sm:inline">Advanced Filters</span>
          <span className="sm:hidden">Filters</span>
          {filterCount > 0 && (
            <Badge size="sm" className="absolute -top-2 -right-2 bg-primary-600 text-white border-primary-500">
              {filterCount}
            </Badge>
          )}
        </Button>

        <Button
          onClick={onSearch}
          className="gap-2 bg-primary-600 hover:bg-primary-700 text-white"
        >
          <Search className="w-4 h-4" />
          Search
        </Button>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Advanced Filters
            </h3>
            {filterCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearFilters}
                className="gap-2 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
                Clear All
              </Button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Price Range */}
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Min Price ($)</label>
              <Input
                type="number"
                placeholder="0"
                value={filters.min_price || ''}
                onChange={(e) => onFilterChange({ min_price: parseFloat(e.target.value) || undefined })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm text-slate-300">Max Price ($)</label>
              <Input
                type="number"
                placeholder="1000"
                value={filters.max_price || ''}
                onChange={(e) => onFilterChange({ max_price: parseFloat(e.target.value) || undefined })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>

            {/* Listing Type */}
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Listing Type</label>
              <Select
                value={filters.listing_type || 'all'}
                onChange={(e) => onFilterChange({ listing_type: e.target.value as any })}
                className="bg-slate-900 border-slate-700 text-white"
              >
                <option value="all">All Types</option>
                <option value="fixed_price">Fixed Price</option>
                <option value="auction">Auction</option>
                <option value="negotiable">Negotiable</option>
              </Select>
            </div>

            {/* Quality Score */}
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Min Quality (%)</label>
              <Input
                type="number"
                placeholder="80"
                min="0"
                max="100"
                value={filters.min_quality || ''}
                onChange={(e) => onFilterChange({ min_quality: parseFloat(e.target.value) || undefined })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
          </div>

          {/* Sort Options */}
          <div className="border-t border-slate-700/50 pt-4">
            <label className="text-sm text-slate-300 block mb-2">Sort By</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {[
                { value: 'price_asc', label: 'Price: Low to High' },
                { value: 'price_desc', label: 'Price: High to Low' },
                { value: 'date_desc', label: 'Newest First' },
                { value: 'date_asc', label: 'Oldest First' },
                { value: 'quality_desc', label: 'Quality: High to Low' },
              ].map((option) => (
                <Button
                  key={option.value}
                  variant={filters.sort_by === option.value ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => onFilterChange({ sort_by: option.value as any })}
                  className="whitespace-nowrap"
                >
                  {option.label}
                </Button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Summary */}
      {filterCount > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-slate-400">Active filters:</span>
          {filters.search && (
            <Badge variant="secondary" className="gap-1">
              Search: {filters.search}
              <button onClick={() => onFilterChange({ search: undefined })}>
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.min_price && (
            <Badge variant="secondary" className="gap-1">
              Min: ${filters.min_price}
              <button onClick={() => onFilterChange({ min_price: undefined })}>
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.max_price && (
            <Badge variant="secondary" className="gap-1">
              Max: ${filters.max_price}
              <button onClick={() => onFilterChange({ max_price: undefined })}>
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.listing_type && filters.listing_type !== 'all' && (
            <Badge variant="secondary" className="gap-1">
              Type: {filters.listing_type}
              <button onClick={() => onFilterChange({ listing_type: undefined })}>
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
          {filters.min_quality && (
            <Badge variant="secondary" className="gap-1">
              Quality: {filters.min_quality}%+
              <button onClick={() => onFilterChange({ min_quality: undefined })}>
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}
        </div>
      )}
    </div>
  )
}
