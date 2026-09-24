import { useEffect, useState } from "react";

import { ChemistryPage } from "./pages/ChemistryPage";

export default function App() {
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <ChemistryPage
      darkMode={darkMode}
      onToggleTheme={() => setDarkMode((current) => !current)}
    />
  );
}
