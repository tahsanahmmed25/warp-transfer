import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Monitor, Smartphone, Settings, History, Check, AlertCircle, HelpCircle } from 'lucide-react';

const mockPages = [
  {
    id: 'onboarding',
    tabName: 'Onboarding',
    icon: Monitor,
    title: 'Step-by-step Onboarding Wizard',
    description: 'A beautiful step card layout that guides users through enabling USB debugging, installing OEM drivers, and matching device setups on first launch.',
    // Fluent PyQt UI mock
    renderUI: (isDark: boolean) => (
      <div class="w-full h-full flex flex-col bg-bg-secondary p-5 border border-border-custom rounded-xl font-body select-none">
        <div class="flex items-center justify-between border-b border-border-custom pb-3 mb-4">
          <span class="text-xs font-bold text-text-muted">Setup wizard</span>
          <div class="flex space-x-1.5">
            <span class="w-2.5 h-2.5 rounded-full bg-gold"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-border-custom"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-border-custom"></span>
          </div>
        </div>
        <div class="flex flex-col items-center justify-center my-auto text-center">
          <div class="h-10 w-10 rounded-full bg-gold-glow border border-gold/30 text-gold flex items-center justify-center mb-4">
            <Smartphone className="h-5 w-5" />
          </div>
          <h4 class="font-display text-sm font-bold text-text-main mb-1">Set up your Android Device</h4>
          <p class="text-[10px] text-text-muted max-w-[200px] mb-4">Ensure your device is connected via USB cable and debugging is enabled.</p>
          
          <div class="w-full space-y-2 max-w-[260px]">
            <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-border-custom text-[10px] text-text-main text-left">
              <span>1. Enable USB Debugging</span>
              <Check className="h-3.5 w-3.5 text-gold" />
            </div>
            <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-border-custom text-[10px] text-text-main text-left opacity-60">
              <span>2. Accept RSA Fingerprint</span>
              <span class="text-[9px] text-text-muted">Waiting...</span>
            </div>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'dashboard',
    tabName: 'Device Connection',
    icon: Smartphone,
    title: 'Visual Device Status Card',
    description: 'Dynamic device polling updates layouts automatically. Shows custom styled memory bars, storage scopes, and rapid backup shortcuts.',
    renderUI: (isDark: boolean) => (
      <div class="w-full h-full flex flex-col bg-bg-secondary p-5 border border-border-custom rounded-xl font-body select-none">
        <div class="flex items-center justify-between border-b border-border-custom pb-3 mb-4">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-ping"></span>
            <span class="text-[10px] font-bold text-text-main">Connected</span>
          </div>
          <span class="text-[10px] text-text-muted">Redmi Note 7 Pro</span>
        </div>
        <div class="flex flex-col space-y-4 my-auto">
          {/* Device storage summary */}
          <div class="flex flex-col p-3 rounded-xl bg-bg-primary border border-border-custom">
            <div class="flex justify-between items-center text-[10px] text-text-muted mb-1.5">
              <span>Internal Storage</span>
              <span class="font-bold text-text-main">52.4 GB / 128 GB Free</span>
            </div>
            <div class="w-full h-1.5 bg-border-custom rounded-full overflow-hidden">
              <div class="h-full bg-gold rounded-full w-[60%]" />
            </div>
          </div>

          {/* DCIM preset copy trigger */}
          <div class="grid grid-cols-2 gap-2">
            <div class="flex flex-col p-2.5 rounded-xl bg-bg-primary border border-border-custom text-left hover:border-gold transition-colors">
              <span class="text-[9px] font-bold text-text-muted">PHOTOS PRESET</span>
              <span class="text-[11px] font-bold text-text-main mt-0.5">Backup Camera</span>
              <span class="text-[8px] text-text-muted mt-2">DCIM folder (1,280 files)</span>
            </div>
            <div class="flex flex-col p-2.5 rounded-xl bg-bg-primary border border-border-custom text-left hover:border-gold transition-colors">
              <span class="text-[9px] font-bold text-text-muted">DOWNLOAD PRESET</span>
              <span class="text-[11px] font-bold text-text-main mt-0.5">Backup Downloads</span>
              <span class="text-[8px] text-text-muted mt-2">Download folder (42 files)</span>
            </div>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'conflict',
    tabName: 'Collision Solver',
    icon: Settings,
    title: 'Advanced Collision Picker',
    description: 'Keep your backups clean with customizable collision policies. Configurable directly in the GUI: Overwrite, Skip, Ask, or Auto-Rename files.',
    renderUI: (isDark: boolean) => (
      <div class="w-full h-full flex flex-col bg-bg-secondary p-5 border border-border-custom rounded-xl font-body select-none">
        <div class="flex items-center justify-between border-b border-border-custom pb-3 mb-3">
          <span class="text-[10px] font-bold text-text-main">File Conflict Detected</span>
          <AlertCircle className="h-4 w-4 text-gold" />
        </div>
        <div class="flex flex-col my-auto space-y-3">
          <p class="text-[10px] text-text-muted leading-relaxed">
            The target destination folder already contains a file named <strong class="text-text-main">IMG_20260716.jpg</strong>. What would you like to do?
          </p>

          <div class="flex flex-col space-y-1.5">
            <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-gold/30 text-[9px] text-gold font-bold">
              <span>Rename (Keep Both files)</span>
              <span class="text-[8px] opacity-60">IMG_20260716(1).jpg</span>
            </div>
            <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-border-custom text-[9px] text-text-main opacity-80 hover:border-gold transition-colors">
              <span>Skip file</span>
            </div>
            <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-border-custom text-[9px] text-text-main opacity-80 hover:border-gold transition-colors">
              <span>Overwrite existing file</span>
            </div>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'history',
    tabName: 'History Logs',
    icon: History,
    title: 'Transfer History Records',
    description: 'A detailed timeline documenting files copied, speeds achieved, and session durations, persisting transfer statistics across launches.',
    renderUI: (isDark: boolean) => (
      <div class="w-full h-full flex flex-col bg-bg-secondary p-5 border border-border-custom rounded-xl font-body select-none">
        <div class="flex items-center justify-between border-b border-border-custom pb-3 mb-3">
          <span class="text-[10px] font-bold text-text-main">Transfer History</span>
          <span class="text-[9px] text-text-muted">Last 7 Days</span>
        </div>
        <div class="flex flex-col space-y-2 overflow-hidden my-auto">
          {/* Row 1 */}
          <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-border-custom text-[9px]">
            <div class="flex flex-col text-left">
              <span class="font-bold text-text-main">Camera DCIM backup</span>
              <span class="text-[8px] text-text-muted mt-0.5">USB Pull • 1,280 files</span>
            </div>
            <div class="flex flex-col text-right">
              <span class="font-bold text-gold">3.2 GB • Success</span>
              <span class="text-[8px] text-text-muted mt-0.5">38.4 MB/s • 1m 24s</span>
            </div>
          </div>
          {/* Row 2 */}
          <div class="flex items-center justify-between p-2 rounded-lg bg-bg-primary border border-border-custom text-[9px]">
            <div class="flex flex-col text-left">
              <span class="font-bold text-text-main">Download folder push</span>
              <span class="text-[8px] text-text-muted mt-0.5">USB Push • 12 files</span>
            </div>
            <div class="flex flex-col text-right">
              <span class="font-bold text-text-main">48 MB • Success</span>
              <span class="text-[8px] text-text-muted mt-0.5">24.1 MB/s • 2s</span>
            </div>
          </div>
        </div>
      </div>
    )
  }
];

export default function AppCarousel() {
  const [activeTab, setActiveTab] = useState('onboarding');

  const currentPage = mockPages.find(p => p.id === activeTab) || mockPages[0];

  return (
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center w-full">
      {/* Left Column: Navigation & Content */}
      <div class="lg:col-span-5 flex flex-col space-y-6">
        <div class="flex flex-row lg:flex-col overflow-x-auto lg:overflow-x-visible space-x-2 lg:space-x-0 lg:space-y-2 border-b lg:border-b-0 border-border-custom pb-3 lg:pb-0">
          {mockPages.map(page => {
            const Icon = page.icon;
            const isActive = page.id === activeTab;
            return (
              <button
                key={page.id}
                onClick={() => setActiveTab(page.id)}
                class={`flex items-center space-x-3 px-4 py-2.5 rounded-xl border font-display text-sm font-semibold tracking-tight transition-all duration-300 cursor-pointer shrink-0 ${
                  isActive 
                    ? 'border-gold bg-gold-glow text-gold shadow-md' 
                    : 'border-transparent text-text-muted hover:text-text-main hover:bg-border-custom/20'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{page.tabName}</span>
              </button>
            );
          })}
        </div>

        {/* Description Box */}
        <div class="flex flex-col text-center lg:text-left">
          <h3 class="font-display text-xl font-bold text-text-main mb-2">
            {currentPage.title}
          </h3>
          <p class="font-body text-xs sm:text-sm text-text-muted leading-relaxed">
            {currentPage.description}
          </p>
        </div>
      </div>

      {/* Right Column: Interactive Browser Frame */}
      <div class="lg:col-span-7 flex justify-center w-full">
        {/* Mock Windows App Frame */}
        <div class="w-full max-w-sm aspect-[4/3] rounded-2xl border border-border-custom bg-bg-secondary/20 p-2.5 flex flex-col shadow-lg shadow-black/20">
          <div class="flex items-center justify-between px-3 pb-2 border-b border-border-custom/50 text-[10px] text-text-muted font-body">
            {/* Window Title */}
            <div class="flex items-center space-x-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-border-custom"></span>
              <span class="font-bold text-text-main">Warp Transfer v1.0.0</span>
            </div>
            {/* Window Buttons */}
            <div class="flex space-x-1">
              <span class="w-2.5 h-0.5 bg-text-muted"></span>
              <span class="w-2.5 h-2.5 border border-text-muted rounded-xs"></span>
              <span class="w-2.5 h-2.5 text-text-muted leading-none">×</span>
            </div>
          </div>

          {/* Window Body */}
          <div class="flex-grow rounded-lg bg-bg-primary overflow-hidden p-3 flex items-center justify-center relative mt-2.5">
            <AnimatePresence mode="wait">
              <motion.div 
                key={currentPage.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="w-full h-full"
              >
                {currentPage.renderUI(true)}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
