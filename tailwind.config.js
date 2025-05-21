/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./reservas/templates/**/*.html",
    "./static/**/*.js",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {},
  }
  ,
  plugins: [
    require("daisyui"),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('flowbite/plugin')
  ],
  daisyui: {
    themes: ["light", "dark"],
  }
}
