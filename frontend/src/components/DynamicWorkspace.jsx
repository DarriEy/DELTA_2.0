import React from 'react';
import EducationalPanel from './ControlPanels/EducationalPanel';
import ModelingPanel from './ControlPanels/ModelingPanel';
import DataAnalysisPanel from './ControlPanels/DataAnalysisPanel';
import GeneralPanel from './Layout/GeneralPanel';

const DynamicWorkspace = ({ 
  activeMode, 
  showContentFrame, 
  currentEducationalContent, 
  selectedModel, 
  setSelectedModel, 
  handleModelingJobSubmit, 
  isProcessing, 
  jobStatus, 
  currentDataAnalysisContent 
}) => {
  return (
    <div className={`transition-all duration-700 h-full ${showContentFrame ? 'opacity-100 translate-y-0' : 'opacity-60 translate-y-4 pointer-events-none grayscale blur-sm'}`}>
      <div className="h-full bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[2rem] p-10 overflow-y-auto scrollbar-hide">
        {activeMode === 'educational' && <EducationalPanel content={currentEducationalContent} />}
        {activeMode === 'modeling' && (
          <ModelingPanel 
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            onJobSubmit={() => handleModelingJobSubmit(selectedModel)}
            isProcessing={isProcessing}
            jobStatus={jobStatus}
          />
        )}
        {activeMode === 'dataAnalysis' && <DataAnalysisPanel content={currentDataAnalysisContent} />}
        
        {activeMode === 'general' && (
          <GeneralPanel />
        )}
      </div>
    </div>
  );
};

export default DynamicWorkspace;
