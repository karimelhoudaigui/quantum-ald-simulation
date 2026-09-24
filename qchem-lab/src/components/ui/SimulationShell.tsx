import { ArrowLeft, Moon, Sun } from "lucide-react";
import type { ReactNode } from "react";

import { IconButton } from "./IconButton";

interface SimulationShellProps {
  title: string;
  subtitle: string;
  left: ReactNode;
  right: ReactNode;
  children: ReactNode;
  darkMode: boolean;
  onBack?: () => void;
  onToggleTheme: () => void;
}

export function SimulationShell({
  title,
  subtitle,
  left,
  right,
  children,
  darkMode,
  onBack,
  onToggleTheme,
}: SimulationShellProps) {
  return (
    <div className="min-h-[100svh] bg-background text-foreground lg:h-[100svh] lg:overflow-hidden">
      <div className="grid min-h-0 min-w-0 grid-cols-1 lg:h-full lg:grid-cols-[minmax(280px,320px)_minmax(0,1fr)_minmax(340px,380px)]">
        {left}
        <main className="flex min-h-0 min-w-0 flex-col gap-5 overflow-y-auto overscroll-contain p-4 sm:p-5">
          <header className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-4">
              {onBack ? (
                <IconButton label="Back to simulations" onClick={onBack}>
                  <ArrowLeft size={18} />
                </IconButton>
              ) : null}
              {onBack ? (
                <button
                  type="button"
                  onClick={onBack}
                  className="min-w-0 rounded-md text-left transition hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-primary"
                  title="Back to simulations"
                >
                  <p className="text-xs font-medium uppercase text-foreground/50">{subtitle}</p>
                  <h1 className="truncate text-xl font-semibold sm:text-3xl">{title}</h1>
                </button>
              ) : (
                <div className="min-w-0">
                  <p className="text-xs font-medium uppercase text-foreground/50">{subtitle}</p>
                  <h1 className="truncate text-xl font-semibold sm:text-3xl">{title}</h1>
                </div>
              )}
            </div>
            <IconButton label="Toggle theme" onClick={onToggleTheme}>
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </IconButton>
          </header>
          {children}
        </main>
        {right}
      </div>
    </div>
  );
}
