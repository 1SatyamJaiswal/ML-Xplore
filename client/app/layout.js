// app/layout.js
import { Inter } from "next/font/google";
import "react-toastify/dist/ReactToastify.css";
import "./globals.css";
import { ToastContainer } from "react-toastify";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body 
        className={`${inter.className} bg-white dark:bg-gray-900 min-h-screen flex flex-col`}
      >

        <ToastContainer />
        
        {/* Main Content Area */}
        <main className="flex-grow container mx-auto px-4 py-8">
          {children}
        </main>

        {/* Optional Footer */}
        <footer className="bg-gray-100 dark:bg-gray-800 py-4 text-center">
          <p className="text-gray-600 dark:text-gray-300">
            © 2024 ML - Explore
          </p>
        </footer>
      </body>
    </html>
  );
}