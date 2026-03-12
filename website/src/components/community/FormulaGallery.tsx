import React, { useState, useEffect } from 'react';
import { Search, Download, Star, Eye, User, Tag } from 'lucide-react';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface Formula {
  id: string;
  title: string;
  description?: string;
  formulaType: string;
  visibility: string;
  rating?: number;
  ratingCount?: number;
  usageCount?: number;
  createdAt: string;
  author_display_name?: string;
  author_avatar_url?: string;
}

interface FormulaGalleryProps {
  apiBase: string;
}

export const FormulaGallery: React.FC<FormulaGalleryProps> = ({ apiBase }) => {
  const [formulas, setFormulas] = useState<Formula[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [sortBy, setSortBy] = useState<'recent' | 'rating' | 'usage'>('recent');

  useEffect(() => {
    fetchFormulas();
  }, [searchTerm, selectedType, sortBy]);

  const fetchFormulas = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.set('query', searchTerm);
      if (selectedType !== 'all') params.set('type', selectedType);
      params.set('sort', sortBy);
      params.set('limit', '12');

      const response = await fetch(`${apiBase}/community/formulas?${params}`);
      if (response.ok) {
        const data = await response.json();
        setFormulas(data);
      }
    } catch (error) {
      console.error('Failed to fetch formulas:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      'confidence-cascade': '🎯',
      'smp': '🤖',
      'tile': '🧩',
      'default': '🔧'
    };
    return icons[type] || icons.default;
  };

  const previewFormula = async (formulaId: string) => {
    window.open(`/community/formulas/${formulaId}`, '_blank');
  };

  const downloadFormula = async (formula: Formula) => {
    try {
      const code = JSON.parse(formula.formulaCode);
      const blob = new Blob([JSON.stringify(code, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${formula.title.replace(/\s+/g, '-').toLowerCase()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download formula:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Shared Formulas</h2>
        <Button
          variant="primary"
          onClick={() => window.location.href = '/community/contribute'}
        >
          Share Your Formula
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search formulas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Types</option>
          <option value="confidence-cascade">Confidence Cascade</option>
          <option value="smp">SMP Systems</option>
          <option value="tile">Tile Algebra</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="recent">Most Recent</option>
          <option value="rating">Highest Rated</option>
          <option value="usage">Most Used</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {formulas.map((formula) => (
            <div key={formula.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getTypeIcon(formula.formulaType)}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{formula.title}</h3>
                    <p className="text-sm text-gray-500">{formula.formulaType.replace('-', ' ').toUpperCase()}</p>
                  </div>
                </div>
                {formula.visibility === 'public' && <Badge variant="success">Public</Badge>}
              </div>

              {formula.description && (
                <p className="text-gray-700 text-sm mb-3 line-clamp-2">{formula.description}</p>
              )}

              {formula.tags && formula.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {formula.tags.map((tag, idx) => (
                    <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full bg-gray-100 text-xs">
                      <Tag className="w-3 h-3 mr-1" /> {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                <div className="flex items-center space-x-4">
                  {formula.rating && (
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-400 mr-1" /> {formula.rating.toFixed(1)} ({formula.ratingCount})
                    </div>
                  )}
                  <div className="flex items-center">
                    <Eye className="w-4 h-4 mr-1" /> {formula.usageCount || 0}
                  </div>
                </div>
                <div className="flex items-center">
                  <User className="w-4 h-4 mr-1" /> {
                    formula.author_display_name || 'Anonymous'
                  }
                </div>
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => previewFormula(formula.id)}
                  className="flex-1"
                >
                  Preview
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => downloadFormula(formula)}
                  title="Download JSON"
                >
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && formulas.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No formulas found. Try adjusting your filters.</p>
        </div>
      )}
    </div>
  );
};