/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111719",
        panel: "#182124",
        line: "#293438",
        muted: "#91a09e",
        mint: "#85e2bd",
        amber: "#e6ba72",
      },
      fontFamily: {
        sans: ["'DM Sans'", "sans-serif"],
        display: ["'Space Grotesk'", "sans-serif"],
      },
    },
  },
  plugins: [],
};