import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { GitFork, Star, AlertCircle, GitBranch } from 'lucide-react';

type Stats = { stars: number; forks: number; issues: number };

const GITHUB_REPO = "tahsanahmmed25/warp-transfer";

export default function GitHubStats() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}`);
        if (!res.ok) throw new Error("repository fetch failed");
        const repo = await res.json();

        if (!cancelled) {
          setStats({ 
            stars: repo.stargazers_count ?? 0, 
            forks: repo.forks_count ?? 0, 
            issues: repo.open_issues_count ?? 0 
          });
          setStatus("ready");
        }
      } catch (err) {
        if (!cancelled) setStatus("error");
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const cards = stats
    ? [
        { icon: Star, value: stats.stars, label: "GitHub Stars" },
        { icon: GitFork, value: stats.forks, label: "Forks" },
        { icon: AlertCircle, value: stats.issues, label: "Open Issues" },
      ]
    : [];

  return (
    <section class="py-20 lg:py-28 relative">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 reveal">
        
        {/* Section Header */}
        <div class="mx-auto max-w-2xl text-center mb-12">
          <div class="inline-flex items-center space-x-1.5 rounded-full border border-gold bg-gold-glow px-3 py-1 text-xs font-semibold text-gold tracking-wide mb-4">
            <span>Repository Metrics</span>
          </div>
          <h2 class="font-display text-3xl sm:text-4xl font-bold tracking-tight text-text-main">
            Live Repository Statistics
          </h2>
          <p class="font-body text-xs sm:text-sm text-text-muted mt-3 max-w-xl mx-auto">
            These numbers are not hardcoded. They represent active community engagement on this repository, fetched dynamically from GitHub's API on page load.
          </p>
        </div>

        {/* Stats Cards Display */}
        <div class="flex flex-col items-center gap-6">
          {status === 'loading' && (
            <div class="grid w-full max-w-2xl grid-cols-3 gap-4">
              {[0, 1, 2].map((i) => (
                <div key={i} class="h-28 rounded-2xl border border-border-custom bg-bg-secondary/20 animate-pulse" />
              ))}
            </div>
          )}

          {status === 'ready' && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="grid w-full max-w-2xl grid-cols-3 gap-4"
            >
              {cards.map((card) => {
                const Icon = card.icon;
                return (
                  <div key={card.label} class="rounded-2xl border border-border-custom bg-bg-secondary/40 px-3 py-6 text-center shadow-sm">
                    <Icon className="mx-auto text-gold h-5 w-5 mb-3" />
                    <div class="font-display text-2xl sm:text-3xl font-bold text-text-main leading-none">
                      {card.value}
                    </div>
                    <div class="font-body text-[10px] text-text-muted mt-2 uppercase tracking-wider font-semibold">
                      {card.label}
                    </div>
                  </div>
                );
              })}
            </motion.div>
          )}

          {status === 'error' && (
            <div class="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-center text-xs text-text-muted font-body">
              Unable to reach GitHub API. Visit the repository page directly instead.
            </div>
          )}

          {/* Action Link Button */}
          <a
            href="https://github.com/tahsanahmmed25/warp-transfer"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-4 inline-flex items-center space-x-2 rounded-full border border-border-custom hover:border-gold hover:text-gold text-text-main font-display text-xs font-semibold px-5 py-2.5 transition-all duration-300 hover:scale-[1.02] shadow-sm bg-bg-secondary/40"
          >
            <GitBranch className="h-4 w-4" />
            <span>View Repository</span>
          </a>
        </div>

      </div>
    </section>
  );
}
