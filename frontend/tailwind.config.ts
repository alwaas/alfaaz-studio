import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        studio: {
          bg: "#080B10",
          surface: "#0D131F",
          card: "#121A2A",
          hover: "#1A253C",
          border: "#1E2A42",
          borderLight: "#2E3F63",
          gold: "#F59E0B",
          amber: "#D97706",
          emerald: "#10B981",
          cyan: "#06B6D4",
          rose: "#F43F5E",
          text: "#F1F5F9",
          muted: "#94A3B8",
        },
      },
      fontFamily: {
        nastaliq: [
          "var(--font-nastaliq)",
          "Jameel Noori Nastaleeq",
          "Noto Nastaliq Urdu",
          "Gulzar",
          "serif",
        ],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        studio: "0 8px 32px 0 rgba(0, 0, 0, 0.45)",
        gold: "0 0 20px -2px rgba(245, 158, 11, 0.25)",
        emerald: "0 0 20px -2px rgba(16, 185, 129, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;

