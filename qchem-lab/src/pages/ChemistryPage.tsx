import { ActiveSpaceExplorer } from "../components/chemistry/ActiveSpaceExplorer";
import { ChemistryPipelineRunner } from "../components/chemistry/ChemistryPipelineRunner";
import { ChemistryResultsDashboard } from "../components/chemistry/ChemistryResultsDashboard";
import { MoleculeCanvas } from "../components/chemistry/MoleculeCanvas";
import { MoleculeConfigurator } from "../components/chemistry/MoleculeConfigurator";
import { SimulationShell } from "../components/ui/SimulationShell";

interface ChemistryPageProps {
  darkMode: boolean;
  onBack?: () => void;
  onToggleTheme: () => void;
}

export function ChemistryPage({ darkMode, onBack, onToggleTheme }: ChemistryPageProps) {
  return (
    <SimulationShell
      title="Quantum Chemistry Lab"
      subtitle="Research console"
      left={<MoleculeConfigurator />}
      right={<ChemistryResultsDashboard />}
      darkMode={darkMode}
      onBack={onBack}
      onToggleTheme={onToggleTheme}
    >
      <ChemistryPipelineRunner />
      <MoleculeCanvas />
      <ActiveSpaceExplorer />
    </SimulationShell>
  );
}
