/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#09090b', // Zinc 950
                surface: '#18181b',    // Zinc 900
                primary: '#8b5cf6',    // Violet 500
                secondary: '#10b981',  // Emerald 500
            }
        },
    },
    plugins: [],
}
