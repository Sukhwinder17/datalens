/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      // TODO: extend with the DataLens design system (brand colors,
      // font family, spacing scale) once visual design is decided.
    },
  },
  plugins: [],
};
