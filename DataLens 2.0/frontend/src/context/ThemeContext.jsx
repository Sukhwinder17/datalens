import { createContext, useContext } from "react";

// TODO: implement real light/dark theme state + toggle + persistence.
const ThemeContext = createContext({ theme: "light", toggleTheme: () => {} });

export function useTheme() {
  return useContext(ThemeContext);
}

export default ThemeContext;
