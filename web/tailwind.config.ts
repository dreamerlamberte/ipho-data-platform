import type { Config } from "tailwindcss";

// Colors are CSS variables (app/globals.css) so light/dark swap in one place.
const v = (name: string) => `var(--${name})`;

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        page: v("page"),
        surface: v("surface"),
        hover: v("hover"),
        ink: { DEFAULT: v("ink"), 2: v("ink-2"), muted: v("muted") },
        line: v("grid"),
        series: v("series-1"),
        good: v("good"),
        warning: v("warning"),
        serious: v("serious"),
        critical: v("critical"),
      },
      borderColor: { hair: v("border") },
      fontFamily: { sans: ["system-ui", "-apple-system", "Segoe UI", "sans-serif"] },
    },
  },
  plugins: [],
};
export default config;
