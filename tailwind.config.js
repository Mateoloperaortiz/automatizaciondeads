/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./adflux/templates/**/*.html", // Scan all .html files in the templates folder
    "./adflux/static/js/**/*.js"    // Include Alpine.js files if you add classes there later
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 