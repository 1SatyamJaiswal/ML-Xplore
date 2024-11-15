// app/layout.js
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body 
        className={`${inter.className} bg-white dark:bg-gray-900 min-h-screen flex flex-col`}
      >
        {/* Main Content Area */}
        <main className="flex-grow container mx-auto px-4 py-8">
          {children}
        </main>

        {/* Optional Footer */}
        <footer className="bg-gray-100 dark:bg-gray-800 py-4 text-center">
          <p className="text-gray-600 dark:text-gray-300">
            © {new Date().getFullYear()} Your Project Name
          </p>
        </footer>
      </body>
    </html>
  );
}