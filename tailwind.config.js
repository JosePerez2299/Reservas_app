module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.html",
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
  ],  
  daisyui: {
    themes: ["light", "dark"],
  },
  safelist: [
    // Le indicamos explícitamente a Tailwind que no purgue estas clases:
    "progress-primary",
    "progress-success",
    "progress-warning",
    "progress-error",
  ],
}
