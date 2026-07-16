import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { RefreshCw, XCircle, CheckCircle, Folder, Cpu, AlertTriangle } from 'lucide-react';

export default function MtpVsWarp() {
  const [status, setStatus] = useState<'idle' | 'running' | 'done'>('idle');
  
  // MTP Simulator State
  const [mtpProgress, setMtpProgress] = useState(0);
  const [mtpSpeed, setMtpSpeed] = useState('0 KB/s');
  const [mtpError, setMtpError] = useState(false);

  // Warp Simulator State
  const [warpProgress, setWarpProgress] = useState(0);
  const [warpSpeed, setWarpSpeed] = useState('0 MB/s');
  const [warpActiveWorkers, setWarpActiveWorkers] = useState([0, 0, 0, 0]);

  useEffect(() => {
    if (status !== 'running') return;

    // 1. MTP Simulator Timer
    setMtpError(false);
    let mtpTick = 0;
    const mtpInterval = setInterval(() => {
      mtpTick++;
      if (mtpTick < 10) {
        setMtpProgress(p => Math.min(p + Math.floor(Math.random() * 4) + 1, 45));
        setMtpSpeed(`${(Math.random() * 3 + 0.2).toFixed(1)} MB/s`);
      } else if (mtpTick >= 10 && mtpTick < 18) {
        // Drop speed/freeze
        setMtpSpeed('120 KB/s');
        if (Math.random() > 0.5) setMtpProgress(p => Math.min(p + 1, 45));
      } else if (mtpTick >= 18) {
        // Pop error
        setMtpSpeed('0 KB/s');
        setMtpError(true);
        clearInterval(mtpInterval);
      }
    }, 500);

    // 2. Warp Simulator Timer
    let warpTick = 0;
    const warpInterval = setInterval(() => {
      warpTick++;
      if (warpTick <= 12) {
        setWarpProgress(p => Math.min(p + Math.floor(Math.random() * 12) + 6, 100));
        setWarpSpeed(`${(Math.random() * 6 + 35.2).toFixed(1)} MB/s`);
        // Randomize thread work heights
        setWarpActiveWorkers([
          Math.floor(Math.random() * 100),
          Math.floor(Math.random() * 100),
          Math.floor(Math.random() * 100),
          Math.floor(Math.random() * 100),
        ]);
      } else {
        setWarpProgress(100);
        setWarpSpeed('0 MB/s');
        setWarpActiveWorkers([0, 0, 0, 0]);
        setStatus('done');
        clearInterval(warpInterval);
      }
    }, 400);

    return () => {
      clearInterval(mtpInterval);
      clearInterval(warpInterval);
    };
  }, [status]);

  const startSimulation = () => {
    setMtpProgress(0);
    setMtpSpeed('0 KB/s');
    setMtpError(false);
    setWarpProgress(0);
    setWarpSpeed('0 MB/s');
    setWarpActiveWorkers([0, 0, 0, 0]);
    setStatus('running');
  };

  const resetSimulation = () => {
    setMtpProgress(0);
    setMtpSpeed('0 KB/s');
    setMtpError(false);
    setWarpProgress(0);
    setWarpSpeed('0 MB/s');
    setWarpActiveWorkers([0, 0, 0, 0]);
    setStatus('idle');
  };

  return (
    <div class="w-full flex flex-col space-y-6">
      {/* Controller Header */}
      <div class="flex items-center justify-between px-4 py-3 rounded-2xl glass-panel border border-border-custom bg-bg-secondary/40">
        <span class="font-display text-sm font-semibold tracking-tight text-text-muted">
          Speed Benchmarking (3.2 GB DCIM Folder)
        </span>
        {status === 'idle' ? (
          <button 
            onClick={startSimulation} 
            class="flex items-center space-x-1.5 rounded-xl bg-gold hover:bg-gold-hover text-[#060608] font-display text-xs font-bold px-3 py-1.5 shadow transition-colors cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            <span>Run Benchmark</span>
          </button>
        ) : (
          <button 
            onClick={resetSimulation} 
            class="flex items-center space-x-1.5 rounded-xl border border-border-custom hover:border-gold hover:text-gold text-text-main font-display text-xs font-semibold px-3 py-1.5 transition-colors cursor-pointer"
          >
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Simulator Side-by-Side Cards */}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 1. MTP CARD (explorer) */}
        <div class="flex flex-col rounded-2xl border border-border-custom bg-bg-secondary/40 p-5 relative overflow-hidden transition-all duration-300">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/10 border border-red-500/20 text-red-500">
                <Folder className="h-4 w-4" />
              </div>
              <span class="font-display text-sm font-bold text-text-main">Windows MTP</span>
            </div>
            <span class="font-body text-xs font-medium text-red-500 bg-red-500/10 px-2 py-0.5 rounded-md">
              Explorer Copy
            </span>
          </div>

          {/* Speed / Status */}
          <div class="flex flex-col mb-4">
            <span class="font-body text-2xl font-bold tracking-tight text-text-main">
              {mtpSpeed}
            </span>
            <span class="font-body text-xs text-text-muted mt-0.5">
              {mtpError ? 'Connection dropped' : status === 'running' ? 'Copying files...' : 'Idle'}
            </span>
          </div>

          {/* Progress bar */}
          <div class="w-full bg-border-custom h-2.5 rounded-full overflow-hidden mb-5">
            <motion.div 
              class="h-full bg-red-500/80 rounded-full" 
              animate={{ width: `${mtpProgress}%` }}
              transition={{ duration: 0.2 }}
            />
          </div>

          {/* Active worker thread mock (none for MTP) */}
          <div class="flex flex-col space-y-2 mt-auto">
            <span class="font-display text-xs font-bold text-text-muted">Thread Utilization:</span>
            <div class="flex h-10 w-full items-center justify-center rounded-xl bg-border-custom/30 border border-border-custom/50 text-[10px] font-body text-text-muted text-center px-4">
              Single-threaded sequential queue (Blocking)
            </div>
          </div>

          {/* Error Overlay pop-up */}
          <AnimatePresence>
            {mtpError && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                class="absolute inset-0 bg-[#060608]/90 flex flex-col items-center justify-center text-center p-6"
              >
                <XCircle className="h-10 w-10 text-red-500 mb-3" />
                <span class="font-display text-sm font-bold text-text-main mb-1">MTP Transfer Failed</span>
                <p class="font-body text-[11px] text-text-muted leading-relaxed max-w-[200px]">
                  "The device has either stopped responding or has been disconnected."
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 2. WARP TRANSFER CARD */}
        <div class="flex flex-col rounded-2xl border border-gold bg-bg-secondary/40 p-5 relative overflow-hidden transition-all duration-300 shadow-md shadow-gold-glow">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-gold/10 border border-gold/20 text-gold">
                <Cpu className="h-4 w-4" />
              </div>
              <span class="font-display text-sm font-bold text-text-main">Warp Transfer</span>
            </div>
            <span class="font-body text-xs font-medium text-gold bg-gold/10 px-2 py-0.5 rounded-md">
              Parallel Stream
            </span>
          </div>

          {/* Speed / Status */}
          <div class="flex flex-col mb-4">
            <span class="font-body text-2xl font-bold tracking-tight text-gold">
              {warpSpeed}
            </span>
            <span class="font-body text-xs text-text-muted mt-0.5">
              {status === 'done' ? 'Synced successfully' : status === 'running' ? 'Active parallel queue' : 'Ready'}
            </span>
          </div>

          {/* Progress bar */}
          <div class="w-full bg-border-custom h-2.5 rounded-full overflow-hidden mb-5">
            <motion.div 
              class="h-full bg-gold rounded-full" 
              animate={{ width: `${warpProgress}%` }}
              transition={{ duration: 0.2 }}
            />
          </div>

          {/* Parallel threads activity indicator */}
          <div class="flex flex-col space-y-2 mt-auto">
            <span class="font-display text-xs font-bold text-text-muted">Parallel ADB Worker Channels:</span>
            <div class="grid grid-cols-4 gap-2">
              {warpActiveWorkers.map((progress, idx) => (
                <div key={idx} class="h-10 rounded-xl bg-border-custom/30 border border-border-custom/50 flex flex-col justify-end p-1 overflow-hidden">
                  <motion.div 
                    class="w-full bg-gold/30 rounded-lg border-t border-gold" 
                    animate={{ height: `${progress}%` }}
                    transition={{ type: 'spring', stiffness: 100, damping: 15 }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Success Overlay pop-up */}
          <AnimatePresence>
            {status === 'done' && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                class="absolute inset-0 bg-[#060608]/90 flex flex-col items-center justify-center text-center p-6"
              >
                <CheckCircle className="h-10 w-10 text-gold mb-3 animate-bounce" />
                <span class="font-display text-sm font-bold text-text-main mb-1">Transfer Complete!</span>
                <p class="font-body text-[11px] text-text-muted leading-relaxed max-w-[200px]">
                  1,284 photos & files synced successfully in 4.8 seconds.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
