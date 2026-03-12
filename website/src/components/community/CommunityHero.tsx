import React from 'react';
import { Button } from '../ui/Button';
import { CommunityIcon, FormulaIcon, DiscussionIcon } from '../icons/CommunityIcons';

export const CommunityHero: React.FC = () => {
  return (
    <section className="bg-gradient-to-br from-blue-600 to-purple-700 text-white">
      <div className="container-wide py-16 px-6">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            SuperInstance Community
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100">
            Connect with fellow spreadsheet AI enthusiasts, share formulas, and collaborate on new ideas
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <Button variant="primary" className="bg-white text-blue-600 hover:bg-gray-100">
              <FormulaIcon className="w-5 h-5 mr-2" />
              Share a Formula
            </Button>
            <Button variant="outline" className="border-white text-white hover:bg-white/10">
              <DiscussionIcon className="w-5 h-5 mr-2" />
              Join Discussion
            </Button>
            <Button variant="outline" className="border-white text-white hover:bg-white/10">
              <CommunityIcon className="w-5 h-5 mr-2" />
              Find Workspace
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <div className="text-3xl font-bold mb-2">2,847</div>
              <div className="text-blue-100">Shared Formulas</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <div className="text-3xl font-bold mb-2">15.2k</div>
              <div className="text-blue-100">Community Members</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-6">
              <div className="text-3xl font-bold mb-2">892</div>
              <div className="text-blue-100">Active Discussions</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};